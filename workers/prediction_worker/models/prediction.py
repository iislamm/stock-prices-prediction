from db import db


class Prediction(db.Model):
    symbol = db.Column(db.ForeignKey('stock.symbol'), primary_key=True)
    date = db.Column(db.DateTime(), primary_key=True)
    close = db.Column(db.Float, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'close': self.close,
            'date': self.date
        }
