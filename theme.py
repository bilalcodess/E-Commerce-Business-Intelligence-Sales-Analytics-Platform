import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        /* Watery animated background */
        .stApp {
            background: linear-gradient(-45deg, #020617, #1e1b4b, #0c4a6e, #0284c7);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #f1f5f9;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Glassmorphism Cards */
        .metric-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            margin-bottom: 20px;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 50%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0) 100%);
            transform: skewX(-25deg);
            animation: shine 6s infinite;
        }

        @keyframes shine {
            0% { left: -100%; }
            20% { left: 200%; }
            100% { left: 200%; }
        }

        .metric-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 15px 40px 0 rgba(2, 132, 199, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.08);
        }

        .metric-title {
            color: #94a3b8;
            font-size: 14px;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }

        .metric-value {
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 38px;
            font-weight: 800;
        }
        
        /* Make standard Streamlit widgets dark/glassy */
        div[data-testid="stHeader"] {
            background-color: transparent;
        }

        /* Sidebar Styling to match the theme */
        section[data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.4) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        /* Target the inner container of the sidebar to make it transparent */
        section[data-testid="stSidebar"] > div {
            background-color: transparent !important;
        }

        [data-testid="stSidebarNav"] {
            background-color: transparent !important;
        }

        [data-testid="stSidebarNav"] * {
            background-color: transparent !important;
        }

        [data-testid="stSidebarNav"] a {
            color: #cbd5e1 !important;
            border-radius: 12px !important;
            transition: all 0.3s ease;
        }

        [data-testid="stSidebarNav"] a:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #ffffff !important;
        }
        
        [data-testid="stSidebarNav"] span {
            color: #cbd5e1 !important;
            font-weight: 400 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def apply_plotly_theme(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
