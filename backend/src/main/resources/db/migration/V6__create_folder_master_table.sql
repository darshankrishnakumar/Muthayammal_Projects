-- Migration File V6: Create Folder Master Table
-- Table: folder_master

CREATE TABLE IF NOT EXISTS `folder_master` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `parent_folder_id` BIGINT NULL,
    `project_id` BIGINT NOT NULL,
    `created_by` VARCHAR(255) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `active` BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT `fk_folder_parent` FOREIGN KEY (`parent_folder_id`) REFERENCES `folder_master` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_folder_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
    INDEX `idx_folder_project` (`project_id`),
    INDEX `idx_folder_parent` (`parent_folder_id`),
    INDEX `idx_folder_active` (`active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
