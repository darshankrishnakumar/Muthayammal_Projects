-- Migration File V4: Projects Table
-- Table: projects

CREATE TABLE IF NOT EXISTS `projects` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `project_code` VARCHAR(50) NOT NULL UNIQUE,
  `project_name` VARCHAR(255) NOT NULL,
  `description` TEXT NULL,
  `status` VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
  `budget` DOUBLE NULL,
  `technology_stack` VARCHAR(255) NULL,
  `linked_requirement_id` BIGINT NULL,
  `created_by` VARCHAR(255) NULL,
  `updated_by` VARCHAR(255) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_project_code` (`project_code`),
  INDEX `idx_project_status` (`status`),
  INDEX `idx_project_req` (`linked_requirement_id`),
  CONSTRAINT `fk_projects_requirement` FOREIGN KEY (`linked_requirement_id`) REFERENCES `requirements` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
