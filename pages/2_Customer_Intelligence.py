import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

st.set_page_config(page_title="Customer Intelligence", page_icon="👥", layout="wide")
theme.apply_theme()

st.title("👥 Customer Intelligence")
st.markdown("Analyze customer segments, lifetime value, and retention.")

@st.cache_data
def load_data(query):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)

st.subheader("RFM Segmentation")

rfm_df = load_data("SELECT * FROM customer_segments")

if not rfm_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        segment_counts = rfm_df['Segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']
        fig = px.pie(segment_counts, values='Count', names='Segment', hole=0.4, 
                     title="Customer Segments Distribution",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig = theme.apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        segment_revenue = rfm_df.groupby('Segment')['Monetary'].mean().reset_index()
        fig = px.bar(segment_revenue, x='Monetary', y='Segment', orientation='h',
                     title="Average Revenue by Segment",
                     color='Monetary', color_continuous_scale='Viridis')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig = theme.apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Customer Lifetime Value (LTV)")
ltv_df = load_data("SELECT * FROM customer_lifetime_value_view LIMIT 1000") # Limit for scatter plot

if not ltv_df.empty:
    fig = px.scatter(ltv_df, x='total_orders', y='total_spent', size='avg_order_value',
                     color='total_orders', hover_data=['customer_unique_id'],
                     title="LTV Distribution (Sample of 1000 customers)",
                     labels={'total_orders': 'Total Orders', 'total_spent': 'Total Spent ($)'})
    fig = theme.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
