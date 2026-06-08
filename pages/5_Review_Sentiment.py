import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

st.set_page_config(page_title="Review & Sentiment Analysis", page_icon="💬", layout="wide")
theme.apply_theme()

st.title("💬 Review & Sentiment Analysis")
st.markdown("Analyze customer sentiment and topics based on reviews.")

@st.cache_data
def load_data(query):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)

st.subheader("Sentiment Distribution")

sentiment_df = load_data("SELECT sentiment_label, COUNT(*) as count FROM review_sentiment GROUP BY sentiment_label")

if not sentiment_df.empty:
    fig = px.bar(sentiment_df, x='sentiment_label', y='count', color='sentiment_label',
                 title="Count of Reviews by Sentiment",
                 color_discrete_map={'Positive': '#2ca02c', 'Neutral': '#7f7f7f', 'Negative': '#d62728'})
    fig = theme.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Word Clouds")

col1, col2 = st.columns(2)

@st.cache_data
def generate_wordcloud(sentiment):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(f"SELECT cleaned_review FROM review_sentiment WHERE sentiment_label = '{sentiment}' LIMIT 5000", conn)
    text = " ".join(review for review in df['cleaned_review'].dropna())
    
    if not text.strip():
        text = "No Data"
        
    wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="viridis" if sentiment=="Positive" else "inferno").generate(text)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    # Make plot background transparent for the glassy theme
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    return fig

with col1:
    st.markdown("**Positive Reviews**")
    st.pyplot(generate_wordcloud('Positive'))

with col2:
    st.markdown("**Negative Reviews**")
    st.pyplot(generate_wordcloud('Negative'))

st.markdown("---")

st.subheader("Star Rating vs Sentiment")
scatter_df = load_data("SELECT review_score, sentiment_score FROM review_sentiment LIMIT 5000")

if not scatter_df.empty:
    fig = px.box(scatter_df, x='review_score', y='sentiment_score', 
                 title="Sentiment Score Distribution by Star Rating",
                 labels={'review_score': 'Star Rating', 'sentiment_score': 'Sentiment Polarity'},
                 color='review_score', color_discrete_sequence=px.colors.sequential.Plasma)
    fig = theme.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
