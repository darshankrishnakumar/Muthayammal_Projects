-- ====================================================================
-- Flyway Migration V12: Access Control, Granular Admin Permissions,
-- Data Scoping, Developer Assignment, Notifications & Lifecycle System
-- ====================================================================

-- 1. Admin Granular Permissions Table
CREATE TABLE IF NOT EXISTS admin_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    admin_user_id BIGINT NOT NULL,
    permission_key VARCHAR(100) NOT NULL,
    data_scope VARCHAR(50) NOT NULL DEFAULT 'GLOBAL',
    granted_by VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_admin_perm_user FOREIGN KEY (admin_user_id) REFERENCES user_management(id) ON DELETE CASCADE,
    CONSTRAINT uk_admin_permission_key UNIQUE (admin_user_id, permission_key),
    INDEX idx_admin_perm_lookup (admin_user_id, permission_key, data_scope)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Admin User Scoping (Onboarding/Partner Admin user assignments)
CREATE TABLE IF NOT EXISTS admin_user_assignments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    admin_user_id BIGINT NOT NULL,
    assigned_user_id BIGINT NOT NULL,
    assigned_by VARCHAR(100) NOT NULL,
    notes TEXT,
    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_aua_admin FOREIGN KEY (admin_user_id) REFERENCES user_management(id) ON DELETE CASCADE,
    CONSTRAINT fk_aua_user FOREIGN KEY (assigned_user_id) REFERENCES user_management(id) ON DELETE CASCADE,
    CONSTRAINT uk_admin_user_assign UNIQUE (admin_user_id, assigned_user_id),
    INDEX idx_admin_user_scope (admin_user_id, assigned_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    recipient_email VARCHAR(100) NOT NULL,
    recipient_role VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    link_url VARCHAR(255),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_notifications_recipient (recipient_email, is_read),
    INDEX idx_notifications_role (recipient_role, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Safe Procedure for Conditional Column Additions in MySQL
DROP PROCEDURE IF EXISTS add_column_if_not_exists;

DELIMITER $$
CREATE PROCEDURE add_column_if_not_exists(
    IN tbl_name VARCHAR(64),
    IN col_name VARCHAR(64),
    IN col_definition VARCHAR(255)
)
BEGIN
    DECLARE tbl_count INT;
    DECLARE col_count INT;
    
    SELECT COUNT(*) INTO tbl_count
    FROM information_schema.tables
    WHERE table_schema = DATABASE()
      AND table_name = tbl_name;

    IF tbl_count > 0 THEN
        SELECT COUNT(*) INTO col_count
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = tbl_name
          AND column_name = col_name;

        IF col_count = 0 THEN
            SET @sql = CONCAT('ALTER TABLE `', tbl_name, '` ADD COLUMN `', col_name, '` ', col_definition);
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
        END IF;
    END IF;
END$$
DELIMITER ;

-- Requirements Columns
CALL add_column_if_not_exists('requirements', 'advance_amount', 'DECIMAL(12,2) DEFAULT NULL');
CALL add_column_if_not_exists('requirements', 'remaining_amount', 'DECIMAL(12,2) DEFAULT NULL');
CALL add_column_if_not_exists('requirements', 'advance_payment_status', 'VARCHAR(50) DEFAULT "PENDING"');
CALL add_column_if_not_exists('requirements', 'remaining_payment_status', 'VARCHAR(50) DEFAULT "PENDING"');
CALL add_column_if_not_exists('requirements', 'super_admin_notes', 'TEXT DEFAULT NULL');

-- Projects Columns
CALL add_column_if_not_exists('projects', 'developer_id', 'BIGINT DEFAULT NULL');
CALL add_column_if_not_exists('projects', 'reviewer_admin_id', 'BIGINT DEFAULT NULL');
CALL add_column_if_not_exists('projects', 'advance_amount', 'DECIMAL(12,2) DEFAULT NULL');
CALL add_column_if_not_exists('projects', 'remaining_amount', 'DECIMAL(12,2) DEFAULT NULL');
CALL add_column_if_not_exists('projects', 'advance_payment_status', 'VARCHAR(50) DEFAULT NULL');
CALL add_column_if_not_exists('projects', 'remaining_payment_status', 'VARCHAR(50) DEFAULT NULL');
CALL add_column_if_not_exists('projects', 'lifecycle_status', 'VARCHAR(50) DEFAULT "CREATED"');
CALL add_column_if_not_exists('projects', 'review_notes', 'TEXT DEFAULT NULL');
CALL add_column_if_not_exists('projects', 'change_request_notes', 'TEXT DEFAULT NULL');
CALL add_column_if_not_exists('projects', 'is_marketplace', 'BOOLEAN NOT NULL DEFAULT FALSE');
CALL add_column_if_not_exists('projects', 'purchased_by_user_id', 'BIGINT DEFAULT NULL');

-- Order Management Columns
CALL add_column_if_not_exists('order_management', 'idempotency_key', 'VARCHAR(100) DEFAULT NULL');
CALL add_column_if_not_exists('order_management', 'project_id', 'BIGINT DEFAULT NULL');
CALL add_column_if_not_exists('order_management', 'requirement_id', 'BIGINT DEFAULT NULL');
CALL add_column_if_not_exists('order_management', 'payment_type', 'VARCHAR(50) DEFAULT "FULL"');

-- Clean up helper procedure
DROP PROCEDURE IF EXISTS add_column_if_not_exists;
