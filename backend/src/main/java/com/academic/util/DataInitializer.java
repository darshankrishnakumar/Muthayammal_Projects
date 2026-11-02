package com.academic.util;

import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import com.academic.repository.UserRepository;
import com.academic.service.AuditLogService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(DataInitializer.class);

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private AuditLogService auditLogService;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Override
    public void run(String... args) throws Exception {
        // Migration safeguard: Ensure image_url and audio_url are LONGTEXT and status is VARCHAR(100) in requirements table
        try {
            jdbcTemplate.execute("ALTER TABLE requirements MODIFY image_url LONGTEXT");
            jdbcTemplate.execute("ALTER TABLE requirements MODIFY audio_url LONGTEXT");
            jdbcTemplate.execute("ALTER TABLE user_management MODIFY role VARCHAR(100) NOT NULL DEFAULT 'USER'");
            jdbcTemplate.execute("ALTER TABLE requirements MODIFY status VARCHAR(100) NOT NULL DEFAULT 'DRAFT'");
            jdbcTemplate.execute("ALTER TABLE projects MODIFY status VARCHAR(100) NOT NULL DEFAULT 'CREATED'");
            jdbcTemplate.execute("UPDATE user_management SET email_verified = true WHERE status = 0");
            jdbcTemplate.execute("UPDATE user_management SET role = 'SUPER_ADMIN' WHERE email = 'superadmin@academic.com'");
            logger.info("Successfully migrated requirements columns, status fields, and active user email_verified flags.");
        } catch (Exception e) {
            logger.warn("DDL modification warning (table may not exist yet or column already updated): {}", e.getMessage());
        }

        // Bootstrap DB if empty
        if (userRepository.count() == 0) {
            logger.info("Initializing database with default security accounts...");

            // 1. Create Super Admin
            User superAdmin = new User();
            superAdmin.setEmail("superadmin@academic.com");
            superAdmin.setPassword(passwordEncoder.encode("Superadmin123!"));
            superAdmin.setFullName("Super Administrator");
            superAdmin.setRole(Role.SUPER_ADMIN);
            superAdmin.setStatus(UserStatus.ACTIVE);
            userRepository.save(superAdmin);

            // 2. Create Project Admin
            User admin = new User();
            admin.setEmail("admin@academic.com");
            admin.setPassword(passwordEncoder.encode("Admin123!"));
            admin.setFullName("Project Coordinator");
            admin.setRole(Role.ADMIN);
            admin.setStatus(UserStatus.ACTIVE);
            userRepository.save(admin);

            // 3. Create Regular User
            User user = new User();
            user.setEmail("user@academic.com");
            user.setPassword(passwordEncoder.encode("User123!"));
            user.setFullName("Academic Researcher");
            user.setRole(Role.USER);
            user.setStatus(UserStatus.ACTIVE);
            userRepository.save(user);

            auditLogService.log("system", "SYSTEM_INIT", "Database bootstrapped with default roles and accounts.");
            logger.info("Database bootstrap successfully completed.");
        } else {
            // Ensure all existing initial users are active
            userRepository.findAll().forEach(u -> {
                if (u.getStatus() == UserStatus.INACTIVE) {
                    u.setStatus(UserStatus.ACTIVE);
                    userRepository.save(u);
                }
            });
        }
    }
}
