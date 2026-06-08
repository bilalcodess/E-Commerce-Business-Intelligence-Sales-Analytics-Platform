# E-Commerce Business Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)
![scikit-learn](https://img.shields.io/badge/Machine%20Learning-scikit--learn-orange.svg)
![Plotly](https://img.shields.io/badge/Visualization-Plotly-purple.svg)

🌐 **Live Dashboard**: [https://e-commerce-business-intelligence-sales-analytics-platform-lgt6.streamlit.app/](https://e-commerce-business-intelligence-sales-analytics-platform-lgt6.streamlit.app/)

## 🎯 Business Problem & Context
E-commerce businesses generate massive amounts of data across multiple touchpoints (orders, payments, logistics, reviews). The challenge lies in synthesizing this fragmented data into actionable insights. This project simulates a production-grade Business Intelligence Platform using the Olist Brazilian E-Commerce dataset. 

It aims to provide stakeholders with automated intelligence across 4 key dimensions:
- **Revenue & Growth:** Tracking daily GMV and predicting future demand.
- **Customer Intelligence:** Understanding customer behavior via RFM (Recency, Frequency, Monetary) segmentation.
- **Operational Efficiency:** Pinpointing logistics bottlenecks and underperforming delivery routes.
- **Brand Reputation:** Quantifying product sentiment via NLP.

## 💡 Key Business Insights Found
- **Customer Lifetime Value:** Identified 'Champions' contributing disproportionately to overall GMV ($15.8M Total GMV processed).
- **Logistics Impact:** The worst-performing delivery route (e.g., SP -> MA) demonstrated a high correlation with negative reviews (average star rating dropping below 2.0).
- **Sentiment Correlation:** Over 85% of positive sentiment reviews directly correspond with 4 and 5-star ratings, validating the robustness of the NLP pipeline.
- **Demand Forecasting:** Health & Beauty and Bed Bath & Table consistently demonstrate the strongest revenue growth, with a forecast confidence interval capturing seasonal peaks.

## 🏗️ Data Architecture

```text
[Raw CSVs (7 Files)]
       │
       ▼
(src/build_warehouse.py) ───────> [SQLite Database (ecommerce.db)]
       │                                     │
       ├─ Pandas (ETL)                       ├─ View: daily_revenue_view
       └─ SQLAlchemy                         ├─ View: seller_performance_view
                                             ├─ View: delivery_performance_view
                                             └─ View: product_category_view
                                             
       ┌─────────────────────────────────────┴─────────────────────────────────────┐
       ▼                                     ▼                                     ▼
[RFM Engine]                       [Demand Forecaster]                  [Sentiment Engine]
(scikit-learn K-Means)             (Holt-Winters Smoothing)             (TextBlob NLP)
Calculates LTV & Segments          Predicts 90-day orders               Extracts Review Topics
       │                                     │                                     │
       └─────────────────────────────────────┼─────────────────────────────────────┘
                                             ▼
                                [Streamlit BI Dashboard]
                                (6 Interactive Pages)
```

## 💻 Tech Stack
- **Data Engineering:** Python (Pandas), SQLite, SQLAlchemy
- **Data Science / ML:** Scikit-learn (K-Means Clustering), Statsmodels (Holt-Winters Forecasting), TextBlob (NLP / Sentiment Analysis)
- **Frontend / Visualization:** Streamlit, Plotly Express & Graph Objects
- **Reporting:** Jinja2 (Automated HTML Reports)

## 🚀 3-Step Installation Guide

1. **Clone & Setup Environment**
   ```bash
   git clone https://github.com/yourusername/ecommerce-bi-platform.git
   cd ecommerce-bi-platform
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Build the Data Warehouse & Run Analytical Engines**
   Ensure your 7 Olist CSV files are in the `data/raw/` directory.
   ```bash
   python src/build_warehouse.py
   python src/rfm_engine.py
   python src/forecasting.py
   python src/sentiment_engine.py
   python src/delivery_analyzer.py
   ```

3. **Launch the Dashboard**
   ```bash
   streamlit run app.py
   ```

## 📸 Dashboard Preview

*(Add screenshots of your dashboard here)*

- **Executive Dashboard** (`app.py`): Overview of KPIs and Geo-distribution.
- **Customer Intelligence** (`pages/2_Customer_Intelligence.py`): RFM segments and Cohort analysis.
- **Product & Category** (`pages/3_Product_Category_Analytics.py`): Revenue charts and Demand Forecasting.
- **Seller Performance** (`pages/4_Seller_Performance.py`): Top sellers and At-Risk alerts.
- **Review Sentiment** (`pages/5_Review_Sentiment.py`): NLP Wordclouds and Sentiment Distributions.
- **SQL Explorer** (`pages/6_SQL_Query_Explorer.py`): Interactive technical verification.

---
*Built as a comprehensive demonstration of full-stack data science capabilities.*
