package com.academic.util;

import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import com.academic.repository.UserRepository;
import com.academic.service.AuditLogService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;

@Component
@Order(1)
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

    @Autowired
    private DataSource dataSource;

    @Value("${academic.seed.demo-accounts:false}")
    private boolean seedDemoAccounts;

    @Override
    public void run(String... args) throws Exception {
        if (isMySql()) {
            applyLegacyColumnFixes();
        }

        if (!seedDemoAccounts) {
            if (userRepository.count() == 0) {
                logger.warn("No accounts exist and demo seeding is disabled. Create the first SUPER_ADMIN manually "
                        + "or start once with academic.seed.demo-accounts=true in a non-production profile.");
            }
            return;
        }

        seedIfMissing("superadmin@academic.com", "Superadmin123!", "Super Administrator", Role.SUPER_ADMIN);
        seedIfMissing("admin@academic.com", "Admin123!", "College Administrator", Role.ADMIN);
        seedIfMissing("developer@academic.com", "Developer123!", "Project Developer", Role.PROJECT_DEVELOPER);
        seedIfMissing("user@academic.com", "User123!", "Demo Student", Role.USER);
    }

    private void seedIfMissing(String email, String password, String fullName, Role role) {
        if (userRepository.findByEmail(email).isPresent()) {
            return;
        }
        User user = new User();
        user.setEmail(email);
        user.setPassword(passwordEncoder.encode(password));
        user.setFullName(fullName);
        user.setRole(role);
        user.setStatus(UserStatus.ACTIVE);
        user.setEmailVerified(true);
        userRepository.save(user);
        auditLogService.log("system", "SYSTEM_INIT", "Seeded demo account " + email + " (" + role + ").");
        logger.info("Seeded demo account {} ({})", email, role);
    }

    /**
     * Column type fixes that earlier versions applied outside Flyway. Idempotent on MySQL.
     */
    private void applyLegacyColumnFixes() {
        String[] statements = {
                "ALTER TABLE requirements MODIFY image_url LONGTEXT",
                "ALTER TABLE requirements MODIFY audio_url LONGTEXT",
                "ALTER TABLE user_management MODIFY role VARCHAR(100) NOT NULL DEFAULT 'USER'",
                "ALTER TABLE requirements MODIFY status VARCHAR(100) NOT NULL DEFAULT 'DRAFT'",
                "ALTER TABLE projects MODIFY status VARCHAR(100) NOT NULL DEFAULT 'CREATED'"
        };
        for (String sql : statements) {
            try {
                jdbcTemplate.execute(sql);
            } catch (Exception e) {
                logger.debug("Skipped legacy column fix ({}): {}", sql, e.getMessage());
            }
        }
    }

    private boolean isMySql() {
        try (Connection c = dataSource.getConnection()) {
            return c.getMetaData().getDatabaseProductName().toLowerCase().contains("mysql");
        } catch (Exception e) {
            return false;
        }
    }
}
