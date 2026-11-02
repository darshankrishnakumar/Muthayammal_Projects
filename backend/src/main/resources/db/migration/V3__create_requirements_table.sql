-- Migration File V3: Requirements Table
-- Table: requirements

CREATE TABLE IF NOT EXISTS `requirements` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT NULL,
  `title` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  `category` VARCHAR(100) NULL,
  `budget` DECIMAL(15, 2) NULL,
  `technology_stack` VARCHAR(255) NULL,
  `audio_url` VARCHAR(500) NULL,
  `image_url` VARCHAR(500) NULL,
  `audio_transcript` TEXT NULL,
  `image_ocr_text` TEXT NULL,
  `status` VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
  `rejection_reason` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_req_user` (`user_id`),
  INDEX `idx_req_status` (`status`),
  CONSTRAINT `fk_requirements_user` FOREIGN KEY (`user_id`) REFERENCES `user_management` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
