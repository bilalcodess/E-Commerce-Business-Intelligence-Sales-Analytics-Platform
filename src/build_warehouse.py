import pandas as pd
import sqlite3
import os
import glob
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_warehouse():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir = os.path.join(base_dir, 'data', 'raw')
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    
    if not os.path.exists(raw_data_dir):
        logging.error(f"Raw data directory not found at {raw_data_dir}")
        return

    # Create data directory if not exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}')
    
    files_to_load = {
        'olist_customers_dataset.csv': 'customers',
        'olist_order_items_dataset.csv': 'order_items',
        'olist_order_payments_dataset.csv': 'order_payments',
        'olist_order_reviews_dataset.csv': 'order_reviews',
        'olist_orders_dataset.csv': 'orders',
        'olist_products_dataset.csv': 'products',
        'olist_sellers_dataset.csv': 'sellers',
        'product_category_name_translation.csv': 'product_category_name_translation'
    }
    
    logging.info("Loading CSV files into SQLite database...")
    for filename, table_name in files_to_load.items():
        file_path = os.path.join(raw_data_dir, filename)
        if os.path.exists(file_path):
            logging.info(f"Loading {filename} into table {table_name}...")
            # We can use read_csv directly
            # For large files chunking might be needed, but Olist is small enough for pandas
            df = pd.read_csv(file_path)
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        else:
            logging.warning(f"File {filename} not found.")
            
    logging.info("Applying SQL views...")
    sql_dir = os.path.join(base_dir, 'src', 'sql')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for sql_file in glob.glob(os.path.join(sql_dir, '*.sql')):
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                logging.info(f"Executing {os.path.basename(sql_file)}...")
                try:
                    cursor.executescript(sql_script)
                except Exception as e:
                    logging.error(f"Error executing {sql_file}: {e}")
                    
    logging.info("Data Warehouse build complete.")

if __name__ == '__main__':
    build_warehouse()
