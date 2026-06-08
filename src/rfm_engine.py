import pandas as pd
import sqlite3
import os
import logging
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_rfm_segmentation():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    
    if not os.path.exists(db_path):
        logging.error(f"Database not found at {db_path}")
        return

    logging.info("Loading data for RFM segmentation...")
    # Get all delivered orders and payments
    query = """
    SELECT 
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        p.payment_value
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    """
    
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)
        
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Use max date in dataset as 'today' for Recency
    current_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    # Calculate R, F, M
    rfm = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (current_date - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()
    
    rfm.rename(columns={
        'order_purchase_timestamp': 'Recency',
        'order_id': 'Frequency',
        'payment_value': 'Monetary'
    }, inplace=True)
    
    # Score dimensions 1-5 (5 is best for Frequency/Monetary, 5 is best for Recency, i.e., lowest recency)
    # pd.qcut might fail if bins are not unique, so we handle it with rank
    rfm['R_Score'] = pd.qcut(rfm['Recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    def assign_segment(r, f, m):
        if r >= 4 and f >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal'
        elif r >= 4 and f <= 2:
            return 'New'
        elif r <= 2 and f >= 3:
            return 'At-Risk'
        elif r <= 2 and f <= 2:
            return 'Lost'
        else:
            return 'Potential Loyalists'
            
    rfm['Segment'] = rfm.apply(lambda row: assign_segment(int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])), axis=1)
    
    # K-Means clustering as validation layer
    logging.info("Running K-Means clustering...")
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
    
    kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
    rfm['KMeans_Cluster'] = kmeans.fit_predict(rfm_scaled)
    
    logging.info("Writing customer segments to database...")
    with sqlite3.connect(db_path) as conn:
        rfm.to_sql('customer_segments', conn, if_exists='replace', index=False)
        
    logging.info("RFM segmentation completed successfully.")

if __name__ == '__main__':
    run_rfm_segmentation()
