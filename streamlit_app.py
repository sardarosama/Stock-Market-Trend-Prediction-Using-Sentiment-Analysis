import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import matplotlib.pyplot as plt
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MinMaxScaler


# App 1: Stock Market Trend Prediction Using Sentiment Analysis

st.title("Stock Market Trend Prediction Using Sentiment Analysis")

ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

# Check if the ticker and start date are provided
if ticker and start_date:
    # Fetch historical stock data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Check if data is available
    if not data.empty:
        # Display the fetched data in a line chart
        fig = px.line(data, x=data.index, y='Close', title=f'{ticker} Stock Price')
        st.plotly_chart(fig)

        pricing_data, predictions = st.tabs(["Pricing Data", "Predictions"])

        with pricing_data:
            st.header("Price Movement")
            data2 = data.copy()
            data2['% Change'] = data['Adj Close'] / data2['Adj Close'].shift(1)
            data2.dropna(inplace=True)
            st.write(data2)
            annual_return = data2['% Change'].mean() * 252 * 100 - 1
            st.write('Annual Return:', annual_return, '%')
            stdev = np.std(data2['% Change']) * np.sqrt(252)
            st.write('Standard Deviation:', stdev * 100, '%')
            st.write('Risk-Adjusted Return:', annual_return / (stdev * 100))

        with predictions:
            st.header("Predictions")
            # Display the fetched data in a line chart
            st.plotly_chart(fig)

    else:
        st.write("No data available for the specified ticker and date range.")

else:
    st.write("Please enter a valid ticker and start date.")

# App 2: Stock Trend Prediction

st.title("Stock Trend Prediction")

start = "2011-02-01"
end = "2019-12-31"
user_input = st.text_input("Enter Stock Ticker", "AAPL")
df = yf.download(user_input, start=start, end=end)
df = df.reset_index()
df = df.dropna()

# Describing data
st.subheader('Data from 2011-2019')
st.write("Description")
st.write(df.describe())

# Visualization
st.subheader("Closing Price vs Time Chart")
fig = plt.figure(figsize=(12, 6))
plt.plot(df.Close)
st.pyplot(fig)

st.subheader("Closing Price vs Time Chart with 100MA")
ma100 = df.Close.rolling(100).mean()
fig = plt.figure(figsize=(12, 6))
plt.plot(ma100)
plt.plot(df.Close)
st.pyplot(fig)

st.subheader("Closing Price vs Time Chart with 100MA and 200MA")
ma100 = df.Close.rolling(100).mean()
ma200 = df.Close.rolling(200).mean()
fig = plt.figure(figsize=(12, 6))
plt.plot(ma100, "b")
plt.plot(ma200, "g")
plt.plot(df.Close)
st.pyplot(fig)

data_training = pd.DataFrame(df["Close"][0:int(len(df) * 0.70)])
data_testing = pd.DataFrame(df["Close"][int(len(df) * 0.70):int(len(df))])

if len(data_testing) > 0:
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_training_array = scaler.fit_transform(data_training)

    model = load_model("stock_sentiment_model.pt.h5")

    # Feeding model with past 100 days of data
    # Testing part
    past_100_days = data_training.tail(100)
    final_df = past_100_days.append(data_testing, ignore_index=True)
    input_data = scaler.transform(final_df)
    x_test = []
    y_test = []
    for i in range(100, input_data.shape[0]):
        x_test.append(input_data[i - 100:i])
        y_test.append(input_data[i, 0])

    x_test, y_test = np.array(x_test), np.array(y_test)

    y_pred = model.predict(x_test)

    scale_factor = 1 / 0.13513514
    y_pred = y_pred * scale_factor
    y_test = y_test * scale_factor

    # Final graph
    st.subheader("Prediction vs Original")
    fig2 = plt.figure(figsize=(12, 6))
    plt.plot(y_pred, 'r', label='Predicted Price')
    plt.plot(y_test, 'b', label='Original Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    st.pyplot(fig2)
else:
    st.write("Insufficient data for testing.")