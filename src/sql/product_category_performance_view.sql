CREATE VIEW IF NOT EXISTS product_category_performance_view AS
SELECT 
    COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category_name,
    COUNT(DISTINCT i.order_id) AS total_orders,
    SUM(i.price) AS total_revenue,
    COUNT(i.product_id) AS total_quantity_sold
FROM products p
JOIN order_items i ON p.product_id = i.product_id
LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
GROUP BY category_name;
