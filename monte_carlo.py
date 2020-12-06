import pandas as pd
import numpy as np
import datetime as dt
from TDRestAPI import Rest_Account
import math
from random import random
from scipy.stats import norm
import matplotlib.pyplot as plt

account = Rest_Account('keys.json')

data = account.history('SPY', 1, 600, frequency_type="daily", period_type='year')
open_prices = data['open'].tolist()
periodic_daily_returns = []
for index, open_price in enumerate(open_prices):
    if index > 0:
        current = open_price
        last = open_prices[index-1]
        periodic_daily_return = math.log((current/last))
        periodic_daily_returns.append(periodic_daily_return)

average_return = sum(periodic_daily_returns)/len(periodic_daily_returns)
squared_differences = [(daily_return-average_return)**2 for daily_return in periodic_daily_returns]
vairance = sum(squared_differences)/len(squared_differences)
standard_deviation = math.sqrt(vairance)
drift = average_return - (vairance/2)


random_var = standard_deviation * norm.ppf(random(), loc=average_return, scale=standard_deviation)
print(random_var)



current = open_prices[-1]
forecasts = []

for trials in range(400):
    forecast = []
    current = open_prices[-1]
    for val in range(100):
        random_var = standard_deviation * norm.ppf(random(), loc=average_return, scale=standard_deviation)
        next_days = current * (math.e**(drift+random_var))
        forecast.append(next_days)
        current = next_days
    forecasts.append(forecast)
    print('Done')

# a = np.array(forecasts)
# a = a.mean(axis=0)
# plt.plot(a)
# plt.show()
for cast in forecasts:
    plt.plot(cast)
plt.show()