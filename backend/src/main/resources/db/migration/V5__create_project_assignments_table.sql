-- Migration File V5: Project Assignments Table
-- Table: project_assignments

CREATE TABLE IF NOT EXISTS `project_assignments` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `project_id` BIGINT NOT NULL,
  `user_id` BIGINT NOT NULL,
  `assigned_by` VARCHAR(255) NULL,
  `assigned_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deactivated_at` DATETIME NULL,
  `expired_at` DATETIME NULL,
  `active` BOOLEAN NOT NULL DEFAULT TRUE,
  `notes` VARCHAR(500) NULL,
  INDEX `idx_assign_project` (`project_id`),
  INDEX `idx_assign_user` (`user_id`),
  INDEX `idx_assign_active` (`active`),
  CONSTRAINT `fk_assignments_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_assignments_user` FOREIGN KEY (`user_id`) REFERENCES `user_management` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
