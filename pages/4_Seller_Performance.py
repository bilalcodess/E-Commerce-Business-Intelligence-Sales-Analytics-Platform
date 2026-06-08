import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

st.set_page_config(page_title="Seller Performance", page_icon="🏅", layout="wide")
theme.apply_theme()

st.title("🏅 Seller Performance")
st.markdown("Analyze seller rankings, tiers, and identify underperforming sellers.")

@st.cache_data
def load_data(query):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)

# Load seller data
seller_df = load_data("SELECT * FROM seller_performance_view")

if not seller_df.empty:
    # Assign Seller Tiers
    def assign_tier(row):
        if row['total_revenue'] > 10000 and row['avg_review_score'] >= 4.5:
            return 'Platinum'
        elif row['total_revenue'] > 5000 and row['avg_review_score'] >= 4.0:
            return 'Gold'
        elif row['total_revenue'] > 1000 and row['avg_review_score'] >= 3.5:
            return 'Silver'
        elif row['avg_review_score'] < 3.0:
            return 'At-Risk'
        else:
            return 'Bronze'

    seller_df['Tier'] = seller_df.apply(assign_tier, axis=1)

    st.subheader("Seller Leaderboard")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        tier_counts = seller_df['Tier'].value_counts().reset_index()
        tier_counts.columns = ['Tier', 'Count']
        fig = px.pie(tier_counts, values='Count', names='Tier', hole=0.5,
                     title="Seller Tiers", color='Tier',
                     color_discrete_map={'Platinum': '#e5e4e2', 'Gold': '#ffd700', 'Silver': '#c0c0c0', 'Bronze': '#cd7f32', 'At-Risk': '#ff4c4c'})
        fig = theme.apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        top_sellers = seller_df.sort_values('total_revenue', ascending=False).head(10)
        top_sellers['seller_id_short'] = top_sellers['seller_id'].str[:8] + '...'
        fig = px.bar(top_sellers, x='total_revenue', y='seller_id_short', orientation='h',
                     title="Top 10 Sellers by Revenue", color='Tier',
                     color_discrete_map={'Platinum': '#e5e4e2', 'Gold': '#ffd700', 'Silver': '#c0c0c0', 'Bronze': '#cd7f32', 'At-Risk': '#ff4c4c'})
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig = theme.apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    
    st.subheader("⚠️ Underperforming Seller Alert")
    at_risk_sellers = seller_df[seller_df['Tier'] == 'At-Risk'].sort_values('total_revenue', ascending=False)
    st.dataframe(at_risk_sellers[['seller_id', 'seller_state', 'total_orders', 'total_revenue', 'avg_review_score']],
                 use_container_width=True)
