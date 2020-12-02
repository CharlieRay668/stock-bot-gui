import datetime as dt
import matplotlib.pyplot as plt
import pickle
import os
from os import path
import pandas as pd

DIRECTORY = 'watchlists'
COLUMNS = ['SYMBOL', 'DIRECTION', 'THRESHOLD', 'PT', 'AUTHOR', 'UPLOADED', 'ALERTED', 'CHANNEL']

class Watch:
    def __init__(self, symbol, direction, threshold, pt, author, uploaded, alerted, channel):
        self.symbol = symbol
        self.direction = direction
        self.threshold = float(threshold)
        self.pt = float(pt)
        self.author = author
        self.uploaded = uploaded
        self.alerted = alerted
        self.channel = channel
        self.save_self()

    def __str__(self):
        return self.author + ' ' + self.symbol + ' ' + self.direction + ' ' + str(self.threshold) + ' Profit Target: ' + str(self.pt)

    def save_self(self):
        today = dt.date.today().strftime("%Y_%m_%d")
        csv_path = DIRECTORY+'/'+today+'_watchlist.csv'
        if path.exists(csv_path):
            data = pd.read_csv(csv_path, index_col=0)
            new_df = pd.DataFrame(data=[[self.symbol, self.direction, self.threshold, self.pt, self.author, self.uploaded, self.alerted, self.channel]], columns=COLUMNS)
            data = data.append(new_df, ignore_index = True)
            data.to_csv(csv_path)
        else:
            data = pd.DataFrame(data=[[self.symbol, self.direction, self.threshold, self.pt, self.author, self.uploaded, self.alerted, self.channel]], columns=COLUMNS)
            data.to_csv(csv_path)


# class Watch:
#     def __init__(self, symbol, direction, threshold, pt1, pt2= None, pt3 = None, sl='%50', buyprice = None, sellprice = None):
#         self.buyprice = buyprice
#         self.sellprice = sellprice
#         self.symbol = symbol.upper()
#         self.direction = direction
#         self.threshold = float(threshold)
#         self.pt1 = float(pt1)
#         self.initialized = False
#         self.exit_con = None
#         self.sl = None
#         if '%' in sl:
#             self.sl = float(sl[1:])
#             self.exit_con = None
#         else: 
#             self.exit_con = float(sl)
#             self.sl = None

#     def __str__(self):
#         string =  self.symbol + ' ' + self.direction + ' ' + str(self.threshold) + ' ' + str(self.pt1) + ' %'+ str(self.sl) + ' sl '
#         if self.exit_con != None:
#             string += str(self.exit_con) 
#         if self.buyprice != None:
#             string += ' Bought at ' + str(self.buyprice)
#         if self.sellprice != None:
#             string +=  ' Sold at ' + str(self.sellprice)
#         string += '\n'
#         return string
#     def get_symbol(self):
#         return self.symbol

#     def get_threshold(self):
#         return self.threshold
    
#     def get_direction(self):
#         return self.direction

#     def get_pt1(self):
#         return self.pt1

#     def set_symbol(self, symbol):
#         self.symbol = symbol

#     def get_buyprice(self):
#         return self.buyprice

#     def set_buyprice(self, buyprice):
#         self.buyprice = buyprice
    
#     def set_sellprice(self, sellprice):
#         self.sellprice = sellprice

#     def get_sl(self):
#         return self.sl

#     def get_exit_con(self):
#         return self.exit_con