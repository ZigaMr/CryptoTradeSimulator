# -*- coding: utf-8 -*-
"""
Created on Mon May 20 23:33:22 2019

@author: Ziga
"""
import requests
import json
import pandas as pd
import datetime as dt
from scipy import stats
import time
import logging
import numpy as np


logging.basicConfig(filename='Simulation_ETH2.log', level=logging.INFO)
print('Starting up...')
print(str(dt.datetime.utcnow()))
logging.info('Starting up...')
logging.info(str(dt.datetime.utcnow()))


def signal_slope(data, k = 0.1):
    #data.plot()
    #return stats.linregress(range(len(data)), data)[0]#, 
    return stats.linregress(range(len(data)), data)[0]/data[0]

def get_btc():
    data = requests.get(r'https://www.bitstamp.net/api/v2/transactions/btceur/')
    data = data.json()
    
    data = pd.DataFrame(data)
    data['date'] = data.date.apply(lambda x: dt.datetime.utcfromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))
    data.date = data.date.apply(pd.Timestamp)
    data.date = data.date.apply(lambda x: x.replace(second=0))
    data.price = data.price.apply(float)
    return data


def get_orderbook():
    data = requests.get(r'https://www.bitstamp.net/api/v2/order_book/etheur/')
    data = data.json()
    
    bids = pd.DataFrame()
    bids['quantity'] = [i[1] for i in data['bids']]
    bids['price'] = [i[0] for i in data['bids']]

    asks = pd.DataFrame()
    asks['price'] = [i[0] for i in data['asks']]
    asks['quantity'] = [i[1] for i in data['asks']]
    
    asks.price = asks.price.apply(float)
    asks.quantity = asks.quantity.apply(float)
    asks['q']= asks.price * asks.quantity

    bids.price = bids.price.apply(float)
    bids.quantity = bids.quantity.apply(float)
    bids['q'] = bids.price * bids.quantity
    return bids, asks
            
#signal = signal_slope(get_data().groupby('date').price.mean()[-3:])

 

portfolio = 1000
PnL = 0
last_VWAP = 0
open_position = True
t = dt.datetime.utcnow().minute%10

while True:

    if open_position:
        signal = signal_slope(get_btc().groupby('date').price.mean()[-10:])
        
        if dt.datetime.utcnow().minute%10 != t:

            t = dt.datetime.utcnow().minute%10
            print(t)
            print(signal)
            
        if signal > 0.005:
            
            logging.info(str(dt.datetime.utcnow()))
            logging.info('Opening position')
            logging.info('Signal at: ' + str(signal))
            
            print(str(dt.datetime.utcnow()))
            print('Opening position')
            print('Signal at: ' + str(signal))
            
            bids, asks = get_orderbook()
            last_VWAP = asks[asks.q.cumsum() <= portfolio]
            last_VWAP = asks[:len(last_VWAP)+1]
            quantity = last_VWAP.quantity.sum() - (last_VWAP.q.sum() - portfolio)/last_VWAP.price.iloc[-1]
            logging.info('Bought ' + str(quantity) + ' ETH for ' + str(portfolio) + '€')
            open_position = False
            
    else:
        bids, asks = get_orderbook()
        last_VWAP = bids[bids.q.cumsum() <= portfolio]
        last_VWAP = bids[:len(last_VWAP)+1]
        last_VWAP.quantity.iloc[-1] -= last_VWAP.quantity.sum() - quantity
        x = np.sum(last_VWAP.quantity*last_VWAP.price)
        
        if dt.datetime.utcnow().minute%10 != t:

            logging.info(str(dt.datetime.utcnow()))
            logging.info('Unrealized Position:')
            logging.info(str(x))
            t = dt.datetime.utcnow().minute%10
            print(t)
            print(x)
        
        if x/portfolio > 1.01:
            
            logging.info(str(dt.datetime.utcnow()))
            logging.info('Closing position at profit: ')
            logging.info('New portfolio: ' + str(x))
            print(str(dt.datetime.utcnow()))
            print('Closing position at profit: ')
            print('New portfolio: ' + str(x))
            
            portfolio = x
            open_position = True
        elif x/portfolio < 0.97:
            
            logging.info(str(dt.datetime.utcnow()))
            logging.info('Closing position at profit: ')
            logging.info('New portfolio: ' + str(x))
            print(str(dt.datetime.utcnow()))
            print('Closing position at loss: ')
            print('New portfolio: ' + str(x))
            
            portfolio = x    
            open_position = True
    
    time.sleep(10)
        

        
        

#data_eth = pd.DataFrame(data_eth)
#data_eth['date'] = data_eth.date.apply(lambda x: dt.datetime.utcfromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))
#data_eth.date = data_eth.date.apply(pd.Timestamp)
#
#data_eth.price = data_eth.price.apply(float)
#data_eth.groupby('date').price.mean().pct_change().shift(-1).plot()