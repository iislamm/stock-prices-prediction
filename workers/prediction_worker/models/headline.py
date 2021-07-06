from db import db


class Headline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.ForeignKey('stock.symbol'))
    headline = db.Column(db.String(), nullable=False)
    date = db.Column(db.DateTime(), nullable=False, unique=True)

    def insert(self):
        db.session.add()
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'headline': self.headline,
            'date': self.date
        }
