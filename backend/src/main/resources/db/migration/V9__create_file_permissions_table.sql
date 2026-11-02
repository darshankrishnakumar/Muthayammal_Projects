-- Table: file_permissions
CREATE TABLE IF NOT EXISTS `file_permissions` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `asset_id` BIGINT NOT NULL,
    `user_id` BIGINT NULL,
    `role` VARCHAR(50) NULL,
    `permission_status` VARCHAR(20) NOT NULL DEFAULT 'ALLOWED',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_file_perm_asset` FOREIGN KEY (`asset_id`) REFERENCES `asset_master` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_file_perm_user` FOREIGN KEY (`user_id`) REFERENCES `user_management` (`id`) ON DELETE CASCADE,
    CONSTRAINT `uk_file_user` UNIQUE (`asset_id`, `user_id`),
    CONSTRAINT `uk_file_role` UNIQUE (`asset_id`, `role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
