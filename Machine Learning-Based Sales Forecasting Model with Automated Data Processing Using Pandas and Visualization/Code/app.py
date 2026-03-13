import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# Set page configuration
st.set_page_config(
    page_title="EV Sales Forecasting",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #f5f7f9;
        padding: 2rem;
    }
    
    /* Headers */
    .css-10trblm {
        color: #1f4287;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    
    /* Metrics */
    .css-1r6slb0 {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1rem;
        transition: transform 0.3s ease;
    }
    .css-1r6slb0:hover {
        transform: translateY(-5px);
    }
    
    /* Charts container */
    .chart-container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1f4287;
        padding: 2rem 1rem;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #1f4287;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #163364;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🚗 Global EV Sales Forecasting Dashboard")
st.markdown("### Machine Learning-Based Sales Prediction and Analysis")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("IEA-EV-dataEV salesHistoricalCars.csv")
    return df

df = load_data()

# Sidebar
with st.sidebar:
    st.header("Dashboard Controls")
    selected_region = st.selectbox(
        "Select Region",
        options=df['region'].unique()
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This dashboard provides insights into global EV sales trends and forecasts
    using advanced machine learning techniques.
    """)

# Main content
col1, col2, col3 = st.columns(3)

# Key metrics
filtered_df = df[df['region'] == selected_region]
latest_year = filtered_df['year'].max()
latest_sales = filtered_df[filtered_df['year'] == latest_year]['value'].values[0]
growth = ((latest_sales - filtered_df[filtered_df['year'] == latest_year-1]['value'].values[0]) / 
         filtered_df[filtered_df['year'] == latest_year-1]['value'].values[0] * 100)

with col1:
    st.metric("Latest Annual Sales", f"{int(latest_sales):,}", f"{growth:.1f}% YoY")
    
with col2:
    avg_sales = filtered_df['value'].mean()
    st.metric("Average Annual Sales", f"{int(avg_sales):,}")
    
with col3:
    total_sales = filtered_df['value'].sum()
    st.metric("Total Historical Sales", f"{int(total_sales):,}")

# Sales Trend Chart
st.markdown("### Historical Sales Trend")
fig_trend = px.line(
    filtered_df,
    x='year',
    y='value',
    title=f'EV Sales Trend in {selected_region}',
    template='plotly_white'
)
fig_trend.update_traces(line_color='#1f4287', line_width=3)
fig_trend.update_layout(
    xaxis_title="Year",
    yaxis_title="Sales Volume",
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig_trend, use_container_width=True)

# Year-over-Year Growth
st.markdown("### Year-over-Year Growth Analysis")
filtered_df['YoY_Growth'] = filtered_df['value'].pct_change() * 100

fig_growth = px.bar(
    filtered_df[filtered_df['year'] > filtered_df['year'].min()],
    x='year',
    y='YoY_Growth',
    title=f'Year-over-Year Growth Rate in {selected_region}',
    template='plotly_white'
)
fig_growth.update_traces(marker_color='#1f4287')
fig_growth.update_layout(
    xaxis_title="Year",
    yaxis_title="Growth Rate (%)",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig_growth, use_container_width=True)

# Regional Comparison
st.markdown("### Regional Market Share Analysis")
latest_year_data = df[df['year'] == df['year'].max()]
fig_pie = px.pie(
    latest_year_data,
    values='value',
    names='region',
    title=f'Regional Market Share Distribution ({latest_year})',
    template='plotly_white'
)
fig_pie.update_traces(
    textposition='inside',
    textinfo='percent+label'
)
st.plotly_chart(fig_pie, use_container_width=True)

# LSTM-Based Future Sales Forecast (2024–2030)
st.markdown("### LSTM-Based Future Sales Forecast (2024–2030)")

# Prepare data for LSTM (total global sales per year)
dl_df = df[df['parameter'] == 'EV sales'].groupby('year')['value'].sum().reset_index()
dl_df.rename(columns={'value': 'total_sales'}, inplace=True)

# Normalize data
df_years = dl_df['year']
scaler = MinMaxScaler()
scaled_sales = scaler.fit_transform(dl_df[['total_sales']])

# Load LSTM model
lstm_model = load_model('lstm_model.h5')

# Create last sequence (window=3)
window = 3
last_sequence = scaled_sales[-window:]
predictions_scaled = []

for _ in range(7):  # Predict 2024–2030
    input_seq = last_sequence[-window:].reshape(1, window, 1)
    pred = lstm_model.predict(input_seq, verbose=0)
    predictions_scaled.append(pred[0][0])
    last_sequence = np.append(last_sequence, pred[0][0])

# Inverse transform to get real values
predicted_values = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1)).flatten()
forecast_years = list(range(2024, 2031))
actual_years = dl_df['year']
actual_values = dl_df['total_sales']

# Plot actual vs forecast using Plotly
fig_lstm = go.Figure()
fig_lstm.add_trace(go.Scatter(x=actual_years, y=actual_values, mode='lines+markers', name='Actual Sales', line=dict(color='#1f4287', width=3)))
fig_lstm.add_trace(go.Scatter(x=forecast_years, y=predicted_values, mode='lines+markers', name='LSTM Forecast', line=dict(color='#e94560', width=3, dash='dash')))
fig_lstm.add_vline(x=2023.5, line_dash='dash', line_color='red', annotation_text='Forecast Start', annotation_position='top right')
fig_lstm.update_layout(
    title="EV Sales Forecast using LSTM (2024–2030)",
    xaxis_title="Year",
    yaxis_title="EV Sales (Vehicles)",
    legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0)'),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_lstm, use_container_width=True)

