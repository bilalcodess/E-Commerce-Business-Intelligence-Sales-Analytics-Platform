import pandas as pd
import sqlite3
import os
import logging
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_demand_forecasting():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    
    if not os.path.exists(db_path):
        logging.error(f"Database not found at {db_path}")
        return

    logging.info("Loading daily revenue data for forecasting...")
    query = """
    SELECT 
        DATE(o.order_purchase_timestamp) as ds,
        COUNT(DISTINCT o.order_id) as y
    FROM orders o
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY ds
    ORDER BY ds
    """
    
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)
        
    df['ds'] = pd.to_datetime(df['ds'])
    
    # We will forecast total orders for the next 90 days.
    # Set 'ds' as index and resample to daily frequency to ensure no missing dates
    df.set_index('ds', inplace=True)
    df = df.resample('D').sum().fillna(0)
    
    logging.info("Building Holt-Winters Exponential Smoothing model for total orders...")
    # Add an offset to avoid 0s in multiplicative models or use additive
    model = ExponentialSmoothing(df['y'], trend='add', seasonal='add', seasonal_periods=7, initialization_method="estimated")
    fit_model = model.fit()
    
    forecast = fit_model.forecast(90)
    
    # Create forecast dataframe
    last_date = df.index[-1]
    forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=90, freq='D')
    
    # Approximate confidence intervals (statsmodels HW doesn't give them out of the box easily, so we estimate)
    # Using RMSE of residuals
    residuals = fit_model.resid
    rmse = np.sqrt(np.mean(residuals**2))
    
    forecast_df = pd.DataFrame({
        'forecast_date': forecast_dates,
        'predicted_orders': forecast.values,
        'confidence_lower': np.maximum(0, forecast.values - 1.96 * rmse),
        'confidence_upper': forecast.values + 1.96 * rmse
    })
    
    forecast_df['forecast_date'] = forecast_df['forecast_date'].dt.strftime('%Y-%m-%d')
    
    with sqlite3.connect(db_path) as conn:
        forecast_df.to_sql('demand_forecast', conn, if_exists='replace', index=False)
        
    logging.info("Demand forecasting completed and saved to database.")

if __name__ == '__main__':
    run_demand_forecasting()
