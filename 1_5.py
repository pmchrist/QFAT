# 1.5

# Imports
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np

# Reading Data
pairs_price = pd.read_csv("Pairs_Price.csv")
pairs_ri = pd.read_csv("Pairs_RI.csv")
print(pairs_price.head())
#print(pairs_ri.head())

# Drop NaN's
pairs_price = pairs_price.dropna()


# 1_5

name_security_A = "VW"              # Pricier Asset
name_security_B = "VW_PREF"         # Cheaper Asset
df_spread_trade = pairs_price[[name_security_A, name_security_B]]

# Find Relative Spread
df_spread_trade["spread"] = (df_spread_trade[name_security_A] - df_spread_trade[name_security_B]) / df_spread_trade[name_security_B]
# Rolling 20-day, Spread Average and Volatility
window = 20
df_spread_trade["spread_rolling_mean"] = df_spread_trade["spread"].rolling(window).mean()
df_spread_trade["spread_rolling_std"] = df_spread_trade["spread"].rolling(window).std()
# Trading Based on Z-Score
df_spread_trade["spread_rolling_z_score"] = (df_spread_trade["spread"] - df_spread_trade["spread_rolling_mean"]) / df_spread_trade["spread_rolling_std"]

# Calculating Trades
df_spread_trade["Trade"] = np.zeros(len(df_spread_trade))
long_on_cheap = False
short_on_cheap = False
for i in range(window, len(df_spread_trade)):
    # Continue Trade if any
    if long_on_cheap:
        df_spread_trade["Trade"][i] = 1
    elif short_on_cheap:
        df_spread_trade["Trade"][i] = -1
    # Enter Trade
    if df_spread_trade["spread_rolling_z_score"][i-1] > 2 and not long_on_cheap:      # Go Long
        df_spread_trade["Trade"][i] = 1
        long_on_cheap = True
    elif df_spread_trade["spread_rolling_z_score"][i-1] < -2 and not short_on_cheap:   # Go Short
        df_spread_trade["Trade"][i] = -1
        short_on_cheap = True
    # Exit Trade
    if df_spread_trade["spread_rolling_z_score"][i-1] < 0 and long_on_cheap:      # Stop Long
        df_spread_trade["Trade"][i] = 0
        long_on_cheap = False
    elif df_spread_trade["spread_rolling_z_score"][i-1] > 0 and short_on_cheap:   # Stop Short
        df_spread_trade["Trade"][i] = 0
        short_on_cheap = False

# Find Returns
df_spread_trade["Returns"] = np.zeros(len(df_spread_trade))
for i in range(len(df_spread_trade)):
    if (df_spread_trade["Trade"][i] > 0):       # We are Short Expensive Security, Long Second
        df_spread_trade["Returns"][i] = (df_spread_trade[name_security_A][i-1] - df_spread_trade[name_security_A][i])/df_spread_trade[name_security_A][i] + (df_spread_trade[name_security_B][i] - df_spread_trade[name_security_B][i-1])/df_spread_trade[name_security_B][i-1]
    elif (df_spread_trade["Trade"][i] < 0):     # We are Long Expensive Security, Short Second
        df_spread_trade["Returns"][i] = (df_spread_trade[name_security_A][i] - df_spread_trade[name_security_A][i-1])/df_spread_trade[name_security_B][i-1] + (df_spread_trade[name_security_B][i-1] - df_spread_trade[name_security_B][i])/df_spread_trade[name_security_B][i]

# Sum Returns
returns_long = 0
returns_short = 0
for i in range(len(df_spread_trade)):
    if (df_spread_trade["Trade"][i] > 0): returns_long+=df_spread_trade["Returns"][i]
    elif (df_spread_trade["Trade"][i] < 0): returns_short+=df_spread_trade["Returns"][i]
print("Returns Long: ", returns_long)
print("Returns Short: ", returns_short)

df_spread_trade.to_csv("output.csv") 

