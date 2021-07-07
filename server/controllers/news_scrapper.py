import os
from controllers.prediction import PredictionController
from models.sentiment import Sentiment
import requests
from bs4 import BeautifulSoup
import pandas as pd
from models.headline import Headline
from models.stock import Stock
from sqlalchemy.exc import IntegrityError
from db import db
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
from official.nlp import optimization
import numpy as np


class NewsScrapper:
    def __init__(self):
        self.url = 'https://news.google.com/search?q={}%20when%3A1d&hl=en-US&gl=US&ceid=US%3Aen'
        model_dir = '/environment/models/bert'
        if not os.path.isdir(model_dir):
            print('downloading sentiment analysis model')
            PredictionController.download_folder_from_s3('models/bert')

        self.model = tf.keras.models.load_model(model_dir, compile=False)

    def get_news(self, symbol):
        url = self.url.format(symbol)
        res = requests.get(url)
        if res.status_code == 200:
            html = res.content
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('article')
            all_headlines = []
            for a in articles:
                try:
                    headline_text = a.h3.a.text
                    date = pd.to_datetime(pd.to_datetime(
                        a.time.attrs['datetime']).date())
                    headline = Headline(
                        symbol=symbol, headline=headline_text, date=date)
                    headline.insert()
                    all_headlines.append(headline.to_dict())
                except AttributeError as e:
                    print(e)
                except IntegrityError:
                    db.session.rollback()
                    print('duplicate headline')
            self.analyzeSentiment(all_headlines)

    def scrape_all(self):
        all_stocks = Stock.query.all()
        all_stocks = [s.to_dict()['symbol'] for s in all_stocks]

        for s in all_stocks:
            self.get_news(s)

    def analyzeSentiment(self, headlines):
        if len(headlines) > 0:
            df = pd.DataFrame(headlines)

            predictions = tf.sigmoid(self.model.predict(df['headline']))
            predictions = np.array(predictions).flatten()

            df['sentiment'] = predictions
            df = pd.DataFrame(df.groupby(['date', 'symbol']).mean())
            df.reset_index(inplace=True)
            print(df.head())
            try:
                df.apply(lambda s: Sentiment(
                    symbol=s['symbol'], date=s['date'], sentiment=s['sentiment']).insert(), axis=1)
            except IntegrityError:
                print('duplicate day for sentiment')
                db.session.rollback()
            except Exception as e:
                print("ERROR: ", e)
        else:
            print('no headlines to analyze')
