CREATE VIEW IF NOT EXISTS customer_lifetime_value_view AS
SELECT 
    c.customer_unique_id,
    MIN(DATE(o.order_purchase_timestamp)) AS first_purchase_date,
    MAX(DATE(o.order_purchase_timestamp)) AS last_purchase_date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(p.payment_value) AS total_spent,
    AVG(p.payment_value) AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_payments p ON o.order_id = p.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY c.customer_unique_id;
