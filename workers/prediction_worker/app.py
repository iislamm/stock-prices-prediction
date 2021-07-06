from config import Config
from db import init_db, db
from flask import Flask, jsonify
from prediction_worker import PredictionWorker
from flask_migrate import Migrate
from models.headline import Headline
from models.prediction import Prediction
from models.price import Price
from models.sentiment import Sentiment
from models.stock import Stock

app = Flask(__name__)

app.config.from_object(Config())

init_db(app)

migrate = Migrate(app, db)


@app.route('/predict')
def handle_predict():
    prediction_worker = PredictionWorker()
    predictions = prediction_worker.get_predictions()
    return jsonify({'predictions': predictions[0].tolist()})


if __name__ == '__main__':
    app.run(debug=True)
