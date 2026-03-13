
# Energy Consumption Forecasting and Visualization for Smart Homes
# Using Data Analytics and Machine Learning

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

# Load the dataset
df = pd.read_csv("events.csv")

# Convert 'Start time UTC' to datetime
df['Start time UTC'] = pd.to_datetime(df['Start time UTC'], format='%d-%m-%Y %H:%M')
df.set_index('Start time UTC', inplace=True)

# Rename target column for ease of access
df.rename(columns={"Electricity consumption in Finland": "Electricity_Consumption"}, inplace=True)

# Resample data to daily consumption
df_daily = df.resample('D').sum(numeric_only=True)

# Create time-based features
df_daily['Day'] = df_daily.index.day
df_daily['Month'] = df_daily.index.month
df_daily['Year'] = df_daily.index.year
df_daily['Weekday'] = df_daily.index.weekday

# Create lag features to capture temporal patterns
df_daily['Lag1'] = df_daily['Electricity_Consumption'].shift(1)
df_daily['Lag2'] = df_daily['Electricity_Consumption'].shift(2)
df_daily['Lag3'] = df_daily['Electricity_Consumption'].shift(3)

# Drop NA values
df_daily.dropna(inplace=True)

# Define features and target variable
X = df_daily.drop("Electricity_Consumption", axis=1)
y = df_daily["Electricity_Consumption"]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Train a Random Forest Regressor model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R2 Score: {r2}")

# Plot actual vs predicted values
plt.figure(figsize=(12, 6))
plt.plot(y_test.index, y_test, label="Actual")
plt.plot(y_test.index, y_pred, label="Predicted", alpha=0.7)
plt.title("Actual vs Predicted Electricity Consumption")
plt.xlabel("Date")
plt.ylabel("Electricity Consumption")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
# After model predictions
results_df = pd.DataFrame({
    'Date': y_test.index,
    'Actual_Consumption': y_test.values,
    'Predicted_Consumption': y_pred
})

# Save to CSV for Power BI
results_df.to_csv("energy_forecast_results.csv", index=False)
