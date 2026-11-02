-- ====================================================================
-- Flyway Migration V14: columns the entities use that earlier migrations never created
-- (previously added implicitly by Hibernate ddl-auto=update). Safe on existing databases.
-- ====================================================================

DROP PROCEDURE IF EXISTS v14_add_column;
DELIMITER $$
CREATE PROCEDURE v14_add_column(IN tbl VARCHAR(64), IN col VARCHAR(64), IN def VARCHAR(255))
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

CALL v14_add_column('user_management', 'mobile_number', 'VARCHAR(255) NULL');
CALL v14_add_column('user_management', 'organization', 'VARCHAR(255) NULL');
CALL v14_add_column('user_management', 'otp_code', 'VARCHAR(10) NULL');
CALL v14_add_column('user_management', 'otp_expiry', 'DATETIME(6) NULL');
CALL v14_add_column('user_management', 'email_verified', 'BOOLEAN NOT NULL DEFAULT TRUE');

CALL v14_add_column('requirements', 'problem_statement', 'TEXT NULL');

CALL v14_add_column('project_assignments', 'created_at', 'DATETIME(6) NULL');
CALL v14_add_column('project_assignments', 'updated_at', 'DATETIME(6) NULL');

DROP PROCEDURE IF EXISTS v14_add_column;

-- Type alignment. Each change runs only when the column still has the legacy type.
DROP PROCEDURE IF EXISTS v14_align_types;
DELIMITER $$
CREATE PROCEDURE v14_align_types()
BEGIN
    -- user_management.status: entity stores 0=ACTIVE, 1=INACTIVE, 2=PENDING_VERIFICATION
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = DATABASE()
               AND table_name = 'user_management' AND column_name = 'status' AND data_type IN ('varchar', 'char')) THEN
        UPDATE user_management SET status = '0' WHERE UPPER(status) = 'ACTIVE';
        UPDATE user_management SET status = '1' WHERE UPPER(status) = 'INACTIVE';
        UPDATE user_management SET status = '2' WHERE UPPER(status) = 'PENDING_VERIFICATION';
        UPDATE user_management SET status = '0' WHERE status NOT IN ('0', '1', '2');
        ALTER TABLE user_management MODIFY status INT NOT NULL DEFAULT 0;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = DATABASE()
               AND table_name = 'projects' AND column_name = 'budget' AND data_type = 'double') THEN
        ALTER TABLE projects MODIFY budget DECIMAL(12,2) NULL;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = DATABASE()
               AND table_name = 'requirements' AND column_name = 'image_url' AND data_type <> 'longtext') THEN
        ALTER TABLE requirements MODIFY image_url LONGTEXT NULL;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = DATABASE()
               AND table_name = 'requirements' AND column_name = 'audio_url' AND data_type <> 'longtext') THEN
        ALTER TABLE requirements MODIFY audio_url LONGTEXT NULL;
    END IF;
END$$
DELIMITER ;

CALL v14_align_types();
DROP PROCEDURE IF EXISTS v14_align_types;
