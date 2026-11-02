-- ====================================================================
-- Academic Integration Tool - Developer 3: Project & Assignment Schema
-- Database Target: MySQL 8.x
-- ====================================================================

-- 1. Create Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    project_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    budget DECIMAL(12, 2),
    technology_stack VARCHAR(255),
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    linked_requirement_id BIGINT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    INDEX idx_project_code (project_code),
    INDEX idx_project_status (status),
    INDEX idx_linked_req (linked_requirement_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Create Project Assignments Junction Table (Many-to-Many: User <-> Project)
CREATE TABLE IF NOT EXISTS project_assignments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expired_at DATETIME NULL,
    deactivated_at DATETIME NULL,
    assigned_by VARCHAR(255) NOT NULL,
    notes VARCHAR(255) NULL,
    CONSTRAINT fk_pa_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_pa_user FOREIGN KEY (user_id) REFERENCES user_management(id) ON DELETE CASCADE,
    INDEX idx_pa_project (project_id),
    INDEX idx_pa_user (user_id),
    INDEX idx_pa_active_user (user_id, active),
    INDEX idx_pa_active_project (project_id, active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
