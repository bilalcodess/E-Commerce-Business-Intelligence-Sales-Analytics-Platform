CREATE VIEW IF NOT EXISTS delivery_performance_view AS
SELECT 
    o.order_id,
    c.customer_state,
    DATE(o.order_purchase_timestamp) AS purchase_date,
    DATE(o.order_delivered_customer_date) AS delivery_date,
    DATE(o.order_estimated_delivery_date) AS estimated_date,
    JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp) AS actual_delivery_days,
    JULIANDAY(o.order_estimated_delivery_date) - JULIANDAY(o.order_purchase_timestamp) AS estimated_delivery_days,
    CASE 
        WHEN DATE(o.order_delivered_customer_date) > DATE(o.order_estimated_delivery_date) THEN 1 
        ELSE 0 
    END AS is_late
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL;
