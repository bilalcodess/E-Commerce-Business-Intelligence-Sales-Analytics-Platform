import sqlite3
import pandas as pd
import os
from datetime import datetime
from jinja2 import Template

def generate_weekly_report():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'ecommerce.db')
    reports_dir = os.path.join(base_dir, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    with sqlite3.connect(db_path) as conn:
        # Total KPIs
        kpi_df = pd.read_sql_query("""
            SELECT 
                COUNT(DISTINCT o.order_id) as total_orders,
                SUM(p.payment_value) as total_gmv
            FROM orders o
            JOIN order_payments p ON o.order_id = p.order_id
            WHERE o.order_status NOT IN ('canceled', 'unavailable')
        """, conn)
        
        # Best seller
        best_seller = pd.read_sql_query("""
            SELECT seller_id, total_revenue 
            FROM seller_performance_view 
            ORDER BY total_revenue DESC LIMIT 1
        """, conn)
        
        # Worst delivery route
        worst_route = pd.read_sql_query("""
            SELECT route, is_late 
            FROM worst_delivery_routes 
            ORDER BY is_late DESC LIMIT 1
        """, conn)
        
        # Top category
        top_cat = pd.read_sql_query("""
            SELECT category_name, total_revenue 
            FROM product_category_performance_view 
            WHERE category_name != 'Unknown' 
            ORDER BY total_revenue DESC LIMIT 1
        """, conn)

    html_template = """
    <html>
    <head>
        <title>Weekly Business Summary</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f9f9f9; color: #333; }
            .container { width: 80%; margin: 40px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
            h1 { color: #1e3a8a; }
            .kpi-board { display: flex; justify-content: space-between; margin-bottom: 30px; }
            .kpi-card { background: #eff6ff; padding: 20px; border-radius: 8px; width: 45%; text-align: center; }
            .kpi-value { font-size: 24px; font-weight: bold; color: #1e3a8a; }
            .highlight { color: #d97706; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Weekly Business Summary - {{ date }}</h1>
            <div class="kpi-board">
                <div class="kpi-card">
                    <div>Total Orders</div>
                    <div class="kpi-value">{{ total_orders }}</div>
                </div>
                <div class="kpi-card">
                    <div>Total GMV</div>
                    <div class="kpi-value">${{ total_gmv }}</div>
                </div>
            </div>
            
            <h2>Key Highlights</h2>
            <ul>
                <li>🏆 <strong>Best Seller:</strong> {{ best_seller }} with a total revenue of <span class="highlight">${{ best_seller_rev }}</span>.</li>
                <li>🚀 <strong>Top Category:</strong> {{ top_cat }} leading with <span class="highlight">${{ top_cat_rev }}</span> in revenue.</li>
                <li>⚠️ <strong>Delivery Alert:</strong> The route <strong>{{ worst_route }}</strong> has a late delivery rate of <span class="highlight">{{ worst_route_rate }}%</span>. Immediate attention recommended.</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    template = Template(html_template)
    html_content = template.render(
        date=datetime.now().strftime("%Y-%m-%d"),
        total_orders=f"{kpi_df['total_orders'].iloc[0]:,}",
        total_gmv=f"{kpi_df['total_gmv'].iloc[0]:,.2f}",
        best_seller=best_seller['seller_id'].iloc[0][:8]+'...',
        best_seller_rev=f"{best_seller['total_revenue'].iloc[0]:,.2f}",
        top_cat=top_cat['category_name'].iloc[0],
        top_cat_rev=f"{top_cat['total_revenue'].iloc[0]:,.2f}",
        worst_route=worst_route['route'].iloc[0] if not worst_route.empty else "N/A",
        worst_route_rate=f"{worst_route['is_late'].iloc[0]*100:.1f}" if not worst_route.empty else "0.0"
    )
    
    report_file = os.path.join(reports_dir, f"weekly_summary_{datetime.now().strftime('%Y%m%d')}.html")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Weekly report generated successfully at {report_file}")

if __name__ == '__main__':
    generate_weekly_report()
