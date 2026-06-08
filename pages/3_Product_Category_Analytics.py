import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

st.set_page_config(page_title="Product & Category Analytics", page_icon="📦", layout="wide")
theme.apply_theme()

st.title("📦 Product & Category Analytics")
st.markdown("Analyze category performance and demand forecasts.")

@st.cache_data
def load_data(query):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)

st.subheader("Category Performance Scatter")

cat_df = load_data("SELECT * FROM product_category_performance_view WHERE category_name != 'Unknown'")

if not cat_df.empty:
    fig = px.scatter(cat_df, x='total_quantity_sold', y='total_revenue', 
                     size='total_orders', color='category_name',
                     hover_name='category_name', log_x=True, log_y=True,
                     title="Revenue vs Volume by Category (Log Scale)",
                     labels={'total_quantity_sold': 'Quantity Sold', 'total_revenue': 'Total Revenue ($)'})
    fig = theme.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Top 20 Products by Revenue")

top_products_query = """
SELECT 
    p.product_id,
    COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category,
    SUM(i.price) as revenue,
    COUNT(i.order_id) as orders
FROM products p
JOIN order_items i ON p.product_id = i.product_id
LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
GROUP BY p.product_id, category
ORDER BY revenue DESC LIMIT 20
"""

top_products = load_data(top_products_query)
if not top_products.empty:
    top_products['product_id_short'] = top_products['product_id'].str[:8] + '...'
    fig = px.bar(top_products, x='revenue', y='product_id_short', orientation='h',
                 color='category', title="Top 20 Products",
                 hover_data=['product_id', 'orders', 'revenue'])
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    fig = theme.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Demand Forecast (Next 90 Days)")

forecast_df = load_data("SELECT * FROM demand_forecast")
if not forecast_df.empty:
    forecast_df['forecast_date'] = pd.to_datetime(forecast_df['forecast_date'])
    
    fig = go.Figure()
    
    # Historical data could be added here, but we just show the forecast and its interval
    fig.add_trace(go.Scatter(
        x=forecast_df['forecast_date'], y=forecast_df['predicted_orders'],
        mode='lines', name='Predicted Orders', line=dict(color='rgb(31, 119, 180)')
    ))
    
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_df['forecast_date'], forecast_df['forecast_date'][::-1]]),
        y=pd.concat([forecast_df['confidence_upper'], forecast_df['confidence_lower'][::-1]]),
        fill='toself', fillcolor='rgba(31, 119, 180, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence Interval',
        showlegend=True
    ))
    
    fig.update_layout(title="Predicted Daily Orders", xaxis_title="Date", yaxis_title="Orders")
    fig = theme.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
