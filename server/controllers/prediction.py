import datetime

from sqlalchemy.sql.expression import all_
from models.prediction import Prediction
from models.sentiment import Sentiment
from models.stock import Stock
import tensorflow as tf
import pandas as pd
import joblib
from models.price import Price
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from db import db
import os
import boto3
import shutil


joblib.clip = False


class PredictionController:
    def __init__(self, stock='NFLX'):
        self.scalers = self.load_scalers()
        self.df = None
        self.stock = stock.upper()

        # self.model = tf.keras.models.load_model(
        #     '/environment/models/time_series/gru')

        self.load_model()

        self.get_stock_data()

    def download_folder_from_s3(prefix):
        region_name = os.environ.get('AWS_REGION_NAME')
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        s3_resource = boto3.resource('s3', region_name=region_name,
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key)
        bucket = s3_resource.Bucket('stocks-prediction')
        for obj in bucket.objects.filter(Prefix=prefix):
            print(obj.key)
            target_dir = '/environment/' + obj.key
            if not os.path.exists(os.path.dirname(target_dir)):
                os.makedirs(os.path.dirname(target_dir))
            if obj.key[-1] == '/':
                continue
            print('object', obj.key)
            print('target', target_dir)
            bucket.download_file(obj.key, target_dir)

    def load_model(self):
        model_dir = '/environment/models/time_series'
        # shutil.rmtree(model_dir)
        if os.path.isdir(model_dir):
            print('model downloaded')
        else:
            print('downloading model')
            PredictionController.download_folder_from_s3('models/time_series')

        self.model = tf.keras.models.load_model(
            '/environment/models/time_series/')

    def load_scalers(self):
        scalers = {}

        if not os.path.isdir('/environment/scalers'):
            print('downloading scalers')
            PredictionController.download_folder_from_s3('scalers')

        scalers['close'] = joblib.load('/environment/scalers/close_scaler.pkl')
        scalers['volume'] = joblib.load(
            '/environment/scalers/volume_scaler.pkl')
        scalers['change'] = joblib.load(
            '/environment/scalers/change_scaler.pkl')
        return scalers

    def scale_data(self):
        scalers = self.load_scalers()
        self.df['close'] = scalers['close'].transform(
            self.df['close'].values.reshape(-1, 1))
        self.df['volume'] = scalers['volume'].transform(
            self.df['volume'].values.reshape(-1, 1))
        self.df['change'] = scalers['change'].transform(
            self.df['change'].values.reshape(-1, 1))

    def get_stock_data(self):
        prices = Price.query.filter(
            Price.symbol == self.stock.upper()).order_by(desc(Price.date)).all()
        prices = [p.to_dict() for p in prices]

        self.df = pd.DataFrame(prices)

        self.df.set_index('date', inplace=True)
        self.df.drop(columns=['symbol'], inplace=True)

        sentiments = Sentiment.query.filter(
            Sentiment.symbol == self.stock).order_by(desc(Sentiment.date)).all()
        sentiments = [s.to_dict() for s in sentiments]

        sentiments_df = pd.DataFrame(sentiments)
        sentiments_df.set_index('date', inplace=True)

        sentiments_df.drop(columns=['symbol'], inplace=True)

        self.df = self.df.join(sentiments_df)

        self.df['sentiment'].fillna(-1, inplace=True)

        self.df.sort_index(ascending=True, inplace=True)

        print(self.df.head())
        print(self.df.shape)

        self.scale_data()

    def prepare_prediction_data(self, start=0):
        print('shape', self.df[start:].shape)
        ds = tf.data.Dataset.from_tensor_slices(self.df[start:])
        ds = ds.window(20, shift=1, drop_remainder=True)
        ds = ds.flat_map(lambda w: w.batch(20))
        ds = ds.batch(32).prefetch(1)
        return ds

    def save_predictions(self, predictions, start=0):
        trading_days = self.df[start:].index.to_list()
        start_date = self.df[start:].index.min() 
        max_date = self.df[start:].index.max()
        for i in range(20):
            start_date = start_date + datetime.timedelta(days=1)
            while(start_date not in trading_days and start_date < max_date):
                start_date = start_date + datetime.timedelta(days=1)

            if start_date.weekday() > 4:
                start_date = start_date + \
                    datetime.timedelta(days=7 - start_date.weekday())
        
        prediction_records = []
        predictions = predictions[:, 0] ## TODO Update if you want bulk predictionss
        print('updated predictions shape', predictions.shape)
        print('min date', self.df[start:].index.min())
        print('max date', max_date)
        print('start_date', start_date)
        for p in predictions: ## TODO Update if you want bulk predictions
            start_date = start_date + datetime.timedelta(days=1
            )
            while(start_date not in trading_days and start_date < max_date):
                start_date = start_date + datetime.timedelta(days=1)

            if start_date.weekday() > 4:
                start_date = start_date + \
                    datetime.timedelta(days=7 - start_date.weekday())
            try:
                new_prediction = Prediction(
                    symbol=self.stock, date=start_date, close=float(p))
                prediction_records.append(new_prediction)
                new_prediction.insert()
            except IntegrityError:
                db.session.rollback()
                print('prediction already saved in database')
        prediction_records = [p.to_dict() for p in prediction_records]
        return prediction_records

    def generate_predictions(self):
        scaler = self.scalers['close']
        ds = self.prepare_prediction_data()

        prediction = self.model.predict(ds)
        prediction = scaler.inverse_transform(prediction)

        print('predictions_shape', prediction.shape)

        prediction_records = self.save_predictions(prediction)

        return prediction_records

    def predict_all(self):
        all_stocks = Stock.query.all()
        all_stocks = [s.to_dict() for s in all_stocks]

        for s in all_stocks:
            try:
                self.stock = s['symbol']
                self.get_stock_data()
                self.generate_predictions()
            except Exception as e:
                print('error occuerd with', s)
                print(e)
