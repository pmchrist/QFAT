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
def spread_trade(name_security_A, name_security_B, pairs_price, delay=0):
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
        if df_spread_trade["spread_rolling_z_score"][i - delay] > 2 and not long_on_cheap:      # Go Long
            df_spread_trade["Trade"][i] = 1
            long_on_cheap = True
        elif df_spread_trade["spread_rolling_z_score"][i - delay] < -2 and not short_on_cheap:   # Go Short
            df_spread_trade["Trade"][i] = -1
            short_on_cheap = True
        # Exit Trade
        if df_spread_trade["spread_rolling_z_score"][i - delay] < 0 and long_on_cheap:      # Stop Long
            df_spread_trade["Trade"][i] = 0
            long_on_cheap = False
        elif df_spread_trade["spread_rolling_z_score"][i - delay] > 0 and short_on_cheap:   # Stop Short
            df_spread_trade["Trade"][i] = 0
            short_on_cheap = False

    # Find Returns
    df_spread_trade["Returns"] = np.zeros(len(df_spread_trade))
    for i in range(len(df_spread_trade)):
        if i > 0:
            if (df_spread_trade["Trade"][i-1] > 0):       # We are Short Security A, Long Security B
                # Short expensive security:
                short_A= -1 * (df_spread_trade[name_security_A][i] - df_spread_trade[name_security_A][i-1]) / df_spread_trade[name_security_A][i]
                long_B = (df_spread_trade[name_security_B][i] - df_spread_trade[name_security_B][i-1]) / df_spread_trade[name_security_B][i]
                df_spread_trade["Returns"][i] = short_A + long_B
                
                # df_spread_trade["Returns"][i] = (df_spread_trade[name_security_A][i-1] - df_spread_trade[name_security_A][i])/df_spread_trade[name_security_A][i] + (df_spread_trade[name_security_B][i] - df_spread_trade[name_security_B][i-1])/df_spread_trade[name_security_B][i]
            elif (df_spread_trade["Trade"][i-1] < 0):     # We are Long Security A, Short Security B
                long_A = (df_spread_trade[name_security_A][i] - df_spread_trade[name_security_A][i-1]) / df_spread_trade[name_security_A][i]
                short_B = -1 * (df_spread_trade[name_security_B][i] - df_spread_trade[name_security_B][i-1]) / df_spread_trade[name_security_B][i]
                df_spread_trade["Returns"][i] = long_A + short_B
                
                # df_spread_trade["Returns"][i] = (df_spread_trade[name_security_A][i-1] - df_spread_trade[name_security_A][i])/df_spread_trade[name_security_B][i] + (df_spread_trade[name_security_B][i-1] - df_spread_trade[name_security_B][i])/df_spread_trade[name_security_B][i]

    # Sum Returns
    returns_long = 0
    returns_short = 0
    total_returns = 0
    for i in range(len(df_spread_trade)):
        if i > 0:
            if (df_spread_trade["Trade"][i-1] > 0): 
                returns_long += df_spread_trade["Returns"][i]

            elif (df_spread_trade["Trade"][i-1] < 0): 
                returns_short += df_spread_trade["Returns"][i]

        total_returns += df_spread_trade["Returns"][i]
    
    for i in range(max(len(name_security_A), len(name_security_B))):
        if name_security_A[:i] in name_security_B:
            sec_name = name_security_A[:i]
    sec_name = sec_name.strip("_")

    return df_spread_trade

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

output_file = pd.ExcelWriter("output_allsecs.xlsx")
for i, df in enumerate(df_list):
    df.to_excel(output_file, sheet_name="{0}".format(names[i]))

output_file.save()

def returns_for_plot(pairs_price, delay=0):
    returns = dict()

    for (sec_A, sec_B) in zip(securities_A, securities_B):

        for i in range(max(len(sec_A), len(sec_B))):
            if sec_A[:i] in sec_B:
                sec_name = sec_A[:i]
        sec_name = sec_name.strip("_")

        df = spread_trade(sec_A, sec_B, pairs_price, delay)
        
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
def calc_SR(securities_A, securities_B, delay = 0):

    all_returns = dict()
    for (sec_A, sec_B) in zip(securities_A, securities_B):

            for i in range(max(len(sec_A), len(sec_B))):
                if sec_A[:i] in sec_B:
                    sec_name = sec_A[:i]
            sec_name = sec_name.strip("_")

            df = spread_trade(sec_A, sec_B, pairs_price, delay)
            
            all_returns[sec_name] = df["Returns"]

    returns_df = pd.DataFrame(all_returns)

    equalport_df = returns_df / 8               # Equal Weights
    equalport_df = equalport_df.sum(axis=1)
    equalport_list = list(equalport_df)

    # Annual expected return
    mean_ret = np.mean(equalport_list)

    # Standard deviation
    sd_ret = np.std(equalport_list)

    # Annualized Sharpe Ratio
    SR_ann = mean_ret / sd_ret * math.sqrt(252)

    return SR_ann

SR_ann = calc_SR(securities_A, securities_B)

# 1_5C
df_plot_delay = returns_for_plot(pairs_price, delay = 1)
df_plot_delay = df_plot_delay * 100

df_plot_delay.plot()
plt.xlabel("Date")
plt.ylabel("Cumulative returns (%)")
plt.grid()
plt.show()

# Annualized SR calculation for equal-weighted portfolio
SR_ann_delay = calc_SR(securities_A, securities_B, delay=1)

print("Annualized SR of portfolio without delay: ", SR_ann)
print("Annualized SR of portfolio with delay: ", SR_ann_delay)

print("\n")
print(df_plot)
print(df_plot_delay)