import pandas as pd
import matplotlib.pyplot as plt

# Load the data
file_path = "Quote-Equity-HDFCBANK-EQ-02-01-2024-to-02-01-2025.csv"  # Replace with the actual file path
data = pd.read_csv(file_path)

# Clean the data: remove commas and convert to numeric where needed
for column in ["OPEN ", "HIGH ", "LOW ", "PREV. CLOSE ", "ltp ", "close ", "vwap ", "VOLUME ", "VALUE "]:
    data[column] = data[column].str.replace(",", "").astype(float)

# Ensure the "Date " column is treated as a datetime object
data["Date "] = pd.to_datetime(data["Date "])

# Sort the data by date (oldest to newest)
data = data.sort_values("Date ")

# Calculate MACD and Signal Line
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    data["EMA12"] = data["close "].ewm(span=short_window, adjust=False).mean()
    data["EMA26"] = data["close "].ewm(span=long_window, adjust=False).mean()
    data["MACD"] = data["EMA12"] - data["EMA26"]
    data["Signal_Line"] = data["MACD"].ewm(span=signal_window, adjust=False).mean()
    return data

data = calculate_macd(data)


# Implement buy/sell signals
def generate_signals(data):
    data["Buy_Signal"] = (data["MACD"] > data["Signal_Line"]) & (data["MACD"].shift(1) <= data["Signal_Line"].shift(1))
    data["Sell_Signal"] = (data["MACD"] < data["Signal_Line"]) & (data["MACD"].shift(1) >= data["Signal_Line"].shift(1))
    return data

data = generate_signals(data)
print(data)


# Simulate trading
def backtest(data, initial_balance=100000):
    balance = initial_balance
    position = 0  # 0 means no stock, 1 means holding stock
    for i in range(len(data)):
        if data["Buy_Signal"].iloc[i]:
            position = balance / data["close "].iloc[i]
            balance = 0
        elif data["Sell_Signal"].iloc[i] and position > 0:
            balance = position * data["close "].iloc[i]
            position = 0
    # Final balance if holding stock
    if position > 0:
        balance = position * data["close "].iloc[-1]
    return balance

final_balance = backtest(data)
# print(f"Initial Balance: $100000, Final Balance: ${final_balance:.2f}")
print("if buy and hold: ", (data["close "].iloc[-1]-data["close "].iloc[0])/data["close "].iloc[0]*100)
print(f"Profit/Loss with MCAD:  ${round(final_balance - 100000)/1000} %")


# Plot MACD, Signal Line, and Buy/Sell Signals
plt.figure(figsize=(14, 7))

# Plot Close Price
plt.subplot(2, 1, 1)
plt.plot(data["Date "], data["close "], label="Close Price", color="blue")
plt.scatter(data["Date "][data["Buy_Signal"]], data["close "][data["Buy_Signal"]], label="Buy Signal", marker="^", color="green", alpha=1)
plt.scatter(data["Date "][data["Sell_Signal"]], data["close "][data["Sell_Signal"]], label="Sell Signal", marker="v", color="red", alpha=1)
plt.title("Close Price and Buy/Sell Signals")
plt.legend()

# Plot MACD and Signal Line
plt.subplot(2, 1, 2)
plt.plot(data["Date "], data["MACD"], label="MACD", color="blue")
plt.plot(data["Date "], data["Signal_Line"], label="Signal Line", color="orange")
plt.title("MACD and Signal Line")
plt.legend()

plt.tight_layout()
plt.show()
