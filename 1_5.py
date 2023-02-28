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
print(pairs_ri.head())


# 1_5

df_spread_trade = pd.DataFrame()
name_security_A = "VW"              # Pricier Asset
name_security_B = "VW_PREF"         # Cheaper Asset
# Find Relative Spread
df_spread_trade["spread"] = (pairs_price[name_security_A] - pairs_price[name_security_B]) / pairs_price[name_security_B]
# Rolling 20-day, Spread Average and Volatility
window = 20
df_spread_trade["spread_rolling_mean"] = df_spread_trade["spread"].rolling(window).mean()
df_spread_trade["spread_rolling_std"] = df_spread_trade["spread"].rolling(window).std()
# Trading Based on Z-Score
df_spread_trade["spread_rolling_z_score"] = (df_spread_trade["spread"] - df_spread_trade["spread_rolling_mean"]) / df_spread_trade["spread_rolling_std"]

# Calculating Trades
df_spread_trade["Trade"] = np.zeros(len(df_spread_trade))
in_long = False
in_short = False
for i in range(window, len(pairs_price)):
    # Continue Trade if any
    if in_long:
        df_spread_trade["Trade"][i] = 1
    elif in_short:
        df_spread_trade["Trade"][i] = -1
    # Enter Trade
    if df_spread_trade["spread_rolling_z_score"][i-1] > 2 and not in_long:      # Go Long
        df_spread_trade["Trade"][i] = 1
        in_long = True
    elif df_spread_trade["spread_rolling_z_score"][i-1] < -2 and not in_short:   # Go Short
        df_spread_trade["Trade"][i] = -1
        in_short = True
    # Exit Trade
    if df_spread_trade["spread_rolling_z_score"][i-1] < 0 and in_long:      # Stop Long
        df_spread_trade["Trade"][i] = 0
        in_long = False
    elif df_spread_trade["spread_rolling_z_score"][i-1] > 0 and in_short:   # Stop Short
        df_spread_trade["Trade"][i] = 0
        in_short = False

df_spread_trade["Returns"] = np.zeros(len(df_spread_trade))
for i in range(len(pairs_price)):
    if (df_spread_trade["Trade"][i] > 0):       # We are Short First Security, Long Second
        df_spread_trade["Returns"][i] = (pairs_price[name_security_A][i-1] - pairs_price[name_security_A][i])/pairs_price[name_security_A][i] + (pairs_price[name_security_B][i] - pairs_price[name_security_B][i-1])/pairs_price[name_security_B][i-1]
    elif (df_spread_trade["Trade"][i] < 0):     # We are Long First Security, Short Second
        df_spread_trade["Returns"][i] = (pairs_price[name_security_A][i] - pairs_price[name_security_A][i-1])/pairs_price[name_security_B][i-1] + (pairs_price[name_security_B][i-1] - pairs_price[name_security_B][i])/pairs_price[name_security_B][i]

returns_long = 0
returns_short = 0
for i in range(len(pairs_price)):
    if (df_spread_trade["Trade"][i] > 0): returns_long+=df_spread_trade["Returns"][i]
    elif (df_spread_trade["Trade"][i] < 0): returns_short+=df_spread_trade["Returns"][i]
print("Returns Long: ", returns_long)
print("Returns Short: ", returns_short)

df_spread_trade.to_excel("output.xlsx") 

