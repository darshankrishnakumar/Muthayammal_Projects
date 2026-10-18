-- ====================================================================
-- DATABASE MIGRATION SCRIPT: TELECOM CHURN PREDICTION RELATIONAL SCHEMA
-- Database Engine: MySQL 8.0+ / MariaDB 10.11+
-- Character Set: utf8mb4 / Unicode
-- ====================================================================

CREATE DATABASE IF NOT EXISTS telecom_churn 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE telecom_churn;

-- Drop dependent tables if re-creating
DROP TABLE IF EXISTS prediction_history;
DROP TABLE IF EXISTS billing_accounts;
DROP TABLE IF EXISTS customer_services;
DROP TABLE IF EXISTS customers;

-- 1. Core Customers Demographic Table
CREATE TABLE customers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(64) NOT NULL UNIQUE,
    gender VARCHAR(10) NOT NULL,
    senior_citizen TINYINT NOT NULL DEFAULT 0,
    partner VARCHAR(10) NOT NULL,
    dependents VARCHAR(10) NOT NULL,
    tenure INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_code (customer_code),
    INDEX idx_tenure (tenure),
    CONSTRAINT chk_gender CHECK (gender IN ('Male', 'Female', 'Other')),
    CONSTRAINT chk_senior CHECK (senior_citizen IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Customer Subscribed Telecom & Digital Services
CREATE TABLE customer_services (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    phone_service VARCHAR(10) NOT NULL,
    multiple_lines VARCHAR(30) NOT NULL,
    internet_service VARCHAR(30) NOT NULL,
    online_security VARCHAR(30) NOT NULL,
    online_backup VARCHAR(30) NOT NULL,
    device_protection VARCHAR(30) NOT NULL,
    tech_support VARCHAR(30) NOT NULL,
    streaming_tv VARCHAR(30) NOT NULL,
    streaming_movies VARCHAR(30) NOT NULL,
    CONSTRAINT fk_services_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_services_internet (internet_service)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Billing & Contract Account Information
CREATE TABLE billing_accounts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    contract_type VARCHAR(30) NOT NULL,
    paperless_billing VARCHAR(10) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    monthly_charges DECIMAL(10, 2) NOT NULL,
    total_charges DECIMAL(12, 2) NOT NULL,
    CONSTRAINT fk_billing_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_contract_type (contract_type),
    INDEX idx_monthly_charges (monthly_charges)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Audit Trail of Historical Machine Learning Predictions
CREATE TABLE prediction_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NULL,
    customer_code VARCHAR(64) NULL,
    timestamp DATETIME NOT NULL,
    predicted_class VARCHAR(20) NOT NULL,
    churn_probability DOUBLE NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    recommendation TEXT,
    model_version VARCHAR(50) NOT NULL DEFAULT 'Random Forest',
    
    -- Feature Snapshot for Auditability & Real-Time Querying
    gender VARCHAR(10),
    senior_citizen INT DEFAULT 0,
    partner VARCHAR(10),
    dependents VARCHAR(10),
    tenure INT DEFAULT 0,
    phone_service VARCHAR(10),
    multiple_lines VARCHAR(30),
    internet_service VARCHAR(30),
    online_security VARCHAR(30),
    online_backup VARCHAR(30),
    device_protection VARCHAR(30),
    tech_support VARCHAR(30),
    streaming_tv VARCHAR(30),
    streaming_movies VARCHAR(30),
    contract VARCHAR(30),
    paperless_billing VARCHAR(10),
    payment_method VARCHAR(50),
    monthly_charges DOUBLE,
    total_charges DOUBLE,
    
    INDEX idx_pred_timestamp (timestamp DESC),
    INDEX idx_pred_class (predicted_class),
    INDEX idx_pred_risk (risk_level),
    INDEX idx_pred_contract (contract),
    INDEX idx_pred_internet (internet_service),
    CONSTRAINT chk_pred_class CHECK (predicted_class IN ('Churn', 'No Churn', 'Yes', 'No')),
    CONSTRAINT chk_risk_level CHECK (risk_level IN ('High', 'Medium', 'Low'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
