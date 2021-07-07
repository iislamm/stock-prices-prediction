from db import db


class Price(db.Model):
    symbol = db.Column(db.ForeignKey('stock.symbol'), primary_key=True)
    date = db.Column(db.DateTime(), primary_key=True)
    close = db.Column(db.Float, nullable=True)
    change = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Float, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("symbol", "date"),
    )

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'close': self.close,
            'volume': self.volume,
            'change': self.change,
            'date': self.date
        }
