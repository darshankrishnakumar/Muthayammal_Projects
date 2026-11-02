package com.academic.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;

@Configuration
@EnableWebSecurity
@org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity
public class SecurityConfig {

    @Autowired
    private JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(org.springframework.http.HttpMethod.OPTIONS, "/**").permitAll()
                .requestMatchers("/api/auth/**", "/api/auth").permitAll()
                .requestMatchers("/api/orders/catalog").permitAll()
                .requestMatchers("/api/access-control/**", "/api/access-control").hasAnyRole("SUPER_ADMIN", "ADMIN")
                .requestMatchers("/api/notifications/**", "/api/notifications").hasAnyRole("SUPER_ADMIN", "ADMIN", "PROJECT_DEVELOPER", "USER")
                .requestMatchers("/api/admins/**", "/api/admins").hasAnyRole("SUPER_ADMIN", "ADMIN")
                .requestMatchers("/api/developers/**", "/api/developers").hasRole("SUPER_ADMIN")
                .requestMatchers("/api/audit-logs/**", "/api/audit-logs").hasAnyRole("SUPER_ADMIN", "ADMIN")
                .requestMatchers("/api/users/**", "/api/users").hasAnyRole("SUPER_ADMIN", "ADMIN", "PROJECT_DEVELOPER", "USER")
                .requestMatchers("/api/projects/**", "/api/projects").hasAnyRole("SUPER_ADMIN", "ADMIN", "PROJECT_DEVELOPER", "USER")
                .requestMatchers("/api/requirements/**", "/api/requirements").hasAnyRole("SUPER_ADMIN", "ADMIN", "PROJECT_DEVELOPER", "USER")
                .requestMatchers("/api/folders/**", "/api/folders").hasAnyRole("SUPER_ADMIN", "ADMIN", "PROJECT_DEVELOPER", "USER")
                .requestMatchers("/api/assets/**", "/api/assets").hasAnyRole("SUPER_ADMIN", "ADMIN", "PROJECT_DEVELOPER", "USER")
                .requestMatchers("/api/permissions/**", "/api/permissions").hasAnyRole("SUPER_ADMIN", "ADMIN", "PROJECT_DEVELOPER", "USER")
                .requestMatchers("/api/orders/**", "/api/orders").hasAnyRole("SUPER_ADMIN", "ADMIN", "PROJECT_DEVELOPER", "USER")
                .anyRequest().authenticated()
            );

        http.addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        // Allow all origin patterns dynamically with credentials support
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setExposedHeaders(Arrays.asList("Authorization", "Content-Disposition", "Link", "X-Total-Count"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public org.springframework.boot.autoconfigure.flyway.FlywayMigrationStrategy flywayMigrationStrategy() {
        return flyway -> {
            flyway.repair();
            flyway.migrate();
        };
    }
}
