import pandas as pd

# Load the datasets
train_data = pd.read_csv('train.csv')
center_data = pd.read_csv('fulfilment_center_info.csv')
meal_data = pd.read_csv('meal_info.csv')

# Merge train data with center data on 'center_id'
merged_data = pd.merge(train_data, center_data, on='center_id', how='left')

# Merge the result with meal data on 'meal_id'
merged_data = pd.merge(merged_data, meal_data, on='meal_id', how='left')

# Save the merged data to a new CSV file
merged_data.to_csv('merged_data.csv', index=False)

# Print confirmation and first few rows
print("Merged data saved to 'merged_data.csv'.")
print(merged_data.head())
