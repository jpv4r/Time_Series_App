import streamlit as st
import pandas as pd
from prophet import Prophet
import sqlite3
import datetime
import plotly.express as px

# Title and description
st.title("Food Demand-Supply Forecasting")
st.markdown("This application predicts food demand for the next 10 weeks based on region and category.")

# Function to convert week to date
def convert_week_to_date(week, start_year=2020):
    start_date = datetime.date(start_year, 1, 1)
    start_date += datetime.timedelta(days=(7 - start_date.weekday()))  # Adjust to Monday
    delta = datetime.timedelta(weeks=week - 1)
    return start_date + delta

# Fetch data from SQLite
def fetch_data(region_code, category=None):
    conn = sqlite3.connect('food_demand.db')
    query = f"SELECT week, num_orders FROM orders_data WHERE region_code = '{region_code}'"
    if category:
        query += f" AND category = '{category}'"
    query += " ORDER BY week"
    data = pd.read_sql_query(query, conn)
    conn.close()
    data['ds'] = data['week'].apply(lambda x: convert_week_to_date(x))
    data.rename(columns={'num_orders': 'y'}, inplace=True)
    return data

# Get user inputs
region_code = st.text_input("Enter Region Code (e.g., 56)", value="56")
category = st.text_input("Enter Category (e.g., Beverages)", value="Beverages")

# Submit button
if st.button("Predict"):
    # Fetch data and check if empty
    data = fetch_data(region_code, category)
    if data.empty:
        st.error("No data found for the given region and category.")
    else:
        # Fit Prophet model
        model = Prophet()
        model.fit(data)

        # Generate future predictions
        future = model.make_future_dataframe(periods=10, freq='W')
        forecast = model.predict(future)

        # Prepare data for visualization
        result = forecast[['ds', 'yhat']].tail(10)
        result.rename(columns={'ds': 'week', 'yhat': 'predicted_orders'}, inplace=True)
        result['week'] = result['week'].dt.strftime('%Y-%m-%d')

        # Line chart
        fig = px.line(result, x="week", y="predicted_orders", title="Forecasted Orders for the Next 10 Weeks")
        st.plotly_chart(fig)

        # Data table
        st.subheader("Forecasted Data")
        st.write(result)
