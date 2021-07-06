import datetime
from models.prediction import Prediction
from models.sentiment import Sentiment
import tensorflow as tf
import pandas as pd
import joblib
from models.price import Price
from sqlalchemy import desc


joblib.clip = False


class PredictionWorker:
    def __init__(self, stock='NFLX'):
        self.scalers = self.load_scalers()
        self.df = None
        self.stock = stock.upper()

        self.model = tf.keras.models.load_model('../../models/time_series/gru')

        self.get_stock_data()

    def load_scalers(self):
        scalers = {}
        scalers['close'] = joblib.load('../../scalers/close_scaler.pkl')
        scalers['volume'] = joblib.load('../../scalers/volume_scaler.pkl')
        scalers['change'] = joblib.load('../../scalers/change_scaler.pkl')
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
            Price.symbol == self.stock.upper()).order_by(desc(Price.date)).limit(20).all()
        prices = [p.to_dict() for p in prices]

        self.df = pd.DataFrame(prices)

        self.df.set_index('date', inplace=True)
        self.df.drop(columns=['symbol'], inplace=True)

        sentiments = Sentiment.query.filter(
            Sentiment.symbol == self.stock).order_by(desc(Sentiment.date)).limit(20).all()
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

    def prepare_prediction_data(self):
        ds = tf.data.Dataset.from_tensor_slices(self.df[-20:])
        ds = ds.window(20, shift=1, drop_remainder=True)
        ds = ds.flat_map(lambda w: w.batch(20))
        ds = ds.batch(32).prefetch(1)
        return ds

    def save_predictions(self, predictions):
        start_date = self.df.index.max() + datetime.timedelta(days=1)

        for p in predictions[0]:
            start_date = start_date + datetime.timedelta(days=1)
            if start_date.weekday() > 4:
                start_date = start_date + \
                    datetime.timedelta(days=7 - start_date.weekday())

            new_prediction = Prediction(
                symbol=self.stock, date=start_date, close=float(p))
            new_prediction.insert()

    def get_predictions(self):
        scaler = self.scalers['close']
        ds = self.prepare_prediction_data()

        prediction = self.model.predict(ds)
        prediction = scaler.inverse_transform(prediction)

        self.save_predictions(prediction)

        return prediction


if __name__ == 'main':
    prediction_worker = PredictionWorker()
    prediction_worker.df.head()

    prediction_worker.get_predictions()
