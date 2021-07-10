import re
from io import StringIO
from datetime import datetime, timedelta
import requests
import pandas as pd
from sqlalchemy.sql.expression import desc
from models.price import Price
from models.stock import Stock


class PricesScrapper:
    timeout = 10
    crumb_link = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
    crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
    quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/{quote}?period1={dfrom}&period2={dto}&interval=1d&events=history&crumb={crumb}'

    def __init__(self, symbol=None, days_back=7):
        if symbol is not None:
            self.symbol = symbol.upper()
        self.session = requests.Session()
        self.dt = timedelta(days=days_back)

    def get_crumb(self):
        print(self.crumb_link.format(self.symbol))
        response = self.session.get(self.crumb_link.format(self.symbol), timeout=self.timeout, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        response.raise_for_status()
        match = re.search(self.crumble_regex, response.text)
        if not match:
            raise ValueError('Could not get crumb from Yahoo Finance')
        else:
            self.crumb = match.group(1)

    def get_quote(self):
        if not hasattr(self, 'crumb') or len(self.session.cookies) == 0:
            self.get_crumb()
        now = datetime.utcnow()
        dateto = int(now.timestamp())
        datefrom = int((now - self.dt).timestamp())
        url = self.quote_link.format(
            quote=self.symbol, dfrom=datefrom, dto=dateto, crumb=self.crumb)
        response = self.session.get(url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text), parse_dates=['Date'])

    def get_prices(self):
        df = self.get_quote()
        latest_scrapped_prices = df.sort_values(
            by='Date', axis=0, ascending=False)

        last_db_prices = Price.query.filter(Price.symbol == self.symbol)\
            .filter(Price.date >= latest_scrapped_prices.iloc[0]['Date']).order_by(desc(Price.date)).all()
        last_db_prices = [p.to_dict() for p in last_db_prices]

        # print(last_db_prices)

        if len(last_db_prices) == 0:
            print('new prices')
            last_db_price = Price.query.filter(
                Price.symbol == self.symbol).order_by(desc(Price.date)).first()
            last_db_price = last_db_price.to_dict()
            latest_scrapped_prices = pd.DataFrame(latest_scrapped_prices)
            if last_db_price is not None:
                latest_scrapped_prices = latest_scrapped_prices[
                    latest_scrapped_prices['Date'] >= last_db_price['date']]

            latest_scrapped_prices.sort_values(
                by='Date', ascending=True, axis=0, inplace=True)
            latest_scrapped_prices['change'] = latest_scrapped_prices['Close'].pct_change(
            )

            latest_scrapped_prices = latest_scrapped_prices[
                latest_scrapped_prices['Date'] > last_db_price['date']]

            latest_scrapped_prices.apply(lambda p: Price(symbol=self.symbol,
                                                         date=p['Date'], close=p['Close'], change=p['change'], volume=p['Volume']).insert(), axis=1)
        else:
            print('no new prices')

    def scrape_all(self):
        all_stocks = Stock.query.all()
        all_stocks = [s.to_dict()['symbol'] for s in all_stocks]
        for s in all_stocks:
            self.symbol = s.upper()
            self.get_prices()
