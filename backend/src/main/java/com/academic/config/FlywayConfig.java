package com.academic.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.flyway.FlywayMigrationStrategy;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Kept separate from SecurityConfig: Flyway runs before JPA, and SecurityConfig depends on
 * repositories through the JWT filter, so defining this bean there creates a startup cycle.
 */
@Configuration
public class FlywayConfig {

    @Value("${academic.flyway.repair-on-start:false}")
    private boolean repairOnStart;

    @Bean
    public FlywayMigrationStrategy flywayMigrationStrategy() {
        return flyway -> {
            if (repairOnStart) {
                flyway.repair();
            }
            flyway.migrate();
        };
    }
}
