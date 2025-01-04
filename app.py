from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
from prophet import Prophet
import datetime

app = Flask(__name__)

# Function to convert week number to a real-world date
def convert_week_to_date(week, start_year=2022):
    # Define Week 1 as the first Monday of January in the start_year
    start_date = datetime.date(start_year, 3, 1)
    start_date += datetime.timedelta(days=(7 - start_date.weekday()))  # Adjust to Monday
    delta = datetime.timedelta(weeks=week - 1)
    return start_date + delta

# Function to fetch data from the database
def fetch_data(region_code, category=None):
    conn = sqlite3.connect('food_demand.db')
    query = f"""
    SELECT week, num_orders
    FROM orders_data
    WHERE region_code = '{region_code}'
    """
    if category:
        query += f" AND category = '{category}'"
    query += " ORDER BY week"
    
    # Fetch data
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Convert week to real-world dates
    data['ds'] = data['week'].apply(lambda x: convert_week_to_date(x))
    data.rename(columns={'num_orders': 'y'}, inplace=True)
    return data

# Function to append user data dynamically
def append_user_data(region_code, category, num_orders):
    conn = sqlite3.connect('food_demand.db')
    cursor = conn.cursor()

    # Get the latest date from the database
    cursor.execute("SELECT MAX(week) FROM orders_data")
    latest_week = cursor.fetchone()[0]

    # Calculate the next week
    next_week = latest_week + 1 if latest_week else 1

    # Insert the new record
    cursor.execute("""
        INSERT INTO orders_data (week, region_code, category, num_orders)
        VALUES (?, ?, ?, ?)
    """, (next_week, region_code, category, num_orders))
    conn.commit()
    conn.close()

# Endpoint for predictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get user inputs
        user_input = request.get_json()
        region_code = user_input['region_code']
        category = user_input.get('category')  # Optional
        
        # Fetch relevant data
        data = fetch_data(region_code, category)
        if data.empty:
            return jsonify({'error': 'No data found for the given region and category'}), 404

        # Initialize and fit Prophet model
        model = Prophet()
        model.fit(data)

        # Generate future dates
        future = model.make_future_dataframe(periods=10, freq='W')
        forecast = model.predict(future)

        # Extract and format predictions
        result = forecast[['ds', 'yhat']].tail(10)
        result.rename(columns={'ds': 'week', 'yhat': 'predicted_orders'}, inplace=True)
        result['week'] = result['week'].dt.strftime('%Y-%m-%d')  # Format week for readability

        # Return predictions as JSON
        return jsonify(result.to_dict(orient='records'))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint for adding user data
@app.route('/add_data', methods=['POST'])
def add_data():
    try:
        # Get user inputs
        user_input = request.get_json()
        region_code = user_input['region_code']
        category = user_input['category']
        num_orders = user_input['num_orders']

        # Append the data
        append_user_data(region_code, category, num_orders)
        return jsonify({'message': 'Data added successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Main app
if __name__ == '__main__':
    app.run(debug=True)
