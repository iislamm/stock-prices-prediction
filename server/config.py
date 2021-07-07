import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI', 'postgresql://islam:123123@localhost:5432/stocks')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
