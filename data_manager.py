import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_data(days=30):
    np.random.seed(42)
    start_date = datetime.now() - timedelta(days=days)
    dates = [start_date + timedelta(hours=i) for i in range(days * 24)]
    
    df = pd.DataFrame({'timestamp': dates})
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    base_temp = 22 + 8 * np.sin(np.pi * (df['hour'] - 8) / 12)
    df['temperature'] = base_temp + np.random.normal(0, 2, len(df))
    
    time_demand_factor = np.sin(np.pi * (df['hour'] - 6) / 12) * 300 + 600
    peak_evening_factor = np.exp(-((df['hour'] - 19)**2) / 8) * 250
    temp_heating_cooling = np.abs(df['temperature'] - 20) * 15
    weekend_reduction = df['is_weekend'] * (-100)
    
    df['energy_demand'] = (time_demand_factor + peak_evening_factor + 
                           temp_heating_cooling + weekend_reduction + 
                           np.random.normal(0, 30, len(df)))
    df['energy_demand'] = np.maximum(df['energy_demand'], 300)
    
    solar_base = np.maximum(0, np.sin(np.pi * (df['hour'] - 6) / 13)) * 400
    solar_cloud_cover = np.random.uniform(0.6, 1.0, len(df))
    df['solar_output'] = solar_base * solar_cloud_cover
    
    wind_base = 150 + 50 * np.cos(np.pi * df['hour'] / 6)
    df['wind_output'] = np.maximum(0, wind_base + np.random.normal(0, 40, len(df)))
    df['renewable_output'] = df['solar_output'] + df['wind_output']
    
    base_cost = 50
    peak_cost_multiplier = np.where(df['hour'].isin([17, 18, 19, 20, 21]), 1.8, 1.0)
    demand_cost_factor = (df['energy_demand'] / 800) * 20
    df['cost_per_unit'] = (base_cost * peak_cost_multiplier + demand_cost_factor).round(2)
    
    mask = np.random.choice([True, False], size=len(df), p=[0.01, 0.99])
    df.loc[mask, 'temperature'] = np.nan
    return df

def load_kaggle_dataset(filepath="kaggle_smart_grid.csv"):
    if not os.path.exists(filepath):
        from create_kaggle_csv import create_kaggle_csv_sample
        create_kaggle_csv_sample(filepath)
        
    df = pd.read_csv(filepath)
    col_map = {
        'Datetime': 'timestamp',
        'PJM_Load_MW': 'energy_demand',
        'Outdoor_Temp_C': 'temperature',
        'Solar_Gen_MW': 'solar_output',
        'Wind_Gen_MW': 'wind_output',
        'Grid_Tariff_USD': 'cost_per_unit'
    }
    df = df.rename(columns=col_map)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['renewable_output'] = df['solar_output'] + df['wind_output']
    return df

def process_custom_dataset(file_buffer):
    df = pd.read_csv(file_buffer)
    time_cols = [c for c in df.columns if any(k in c.lower() for k in ['time', 'date', 'hour'])]
    if time_cols:
        df['timestamp'] = pd.to_datetime(df[time_cols[0]], errors='coerce')
    else:
        df['timestamp'] = pd.date_range(end=datetime.now(), periods=len(df), freq='H')
        
    df['timestamp'] = df['timestamp'].fillna(pd.date_range(end=datetime.now(), periods=len(df), freq='H'))
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    demand_cols = [c for c in num_cols if any(k in c.lower() for k in ['demand', 'load', 'power', 'mw', 'use', 'energy'])]
    if demand_cols:
        df['energy_demand'] = df[demand_cols[0]]
    elif num_cols:
        df['energy_demand'] = df[num_cols[0]]
    else:
        df['energy_demand'] = np.random.normal(700, 100, len(df))
        
    if 'temperature' not in df.columns:
        df['temperature'] = 22 + 5 * np.sin(np.pi * df['hour'] / 12)
    if 'solar_output' not in df.columns:
        df['solar_output'] = np.maximum(0, np.sin(np.pi * (df['hour'] - 6) / 13)) * 300
    if 'wind_output' not in df.columns:
        df['wind_output'] = np.random.uniform(100, 250, len(df))
    if 'cost_per_unit' not in df.columns:
        df['cost_per_unit'] = np.random.uniform(40, 75, len(df))
        
    df['renewable_output'] = df['solar_output'] + df['wind_output']
    return df

def preprocess_data(df):
    df = df.copy()
    df['temperature'] = df['temperature'].ffill().bfill()
    df['is_peak'] = df['hour'].isin([17, 18, 19, 20, 21]).astype(int)
    df['month'] = df['timestamp'].dt.month
    
    df['demand_lag_1h'] = df['energy_demand'].shift(1)
    df['demand_lag_24h'] = df['energy_demand'].shift(24)
    df['temp_lag_1h'] = df['temperature'].shift(1)
    
    df = df.dropna().reset_index(drop=True)
    return df
