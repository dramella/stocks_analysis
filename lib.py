#libraries
import requests
import plotly.express as px
import plotly.graph_objects as go
import os
import ssl
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
ssl._create_default_https_context = ssl._create_unverified_context

###getting historical data by ticker
def yf_historical_data(ticker,end_date=None, start_date=None,freq='Daily'):
    """

    :param ticker: stock ticker or list of stock tickers
    :param end_date: last date of data
    :param start_date: first date of data. If start date is not available, then first available date is retrieved
    :param freq: frequency of quotes either daily weekly or monthly
    :return:
    """
    #todo add currency
    #set default end date to today
    if end_date==None:
        end_date = datetime.utcnow()
    else:
        end_date = datetime.strptime(end_date, '%d/%m/%Y')
    #set default start date to prior 30 days
    if start_date==None:
        start_date = datetime(1000, 1, 1, 0, 0)
    else:
        start_date = datetime.strptime(start_date, '%d/%m/%Y')

    def yf_scraping_link(ticker,end_date,start_date,freq):
        #transform end- and startdate in int
        end=int(end_date.timestamp())
        start=int(start_date.timestamp())
        #check date consistency
        if end<start:
            raise Exception("End date must be after the start date!")
        if end_date> datetime.utcnow() or start_date> datetime.utcnow():
            raise Exception("Start/End dates cannot be future dates!")
        #transform frequency in yf interval type
        freq_dict = {'daily': '1d', 'weekly': '1w', 'monthly': '1m'}
        f = freq_dict[freq.lower()]
        #request url and check status
        yf_link = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker.upper()}?period1={start}&period2={end}&interval={f}&events=history"
        r=requests.get(yf_link)
        r.raise_for_status()
        #scrape df
        df = pd.read_csv(yf_link,parse_dates=True)
        df["Ticker"]=ticker
        df["Date"]=pd.to_datetime(df["Date"])
        #check if requested startdate is available
        first_date=df['Date'].iloc[0]
        if first_date>start_date:
            print(f"Time series starts on {first_date.strftime('%d/%m/%Y')}")
        return df

    if isinstance(ticker,list):
        df_list=[]
        for t in ticker:
            df=yf_scraping_link(ticker=t,end_date=end_date,start_date=start_date,freq=freq)
            df_list.append(df)
        df=pd.concat(df_list)
    else:
        df=yf_scraping_link(ticker=ticker,end_date=end_date,start_date=start_date,freq=freq)
    df.set_index(["Ticker", "Date"],inplace=True)

    return df

### plot interactive line graph
def df_line_graph(df,y):
    if isinstance(df.index, pd.MultiIndex):
        df.reset_index(inplace=True)
    df_interpolated = df.interpolate(method='linear', order=2)
    fig = px.line(df_interpolated, x='Date', y=f'{y}', color="Ticker",title=f'Closing Price Historical Chart')
    fig.update_xaxes(rangeslider_visible=True,rangeselector=dict(buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])))
    return fig



### recap on company
def summary_info(ticker):
    url_profile=f"https://finance.yahoo.com/quote/{ticker.upper()}/profile?p={ticker.upper()}"
    r = requests.get(url_profile)
    if r.status_code==200:
        soup = BeautifulSoup(r.text, 'html.parser')
        company_name=(soup.find_all("h3", class_="Fz(m) Mb(10px)")[0]).text
        sector=soup.find_all("span", class_="Fw(600)")[0].text
        industry=(soup.find_all("span", class_="Fw(600)")[1]).text
        keys_list=["Name","Sector","Industry"]
        values_list=[company_name,sector,industry]
        df= pd.DataFrame(list(zip(keys_list, values_list))).T
        df = pd.DataFrame(df.values[1:], columns=df.iloc[0])
        return df
    else:
        print('N/A')


def overview(ticker):
    df=yf_historical_data(ticker)
    df.reset_index(inplace=True)
    df_last_date_row=df.loc[df.Date == df.Date.max()]
    keys_list = ["Date","Close", "Adjusted Close","Open","High","Low","Volume"]
    date_day=df_last_date_row['Date'].to_string(index=False)
    close=df_last_date_row['Close'].to_string(index=False)
    adj_close=df_last_date_row['Adj Close'].to_string(index=False)
    open=df_last_date_row['Open'].to_string(index=False)
    high=df_last_date_row['High'].to_string(index=False)
    low=df_last_date_row['Low'].to_string(index=False)
    volume=df_last_date_row['Volume'].to_string(index=False)
    values_list=[date_day,close,adj_close,open,high,low,volume]
    overview_df = pd.DataFrame(list(zip(keys_list, values_list)))
    overview_df = overview_df.rename(columns={0: "stats", 1: ""})
    overview_df.set_index('stats',drop=True, inplace=True)
    overview_df.index.name=None
    return overview_df


def candlestick(ticker):
    df = yf_historical_data(ticker)
    df.reset_index(inplace=True)
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    fig.update_layout(title='Candlestick Chart')
    return fig


def ticker_returns(ticker):
    df = yf_historical_data(ticker)
    df.reset_index(inplace=True)
    df=df[['Date','Close']]
    df['daily_rets']=df['Close'].pct_change()
    df.dropna(inplace=True)
    df['cumulative_daily_rets']=(1 + df['daily_rets']).cumprod()
