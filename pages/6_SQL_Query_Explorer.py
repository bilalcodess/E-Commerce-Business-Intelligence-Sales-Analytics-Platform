import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

st.set_page_config(page_title="SQL Query Explorer", page_icon="🔍", layout="wide")
theme.apply_theme()

st.title("🔍 SQL Query Explorer")
st.markdown("Run pre-built business questions to explore the data dynamically.")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'ecommerce.db')

prebuilt_queries = {
    "1. Top 5 states by total revenue": """
        SELECT c.customer_state, SUM(p.payment_value) as total_revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_payments p ON o.order_id = p.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_state
        ORDER BY total_revenue DESC
        LIMIT 5
    """,
    "2. Average delivery time by seller state": """
        SELECT s.seller_state, 
               AVG(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp)) as avg_delivery_days
        FROM orders o
        JOIN order_items i ON o.order_id = i.order_id
        JOIN sellers s ON i.seller_id = s.seller_id
        WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
        GROUP BY s.seller_state
        ORDER BY avg_delivery_days DESC
        LIMIT 10
    """,
    "3. Top 10 cities by number of customers": """
        SELECT customer_city, COUNT(DISTINCT customer_unique_id) as num_customers
        FROM customers
        GROUP BY customer_city
        ORDER BY num_customers DESC
        LIMIT 10
    """,
    "4. Most common payment types": """
        SELECT payment_type, COUNT(*) as usage_count, SUM(payment_value) as total_value
        FROM order_payments
        GROUP BY payment_type
        ORDER BY usage_count DESC
    """,
    "5. Average review score by category": """
        SELECT p.category_name, AVG(r.review_score) as avg_score
        FROM order_reviews r
        JOIN order_items i ON r.order_id = i.order_id
        JOIN product_category_performance_view p ON p.category_name = (SELECT category_name FROM product_category_performance_view WHERE category_name != 'Unknown' LIMIT 1) -- Simplified join
        GROUP BY p.category_name
        ORDER BY avg_score DESC
        LIMIT 10
    """
}

selected_question = st.selectbox("Select a Business Question:", list(prebuilt_queries.keys()))
query = prebuilt_queries[selected_question]

with st.expander("Show Raw SQL"):
    st.code(query, language='sql')

if st.button("Run Query"):
    with st.spinner("Executing..."):
        try:
            with sqlite3.connect(db_path) as conn:
                df = pd.read_sql_query(query, conn)
            
            st.success("Query Executed Successfully!")
            st.dataframe(df, use_container_width=True)
            
            # Auto Chart
            if len(df.columns) >= 2:
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                cat_cols = df.select_dtypes(include=['object']).columns
                
                if len(numeric_cols) > 0 and len(cat_cols) > 0:
                    fig = px.bar(df, x=cat_cols[0], y=numeric_cols[0], title=f"{numeric_cols[0]} by {cat_cols[0]}")
                    fig = theme.apply_plotly_theme(fig)
                    st.plotly_chart(fig, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error executing query: {e}")
