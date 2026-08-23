-- Seed initial data for Inventory Management System
USE inventory_db;

-- Initial Categories
INSERT IGNORE INTO categories (id, name, description) VALUES
(1, 'Electronics', 'Gadgets, components, and hardware accessories'),
(2, 'Office Supplies', 'Paper, pens, stationary, and desk items'),
(3, 'Furniture', 'Desks, chairs, cabinets, and office furniture');

-- Initial Suppliers
INSERT IGNORE INTO suppliers (id, name, contact_name, email, phone, address) VALUES
(1, 'TechCorp Supplies', 'Alice Johnson', 'contact@techcorp.com', '+1-555-0192', '100 Innovation Way, Tech City'),
(2, 'Global Office Inc', 'Bob Smith', 'sales@globaloffice.com', '+1-555-0183', '45 Commercial Blvd, Metro City');

-- Initial Passwords:
-- admin / admin123  (Werkzeug generated hash for 'admin123')
-- staff / staff123  (Werkzeug generated hash for 'staff123')
INSERT IGNORE INTO users (id, username, email, password_hash, role) VALUES
(1, 'admin', 'admin@inventory.com', 'scrypt:32768:8:1$u7vL9aN3X$df6c1c8a14cf2c2f9d84cf8f8303d8d64117bb68078c5c56c2d1b7145719bc4522a7f5a7cbcaee1a681c81efcaedc41b8f15d74ffae72365bbab167f401ef6c4', 'admin'),
(2, 'staff', 'staff@inventory.com', 'scrypt:32768:8:1$m9P2kL1W$e3f79a957b98d249f8482d8cbb819d9b62a63ffb30743bdf1d072bfa4e5b958cf19c727d5ab797b5e43c5b5bb96ef61a7a0b58e72ef6d967332c918a51351111', 'staff');

-- Initial Products
INSERT IGNORE INTO products (id, sku, name, category_id, supplier_id, unit, price, quantity, reorder_level) VALUES
(1, 'ELEC-LOGI-MX', 'Logitech MX Master 3S Wireless Mouse', 1, 1, 'pcs', 99.99, 25, 10),
(2, 'ELEC-DELL-U27', 'Dell UltraSharp 27" 4K Monitor', 1, 1, 'pcs', 450.00, 5, 8),
(3, 'OFF-PAPER-A4', 'A4 Printing Paper (Box of 5 Reams)', 2, 2, 'box', 35.50, 40, 15),
(4, 'FURN-ERGO-CHR', 'Ergonomic Executive Mesh Chair', 3, 2, 'pcs', 220.00, 4, 5);

-- Initial Stock Movements
INSERT IGNORE INTO stock_movements (id, product_id, type, quantity, reason, user_id) VALUES
(1, 1, 'IN', 25, 'Initial stock import', 1),
(2, 2, 'IN', 10, 'Initial stock import', 1),
(3, 2, 'OUT', 5, 'Dispatched to Design Dept', 2),
(4, 3, 'IN', 40, 'Initial stock import', 1),
(5, 4, 'IN', 4, 'Initial stock import', 1);

-- Initial Activity Log
INSERT IGNORE INTO activity_log (id, user_id, action, entity_type, entity_id, details) VALUES
(1, 1, 'CREATE', 'USER', 1, 'Admin user account initialized'),
(2, 1, 'CREATE', 'PRODUCT', 1, 'Added product ELEC-LOGI-MX'),
(3, 2, 'STOCK_OUT', 'PRODUCT', 2, 'Deducted 5 units of Dell UltraSharp 27" 4K Monitor');
