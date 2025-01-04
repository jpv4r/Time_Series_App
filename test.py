import requests

# Base URL of the Flask app
base_url = "http://127.0.0.1:5000"

# Test the /add_data endpoint
def test_add_data():
    add_data_url = f"{base_url}/add_data"
    payload = {
        "region_code": "56",
        "category": "Beverages",
        "num_orders": 150
    }
    response = requests.post(add_data_url, json=payload)
    if response.status_code == 200:
        print("Add Data Response:", response.json())
    else:
        print(f"Add Data Error ({response.status_code}):", response.json())

# Test the /predict endpoint
def test_predict():
    predict_url = f"{base_url}/predict"
    payload = {
        "region_code": "56",
        "category": "Beverages"
    }
    response = requests.post(predict_url, json=payload)
    if response.status_code == 200:
        print("Prediction Response:", response.json())
    else:
        print(f"Prediction Error ({response.status_code}):", response.json())

# Run tests
if __name__ == "__main__":
    print("Testing /add_data endpoint...")
    test_add_data()

    print("\nTesting /predict endpoint...")
    test_predict()

