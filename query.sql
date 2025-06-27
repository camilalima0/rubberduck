SELECT quantity FROM orderItem oi 
JOIN orderr o 
ON oi.orderId = o.orderId 
JOIN user u 
ON o.userId = u.userId 
WHERE u.email = 'duck@duck.com';   
