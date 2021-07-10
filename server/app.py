from sqlalchemy import desc
from controllers.price_scrapper import PricesScrapper
from controllers.news_scrapper import NewsScrapper
from config import Config
from db import init_db, db
from flask import Flask, jsonify
from flask_cors import CORS
from controllers.prediction import PredictionController
from flask_migrate import Migrate
from models.headline import Headline
from models.prediction import Prediction
from models.price import Price
from models.sentiment import Sentiment
from models.stock import Stock

app = Flask(__name__)

CORS(app)

app.config.from_object(Config())

init_db(app)

migrate = Migrate(app, db)


@app.route('/')
def handle_hello():
    return 'hello, world'


@app.route('/predict/<string:symbol>')
def handle_predict(symbol):
    prediction_worker = PredictionController(stock=symbol)
    predictions = prediction_worker.get_predictions()
    return jsonify({'predictions': predictions[0].tolist()})


@app.route('/scrape/prices')
def handle_prices_scrape():
    prices_scrapper = PricesScrapper(symbol='nflx')
    prices_scrapper.scrape_all()
    return jsonify({'success': True})


@app.route('/scrape/news')
def handle_news_scrape():
    news_scrapper = NewsScrapper()
    news_scrapper.scrape_all()
    return jsonify({'success': True})


@app.route('/prices/<string:symbol>')
def handle_prices(symbol):
    prices = Price.query.filter(Price.symbol == symbol.upper()).order_by(desc(Price.date)).limit(100).all()
    prices = [p.to_dict() for p in prices]

    return jsonify({'prices': prices})


if __name__ == '__main__':
    app.run(debug=True)
