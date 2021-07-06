import pandas as pd
import re


def dateparse(dates): return pd.to_datetime(dates, format='%Y-%m-%d')


def update_news():
    news_df = pd.read_csv('../../datasets/analyzed_news.csv',
                          index_col=0, parse_dates=['date'], date_parser=dateparse)
    news_df = news_df.dropna()
    news_df['sentiment'] = news_df['sentiment'].apply(
        lambda x: float(re.findall('\d+\.\d+', x)[0]))
    grouped_df = pd.DataFrame(news_df.groupby(['date', 'stock']).mean())
    grouped_df.to_csv('../../datasets/analyzed_news.csv')


def update():
    prices_df = pd.read_csv('../../datasets/nvda_prices.csv',
                            index_col='Date', parse_dates=['Date'], date_parser=dateparse)

    prices_df.drop(columns=['Open', 'High', 'Low'], inplace=True)
    prices_df = prices_df.rename(
        columns={'Close': 'close', 'Volume': 'volume'})
    prices_df = prices_df.drop(columns=['Adj Close'])

    prices_df['change'] = prices_df['close'].pct_change()
    prices_df.dropna(inplace=True)

    prices_df['symbol'] = 'NVDA'

    print(prices_df.head())

    prices_df.to_csv('../../datasets/nvda_prices.csv')


if __name__ == '__main__':
    update_news()
