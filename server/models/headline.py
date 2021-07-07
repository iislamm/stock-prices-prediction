from db import db


class Headline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.ForeignKey('stock.symbol'))
    headline = db.Column(db.String(), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("symbol", "headline"),
    )

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'headline': self.headline,
            'date': self.date
        }
