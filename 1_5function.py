# 1.5

# Imports
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np
import math
import statistics as stat

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

# Reading Data
pairs_price = pd.read_csv("Pairs_Price.csv")
pairs_ri = pd.read_csv("Pairs_RI.csv")
print(pairs_price.head())
#print(pairs_ri.head())

# Drop NaN's
pairs_price = pairs_price.dropna()

# Insert date as index
pairs_price = pairs_price.set_index(pd.to_datetime(pairs_price["date"], dayfirst = True))

# 1_5B
def spread_trade(name_security_A, name_security_B, pairs_price):
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
    total_returns = 0
    for i in range(len(df_spread_trade)):
        if (df_spread_trade["Trade"][i] > 0): 
            returns_long += df_spread_trade["Returns"][i]

        elif (df_spread_trade["Trade"][i] < 0): 
            returns_short += df_spread_trade["Returns"][i]

        total_returns += df_spread_trade["Returns"][i]
    
    for i in range(max(len(name_security_A), len(name_security_B))):
        if name_security_A[:i] in name_security_B:
            sec_name = name_security_A[:i]
    sec_name = sec_name.strip("_")

    return df_spread_trade #, returns_long, returns_short

# Empty securities lists
securities_A = []
securities_B = []

for col in pairs_price.columns[1::2]:
    securities_A.append(col)

for col in pairs_price.columns[2::2]:
    securities_B.append(col)

df_list = []
# Spread trade calculations
for (sec_A, sec_B) in zip(securities_A, securities_B):
    df_spread_trade = spread_trade(sec_A, sec_B, pairs_price)
    df_list.append(df_spread_trade)

names = []
for (sec_A, sec_B) in zip(securities_A, securities_B):
    for i in range(max(len(sec_A), len(sec_B))):
        if sec_A[:i] in sec_B:
            sec_name = sec_A[:i]
    sec_name = sec_name.strip("_")
    names.append(sec_name)   

output_file = pd.ExcelWriter(r"output_allsecs.xlsx")
for i, df in enumerate(df_list):
    df.to_excel(output_file, sheet_name="{0}".format(names[i]))

output_file.save()

def returns_for_plot(pairs_price):
    returns = dict()

    for (sec_A, sec_B) in zip(securities_A, securities_B):

        for i in range(max(len(sec_A), len(sec_B))):
            if sec_A[:i] in sec_B:
                sec_name = sec_A[:i]
        sec_name = sec_name.strip("_")

        df = spread_trade(sec_A, sec_B, pairs_price)
        
        returns[sec_name] = df["Returns"]

    returns_df = pd.DataFrame(returns)

    equalport_df = returns_df / 8
    equalport_df = equalport_df.sum(axis=1)
    returns_df["EQUALPORT"] = equalport_df

    cum_returns_df = returns_df.cumsum()
    return cum_returns_df


df_plot = returns_for_plot(pairs_price)
df_plot = df_plot * 100
df_plot.plot()
plt.xlabel("Date")
plt.ylabel("Cumulative returns (%)")
plt.grid()
plt.show()


# Annualized SR of equal-weighted portfolio
all_returns = dict()
for (sec_A, sec_B) in zip(securities_A, securities_B):

        for i in range(max(len(sec_A), len(sec_B))):
            if sec_A[:i] in sec_B:
                sec_name = sec_A[:i]
        sec_name = sec_name.strip("_")

        df = spread_trade(sec_A, sec_B, pairs_price)
        
        all_returns[sec_name] = df["Returns"]

returns_df = pd.DataFrame(all_returns)

equalport_df = returns_df / 8
equalport_df = equalport_df.sum(axis=1)
equalport_list = list(equalport_df)

# Annualized expected return
mean_ret = stat.mean(equalport_list)
mean_ret_ann = mean_ret * 250

# Annualized standard deviation
sd_ret = np.std(equalport_list)
sd_ret_ann = sd_ret * math.sqrt(250)

# Annualized Sharpe Ratio
SR_ann = mean_ret_ann / sd_ret_ann


# 1_5C
def spread_trade_delay(name_security_A, name_security_B, pairs_price):
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
        if df_spread_trade["spread_rolling_z_score"][i-2] > 2 and not long_on_cheap:      # Go Long
            df_spread_trade["Trade"][i] = 1
            long_on_cheap = True
        elif df_spread_trade["spread_rolling_z_score"][i-2] < -2 and not short_on_cheap:   # Go Short
            df_spread_trade["Trade"][i] = -1
            short_on_cheap = True
        # Exit Trade
        if df_spread_trade["spread_rolling_z_score"][i-2] < 0 and long_on_cheap:      # Stop Long
            df_spread_trade["Trade"][i] = 0
            long_on_cheap = False
        elif df_spread_trade["spread_rolling_z_score"][i-2] > 0 and short_on_cheap:   # Stop Short
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
    total_returns = 0
    for i in range(len(df_spread_trade)):
        if (df_spread_trade["Trade"][i] > 0): 
            returns_long += df_spread_trade["Returns"][i]

        elif (df_spread_trade["Trade"][i] < 0): 
            returns_short += df_spread_trade["Returns"][i]

        total_returns += df_spread_trade["Returns"][i]

    for i in range(max(len(name_security_A), len(name_security_B))):
        if name_security_A[:i] in name_security_B:
            sec_name = name_security_A[:i]
    sec_name = sec_name.strip("_")

    return df_spread_trade #, returns_long, returns_short


def returns_for_plot_delay(pairs_price):
    returns = dict()

    for (sec_A, sec_B) in zip(securities_A, securities_B):

        for i in range(max(len(sec_A), len(sec_B))):
            if sec_A[:i] in sec_B:
                sec_name = sec_A[:i]
        sec_name = sec_name.strip("_")

        df = spread_trade_delay(sec_A, sec_B, pairs_price)
        
        returns[sec_name] = df["Returns"]

    returns_df = pd.DataFrame(returns)

    equalport_df = returns_df / 8
    equalport_df = equalport_df.sum(axis=1)
    returns_df["EQUALPORT"] = equalport_df

    cum_returns_df = returns_df.cumsum()
    return cum_returns_df

df_plot_delay = returns_for_plot_delay(pairs_price)
df_plot_delay = df_plot_delay * 100

df_plot_delay.plot()
plt.xlabel("Date")
plt.ylabel("Cumulative returns (%)")
plt.grid()
plt.show()

# Annualized SR calculation for equal-weighted portfolio
all_returns2 = dict()
for (sec_A, sec_B) in zip(securities_A, securities_B):

        for i in range(max(len(sec_A), len(sec_B))):
            if sec_A[:i] in sec_B:
                sec_name = sec_A[:i]
        sec_name = sec_name.strip("_")

        df2 = spread_trade_delay(sec_A, sec_B, pairs_price)
        
        all_returns2[sec_name] = df2["Returns"]

returns_df2 = pd.DataFrame(all_returns2)

equalport_df2 = returns_df2 / 8
equalport_df2 = equalport_df2.sum(axis=1)
equalport_list2 = list(equalport_df2)

# Annualized expected return
mean_ret2 = stat.mean(equalport_list2)
mean_ret_ann2 = mean_ret2 * 250

# Annualized standard deviation
sd_ret2 = np.std(equalport_list2)
sd_ret_ann2 = sd_ret2 * math.sqrt(250)

# Annualized Sharpe Ratio
SR_ann2 = mean_ret_ann2 / sd_ret_ann2

print("Annualized SR of portfolio without delay: ", SR_ann)
print("Annualized SR of portfolio with delay: ", SR_ann2)

print("\n")
print(df_plot)
print(df_plot_delay)