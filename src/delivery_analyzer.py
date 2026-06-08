import pandas as pd
import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_delivery_analysis():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    
    if not os.path.exists(db_path):
        logging.error(f"Database not found at {db_path}")
        return

    logging.info("Analyzing delivery performance...")
    query = """
    SELECT 
        o.order_id,
        c.customer_state,
        s.seller_state,
        p.product_category_name_english AS category_name,
        o.order_purchase_timestamp,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        r.review_score
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items i ON o.order_id = i.order_id
    JOIN sellers s ON i.seller_id = s.seller_id
    JOIN products pr ON i.product_id = pr.product_id
    LEFT JOIN product_category_name_translation p ON pr.product_category_name = p.product_category_name
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
    """
    
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)
        
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Calculate actual vs estimated
    df['is_late'] = (df['order_delivered_customer_date'] > df['order_estimated_delivery_date']).astype(int)
    df['delivery_time_days'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    
    # Top 20 worst routes (seller_state -> customer_state)
    df['route'] = df['seller_state'] + ' -> ' + df['customer_state']
    route_stats = df.groupby('route').agg({
        'order_id': 'count',
        'is_late': 'mean'
    }).reset_index()
    
    # Filter routes with at least 50 orders
    route_stats = route_stats[route_stats['order_id'] >= 50]
    worst_routes = route_stats.sort_values('is_late', ascending=False).head(20)
    
    # Impact on review score
    late_impact = df.groupby('is_late')['review_score'].mean().reset_index()
    
    # Save insights to database
    with sqlite3.connect(db_path) as conn:
        worst_routes.to_sql('worst_delivery_routes', conn, if_exists='replace', index=False)
        late_impact.to_sql('late_delivery_impact', conn, if_exists='replace', index=False)
        
    logging.info("Delivery analysis completed.")

if __name__ == '__main__':
    run_delivery_analysis()
