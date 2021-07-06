from db import db


class Stock(db.Model):
    symbol = db.Column(db.String(), primary_key=True)
    company_name = db.Column(db.String(), nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    prices = db.relationship('Price', backref='stock')
    sentiments = db.relationship('Sentiment', backref='stock')
    headlines = db.relationship('Headline', backref='stock')

    def insert(self):
        db.session.add()
        db.session.commit()

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'company_name': self.company_name,
            'current_price': self.current_price
        }
