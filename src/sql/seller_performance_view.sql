CREATE VIEW IF NOT EXISTS seller_performance_view AS
SELECT 
    s.seller_id,
    s.seller_state,
    COUNT(DISTINCT i.order_id) AS total_orders,
    SUM(i.price) AS total_revenue,
    AVG(r.review_score) AS avg_review_score
FROM sellers s
JOIN order_items i ON s.seller_id = i.seller_id
LEFT JOIN order_reviews r ON i.order_id = r.order_id
GROUP BY s.seller_id, s.seller_state;
