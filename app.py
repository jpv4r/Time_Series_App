from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
from prophet import Prophet
import datetime

app = Flask(__name__)

# Function to convert week number to real-world date (Starting from March 14, 2025)
def convert_week_to_date(week, start_year=2025):
    start_date = datetime.date(start_year, 3, 14)  # Fixed start date
    delta = datetime.timedelta(weeks=week - 1)  # Shift weeks dynamically
    return start_date + delta

# Function to fetch data from the database
def fetch_data(region_code, category=None):
    conn = sqlite3.connect('food_demand.db')
    query = """
    SELECT week, num_orders, category
    FROM orders_data
    WHERE region_code = ?
    """
    params = [region_code]

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY week"

    # Fetch data
    data = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert week to actual dates
    if not data.empty:
        data['ds'] = data['week'].apply(lambda x: convert_week_to_date(x))
        data.rename(columns={'num_orders': 'y'}, inplace=True)

    return data

# Function to append user input data dynamically
def append_user_data(region_code, category, num_orders):
    conn = sqlite3.connect('food_demand.db')
    cursor = conn.cursor()

    # Get latest recorded week number
    cursor.execute("SELECT MAX(week) FROM orders_data WHERE region_code = ?", (region_code,))
    latest_week = cursor.fetchone()[0] or 0

    # Assign the next week's number dynamically
    next_week = latest_week + 1

    # Insert new record
    cursor.execute("""
        INSERT INTO orders_data (week, region_code, category, num_orders)
        VALUES (?, ?, ?, ?)
    """, (next_week, region_code, category, num_orders))

    conn.commit()
    conn.close()

# Prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    try:
        user_input = request.get_json()
        region_code = user_input['region_code']
        category = user_input.get('category')  # Optional field

        # Fetch relevant data
        data = fetch_data(region_code, category)
        if data.empty:
            return jsonify({'error': 'No data found for the given region and category'}), 404

        # Initialize and train Prophet model
        model = Prophet()
        model.fit(data)

        # Generate future dates starting from March 14, 2025
        future = model.make_future_dataframe(periods=10, freq='W')
        future['ds'] = pd.date_range(start="2025-03-14", periods=10, freq='W')
        forecast = model.predict(future)

        # Extract predictions
        result = forecast[['ds', 'yhat']].tail(10)
        result.rename(columns={'ds': 'week', 'yhat': 'predicted_orders'}, inplace=True)
        result['week'] = result['week'].dt.strftime('%Y-%m-%d')  # Formatting

        return jsonify(result.to_dict(orient='records'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User data insertion endpoint
@app.route('/add_data', methods=['POST'])
def add_data():
    try:
        user_input = request.get_json()
        region_code = user_input['region_code']
        category = user_input['category']
        num_orders = user_input['num_orders']

        # Append the user data
        append_user_data(region_code, category, num_orders)
        return jsonify({'message': 'Data added successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
