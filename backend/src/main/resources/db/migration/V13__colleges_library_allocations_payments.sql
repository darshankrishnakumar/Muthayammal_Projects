-- ====================================================================
-- Flyway Migration V13: Multi-college distribution platform
--   * colleges and college membership for admins/students
--   * central project library metadata (one copy of every project)
--   * college -> project allocations (no file duplication)
--   * per-user project entitlements (replaces single purchased_by_user_id)
--   * payment transactions with an explicit simulated flag
--   * status history timeline
-- Written to be safe on databases that were partly built by Hibernate ddl-auto.
-- ====================================================================

-- order_management was historically created by Hibernate only; make fresh installs complete.
CREATE TABLE IF NOT EXISTS order_management (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    item_description TEXT,
    amount DOUBLE NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    fulfillment_details TEXT,
    idempotency_key VARCHAR(100) UNIQUE,
    project_id BIGINT,
    requirement_id BIGINT,
    payment_type VARCHAR(50) DEFAULT 'FULL',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL,
    CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES user_management(id),
    INDEX idx_order_user (user_id),
    INDEX idx_order_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS colleges (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(30) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    contact_email VARCHAR(150),
    contact_phone VARCHAR(30),
    address TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by VARCHAR(150),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL,
    CONSTRAINT uk_college_code UNIQUE (code),
    INDEX idx_college_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP PROCEDURE IF EXISTS v13_add_column;
DELIMITER $$
CREATE PROCEDURE v13_add_column(IN tbl VARCHAR(64), IN col VARCHAR(64), IN def VARCHAR(255))
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = tbl)
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = tbl AND column_name = col) THEN
        SET @ddl = CONCAT('ALTER TABLE `', tbl, '` ADD COLUMN `', col, '` ', def);
        PREPARE stmt FROM @ddl;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS v13_add_index;
DELIMITER $$
CREATE PROCEDURE v13_add_index(IN tbl VARCHAR(64), IN idx VARCHAR(64), IN cols VARCHAR(255))
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = tbl)
       AND NOT EXISTS (SELECT 1 FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = tbl AND index_name = idx) THEN
        SET @ddl = CONCAT('CREATE INDEX `', idx, '` ON `', tbl, '` (', cols, ')');
        PREPARE stmt FROM @ddl;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

-- College membership
CALL v13_add_column('user_management', 'college_id', 'BIGINT NULL');
CALL v13_add_index('user_management', 'idx_user_college', 'college_id');

-- Library metadata on projects
CALL v13_add_column('projects', 'project_type', 'VARCHAR(20) NOT NULL DEFAULT ''CUSTOM''');
CALL v13_add_column('projects', 'catalog_status', 'VARCHAR(20) NOT NULL DEFAULT ''DRAFT''');
CALL v13_add_column('projects', 'abstract_text', 'TEXT NULL');
CALL v13_add_column('projects', 'domain', 'VARCHAR(100) NULL');
CALL v13_add_column('projects', 'tags', 'VARCHAR(500) NULL');
CALL v13_add_column('projects', 'price', 'DECIMAL(12,2) NULL');
CALL v13_add_column('projects', 'installation_instructions', 'TEXT NULL');
CALL v13_add_column('projects', 'source_ref', 'VARCHAR(255) NULL');
CALL v13_add_column('projects', 'developer_accepted_at', 'DATETIME NULL');
CALL v13_add_column('projects', 'progress_percent', 'INT NOT NULL DEFAULT 0');
CALL v13_add_index('projects', 'idx_project_type_catalog', 'project_type, catalog_status');
CALL v13_add_index('projects', 'idx_project_source_ref', 'source_ref');
CALL v13_add_index('projects', 'idx_project_developer', 'developer_id');

-- File categories and preview flag
CALL v13_add_column('asset_master', 'category', 'VARCHAR(30) NOT NULL DEFAULT ''OTHER''');
CALL v13_add_column('asset_master', 'previewable', 'BOOLEAN NOT NULL DEFAULT FALSE');

