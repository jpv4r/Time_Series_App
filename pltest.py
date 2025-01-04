from prophet import Prophet

# Example data
import pandas as pd
data = pd.DataFrame({
    'ds': pd.date_range(start='2025-01-01', periods=10, freq='D'),
    'y': [10, 12, 15, 18, 19, 21, 24, 25, 28, 30]
})

model = Prophet()
model.fit(data)
future = model.make_future_dataframe(periods=5)
forecast = model.predict(future)
print(forecast[['ds', 'yhat']].tail())
