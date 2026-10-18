-- Project 19: Stock Management System (Enterprise Edition)
-- Database: stock_management_db

CREATE DATABASE IF NOT EXISTS stock_management_db;
USE stock_management_db;

-- 1. Categories
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Products Catalog
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    price FLOAT NOT NULL,
    cost_price FLOAT DEFAULT 0.0,
    quantity INT DEFAULT 0,
    min_stock INT DEFAULT 10,
    reorder_point INT DEFAULT 15,
    lead_time_days INT DEFAULT 3,
    category_id INT,
    description TEXT,
    barcode VARCHAR(50) UNIQUE,
    rfid_tag VARCHAR(50) UNIQUE,
    location_aisle VARCHAR(50) DEFAULT 'Aisle A-01',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- 3. Suppliers & Vendors
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(50),
    address VARCHAR(255),
    lead_time_days INT DEFAULT 5,
    rating FLOAT DEFAULT 4.8,
    payment_terms VARCHAR(50) DEFAULT 'Net 30',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Purchase Orders
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    po_number VARCHAR(50) NOT NULL UNIQUE,
    supplier_id INT NOT NULL,
    total_amount FLOAT DEFAULT 0.0,
    status VARCHAR(30) DEFAULT 'ORDERED',
    ordered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    expected_delivery_date DATETIME,
    received_date DATETIME,
    notes TEXT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);

-- 5. Purchase Order Line Items
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    po_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity_ordered INT NOT NULL,
    unit_cost FLOAT NOT NULL,
    total_cost FLOAT NOT NULL,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 6. Large Cargo Shipments
CREATE TABLE IF NOT EXISTS shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_number VARCHAR(80) NOT NULL UNIQUE,
    po_id INT,
    carrier VARCHAR(80) DEFAULT 'BlueDart Cargo Express',
    origin VARCHAR(100),
    destination VARCHAR(100),
    current_location VARCHAR(100),
    status VARCHAR(30) DEFAULT 'IN_TRANSIT',
    estimated_delivery DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id) ON DELETE SET NULL
);

-- 7. Sales Ledger
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity_sold INT NOT NULL,
    unit_price FLOAT NOT NULL,
    total_amount FLOAT NOT NULL,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    customer_name VARCHAR(100) DEFAULT 'Walk-in Retail',
    payment_method VARCHAR(50) DEFAULT 'UPI / Electronic',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 8. Stock Movements & Audit Trail
CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    movement_type VARCHAR(20) NOT NULL COMMENT 'IN, OUT, AUDIT_ADJUSTMENT',
    quantity INT NOT NULL,
    reason VARCHAR(200),
    device_source VARCHAR(100) DEFAULT 'ERP Terminal',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 9. IoT Devices & Hardware Sensors
CREATE TABLE IF NOT EXISTS iot_devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL UNIQUE,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'ONLINE',
    battery_level INT DEFAULT 95,
    ip_address VARCHAR(50),
    location_area VARCHAR(100),
    last_ping DATETIME DEFAULT CURRENT_TIMESTAMP
);
