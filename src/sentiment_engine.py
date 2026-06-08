import pandas as pd
import sqlite3
import os
import logging
from textblob import TextBlob
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def analyze_sentiment(text):
    if not text:
        return 0.0, 'Neutral'
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return polarity, 'Positive'
    elif polarity < -0.1:
        return polarity, 'Negative'
    else:
        return polarity, 'Neutral'

def run_sentiment_analysis():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    
    if not os.path.exists(db_path):
        logging.error(f"Database not found at {db_path}")
        return

    logging.info("Loading reviews from database...")
    query = """
    SELECT 
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message
    FROM order_reviews
    WHERE review_comment_message IS NOT NULL OR review_comment_title IS NOT NULL
    """
    
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)
        
    logging.info(f"Processing {len(df)} reviews...")
    
    # Combine title and message
    df['full_review'] = df['review_comment_title'].fillna('') + ' ' + df['review_comment_message'].fillna('')
    df['cleaned_review'] = df['full_review'].apply(clean_text)
    
    # Apply sentiment
    sentiment_results = df['cleaned_review'].apply(analyze_sentiment)
    df['sentiment_score'] = [res[0] for res in sentiment_results]
    df['sentiment_label'] = [res[1] for res in sentiment_results]
    
    logging.info("Saving sentiment results to database...")
    
    results_df = df[['review_id', 'order_id', 'review_score', 'sentiment_score', 'sentiment_label', 'cleaned_review']]
    
    with sqlite3.connect(db_path) as conn:
        results_df.to_sql('review_sentiment', conn, if_exists='replace', index=False)
        
    logging.info("Sentiment analysis completed.")

if __name__ == '__main__':
    run_sentiment_analysis()
