import numpy as np
from models.sentiment import Sentiment
import tensorflow as tf
import pandas as pd
import joblib
import re
from models.price import Price
from sqlalchemy import desc


joblib.clip = False


class PredictionWorker:
    def __init__(self, stock='NFLX'):
        self.scalers = self.load_scalers()
        self.df = None
        self.stock = stock

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
        def dateparse(dates): return pd.to_datetime(dates, format='%Y-%m-%d')
        # self.df = pd.read_csv('../../datasets/nflx_prices.csv',
        #                       index_col='Date', parse_dates=['Date'], date_parser=dateparse)

        # self.df.drop(columns=['Open', 'High', 'Low'], inplace=True)
        # self.df = self.df.rename(
        #     columns={'Close': 'close', 'Volume': 'volume'})
        # self.df = self.df.drop(columns=['Adj Close'])

        # self.df['change'] = self.df['close'].pct_change()
        # self.df.dropna(inplace=True)

        # news_df = pd.read_csv('../../datasets/analyzed_news.csv',
        #                       index_col=0, parse_dates=['date'], date_parser=dateparse)
        # news_df = news_df.where(news_df['stock'] == 'NFLX').dropna()
        # news_df['sentiment'] = news_df['sentiment'].apply(
        #     lambda x: float(re.findall('\d+\.\d+', x)[0]))
        # grouped_df = pd.DataFrame(news_df.groupby(['date']).mean())

        # self.df = self.df.join(grouped_df)
        # self.df['sentiment'].fillna(-1, inplace=True)

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

    def get_predictions(self):
        scaler = self.scalers['close']
        ds = self.prepare_prediction_data()

        prediction = self.model.predict(ds)
        prediction = scaler.inverse_transform(prediction)

        # TODO: Save the prediction to the database
        return prediction


if __name__ == 'main':
    prediction_worker = PredictionWorker()
    prediction_worker.df.head()

    prediction_worker.get_predictions()
