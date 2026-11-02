-- Migration V11: Add High-Concurrency Performance Indexes for Projects, Folders, Requirements, and Assignments

CREATE INDEX `idx_projects_status_created` ON `projects` (`status`, `created_at`);
CREATE INDEX `idx_folder_proj_parent_act` ON `folder_master` (`project_id`, `parent_folder_id`, `active`);
CREATE INDEX `idx_req_user_status` ON `requirements` (`user_id`, `status`);
CREATE INDEX `idx_pa_proj_user_act` ON `project_assignments` (`project_id`, `user_id`, `active`);
