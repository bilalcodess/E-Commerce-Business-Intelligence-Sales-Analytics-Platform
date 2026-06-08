CREATE VIEW IF NOT EXISTS daily_revenue_view AS
SELECT 
    DATE(o.order_purchase_timestamp) AS order_date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(p.payment_value) AS total_revenue
FROM orders o
JOIN order_payments p ON o.order_id = p.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY DATE(o.order_purchase_timestamp);
