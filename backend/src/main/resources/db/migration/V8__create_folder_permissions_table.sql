-- Table: folder_permissions
CREATE TABLE IF NOT EXISTS `folder_permissions` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `folder_id` BIGINT NOT NULL,
    `user_id` BIGINT NULL,
    `role` VARCHAR(50) NULL,
    `permission_status` VARCHAR(20) NOT NULL DEFAULT 'ALLOWED',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_folder_perm_folder` FOREIGN KEY (`folder_id`) REFERENCES `folder_master` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_folder_perm_user` FOREIGN KEY (`user_id`) REFERENCES `user_management` (`id`) ON DELETE CASCADE,
    CONSTRAINT `uk_folder_user` UNIQUE (`folder_id`, `user_id`),
    CONSTRAINT `uk_folder_role` UNIQUE (`folder_id`, `role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
