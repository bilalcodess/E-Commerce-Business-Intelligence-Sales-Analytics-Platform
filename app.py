import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os
import theme

st.set_page_config(page_title="E-Commerce BI Platform", page_icon="📈", layout="wide")

# Apply centralized theme
theme.apply_theme()

@st.cache_data
def load_data(query):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)

st.title("📊 Executive Dashboard")
st.markdown("Overview of key business metrics and geographical distribution of orders.")

# Load KPIs
kpi_query = """
SELECT 
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT c.customer_unique_id) as total_customers,
    SUM(p.payment_value) as total_gmv,
    SUM(p.payment_value) / COUNT(DISTINCT o.order_id) as avg_order_value
FROM orders o
JOIN order_payments p ON o.order_id = p.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
"""
kpi_df = load_data(kpi_query)

# Display KPI Cards
if not kpi_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total GMV</div><div class="metric-value">${kpi_df["total_gmv"].iloc[0]:,.2f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Orders</div><div class="metric-value">{kpi_df["total_orders"].iloc[0]:,}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Customers</div><div class="metric-value">{kpi_df["total_customers"].iloc[0]:,}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Order Value</div><div class="metric-value">${kpi_df["avg_order_value"].iloc[0]:,.2f}</div></div>', unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Revenue Trend (Monthly)")
    trend_df = load_data("""
        SELECT strftime('%Y-%m', order_date) as month, SUM(total_revenue) as revenue
        FROM daily_revenue_view
        GROUP BY month
        ORDER BY month
    """)
    if not trend_df.empty:
        fig = px.line(trend_df, x='month', y='revenue', markers=True, 
                      line_shape='spline', color_discrete_sequence=['#38bdf8'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                          font=dict(color='#e2e8f0'),
                          margin=dict(l=20, r=20, t=20, b=20),
                          xaxis_title="Month", yaxis_title="Revenue ($)")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Categories")
    cat_df = load_data("""
        SELECT category_name, total_revenue 
        FROM product_category_performance_view 
        ORDER BY total_revenue DESC LIMIT 10
    """)
    if not cat_df.empty:
        fig = px.bar(cat_df, x='total_revenue', y='category_name', orientation='h',
                     color='total_revenue', color_continuous_scale='Blues')
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, 
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='#e2e8f0'),
                          margin=dict(l=20, r=20, t=20, b=20),
                          xaxis_title="Revenue ($)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("🗺️ Geographic Heatmap (State-wise Orders)")

geo_df = load_data("""
    SELECT c.customer_state as state, COUNT(o.order_id) as orders
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY state
""")
if not geo_df.empty:
    fig = px.treemap(geo_df, path=['state'], values='orders',
                     color='orders', color_continuous_scale='Mint',
                     title="Order Distribution by State")
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20),
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#e2e8f0'))
    st.plotly_chart(fig, use_container_width=True)
