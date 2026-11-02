-- Migration File V7: Create Asset Master Table
-- Table: asset_master

CREATE TABLE IF NOT EXISTS `asset_master` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `folder_id` BIGINT NOT NULL,
    `file_name` VARCHAR(255) NOT NULL,
    `original_file_name` VARCHAR(255) NOT NULL,
    `mime_type` VARCHAR(150) NOT NULL,
    `extension` VARCHAR(50) NOT NULL,
    `file_size` BIGINT NOT NULL,
    `storage_path` VARCHAR(500) NOT NULL,
    `version_no` INT NOT NULL DEFAULT 1,
    `is_current_version` BOOLEAN NOT NULL DEFAULT TRUE,
    `parent_asset_id` BIGINT NULL,
    `description` TEXT NULL,
    `uploaded_by` VARCHAR(255) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `active` BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT `fk_asset_folder` FOREIGN KEY (`folder_id`) REFERENCES `folder_master` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_asset_parent` FOREIGN KEY (`parent_asset_id`) REFERENCES `asset_master` (`id`) ON DELETE SET NULL,
    INDEX `idx_asset_folder` (`folder_id`),
    INDEX `idx_asset_parent` (`parent_asset_id`),
    INDEX `idx_asset_current_version` (`is_current_version`),
    INDEX `idx_asset_active` (`active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
