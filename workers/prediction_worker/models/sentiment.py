from db import db


class Sentiment(db.Model):
    symbol = db.Column(db.ForeignKey('stock.symbol'), primary_key=True)
    date = db.Column(db.DateTime(), primary_key=True)
    sentiment = db.Column(db.Float, nullable=False)

    def insert(self):
        db.session.add()
        db.session.commit()

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'sentiment': self.sentiment,
            'date': self.date
        }