-- College scoping and forwarding on requirements
CALL v13_add_column('requirements', 'college_id', 'BIGINT NULL');
CALL v13_add_column('requirements', 'college_admin_notes', 'TEXT NULL');
CALL v13_add_column('requirements', 'forwarded_by', 'VARCHAR(150) NULL');
CALL v13_add_column('requirements', 'forwarded_at', 'DATETIME NULL');
CALL v13_add_index('requirements', 'idx_requirement_college_status', 'college_id, status');

-- Orders
CALL v13_add_column('order_management', 'college_id', 'BIGINT NULL');
CALL v13_add_column('order_management', 'currency', 'VARCHAR(10) NULL DEFAULT ''INR''');
CALL v13_add_column('order_management', 'simulated_payment', 'BOOLEAN NOT NULL DEFAULT FALSE');
CALL v13_add_index('order_management', 'idx_order_college', 'college_id');

DROP PROCEDURE IF EXISTS v13_add_column;
DROP PROCEDURE IF EXISTS v13_add_index;

CREATE TABLE IF NOT EXISTS college_project_allocations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    college_id BIGINT NOT NULL,
    project_id BIGINT NOT NULL,
    price_override DECIMAL(12,2) NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    allocated_by VARCHAR(150) NOT NULL,
    allocated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_by VARCHAR(150),
    revoked_at DATETIME NULL,
    CONSTRAINT uk_college_project UNIQUE (college_id, project_id),
    CONSTRAINT fk_alloc_college FOREIGN KEY (college_id) REFERENCES colleges(id),
    CONSTRAINT fk_alloc_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_alloc_college_active (college_id, active),
    INDEX idx_alloc_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS project_entitlements (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    project_id BIGINT NOT NULL,
    source VARCHAR(30) NOT NULL,
    order_id BIGINT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    granted_by VARCHAR(150) NOT NULL,
    granted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_at DATETIME NULL,
    CONSTRAINT uk_entitlement_user_project UNIQUE (user_id, project_id),
    CONSTRAINT fk_entitlement_user FOREIGN KEY (user_id) REFERENCES user_management(id),
    CONSTRAINT fk_entitlement_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_entitlement_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS payment_transactions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    provider VARCHAR(50) NOT NULL,
    provider_reference VARCHAR(120) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    simulated BOOLEAN NOT NULL DEFAULT FALSE,
    failure_reason VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at DATETIME NULL,
    CONSTRAINT uk_payment_provider_ref UNIQUE (provider_reference),
    CONSTRAINT fk_payment_order FOREIGN KEY (order_id) REFERENCES order_management(id),
    INDEX idx_payment_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS status_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    entity_type VARCHAR(30) NOT NULL,
    entity_id BIGINT NOT NULL,
    from_status VARCHAR(60),
    to_status VARCHAR(60) NOT NULL,
    actor_email VARCHAR(150) NOT NULL,
    note TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status_history_entity (entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Backfill: existing marketplace projects become published library projects.
UPDATE projects SET project_type = 'LIBRARY', catalog_status = 'PUBLISHED'
 WHERE is_marketplace = TRUE AND project_type = 'CUSTOM';
UPDATE projects SET price = budget WHERE project_type = 'LIBRARY' AND price IS NULL AND budget IS NOT NULL;

-- Backfill: carry single-buyer access over as entitlements.
INSERT IGNORE INTO project_entitlements (user_id, project_id, source, active, granted_by, granted_at)
SELECT p.purchased_by_user_id, p.id,
       CASE WHEN p.project_type = 'LIBRARY' THEN 'PURCHASE' ELSE 'CUSTOM_DELIVERY' END,
       TRUE, 'migration-v13', NOW()
  FROM projects p
  JOIN user_management u ON u.id = p.purchased_by_user_id
 WHERE p.purchased_by_user_id IS NOT NULL;
