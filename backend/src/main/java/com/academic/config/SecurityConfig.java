package com.academic.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
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
import java.util.List;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private static final String[] ALL_ROLES = {"SUPER_ADMIN", "ADMIN", "PROJECT_DEVELOPER", "USER"};

    @Autowired
    private JwtAuthenticationFilter jwtAuthenticationFilter;

    @Value("${academic.cors.allowed-origins:http://localhost:5173}")
    private String allowedOrigins;

    @Value("${academic.flyway.repair-on-start:false}")
    private boolean repairOnStart;

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
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((req, res, e) -> writeError(res, HttpStatus.UNAUTHORIZED, "Unauthenticated: please sign in again."))
                .accessDeniedHandler((req, res, e) -> writeError(res, HttpStatus.FORBIDDEN, "Access denied."))
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                .requestMatchers("/error").permitAll()
                .requestMatchers(HttpMethod.POST, "/api/auth/login", "/api/auth/register", "/api/auth/verify-otp", "/api/auth/resend-otp").permitAll()
                .requestMatchers("/api/auth/**").authenticated()
                // Platform-owner only
                .requestMatchers("/api/colleges/**", "/api/colleges").hasRole("SUPER_ADMIN")
                .requestMatchers("/api/developers/**", "/api/developers").hasRole("SUPER_ADMIN")
                .requestMatchers("/api/library/**", "/api/library").hasRole("SUPER_ADMIN")
                .requestMatchers("/api/allocations/**", "/api/allocations").hasAnyRole("SUPER_ADMIN", "ADMIN")
                // Administration
                .requestMatchers("/api/access-control/**", "/api/access-control").hasAnyRole("SUPER_ADMIN", "ADMIN")
                .requestMatchers("/api/admins/**", "/api/admins").hasAnyRole("SUPER_ADMIN", "ADMIN")
                .requestMatchers("/api/audit-logs/**", "/api/audit-logs").hasAnyRole("SUPER_ADMIN", "ADMIN")
                // Shared; fine-grained checks happen in the service layer
                .requestMatchers("/api/**").hasAnyRole(ALL_ROLES)
                .anyRequest().denyAll()
            );

        http.addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        List<String> origins = Arrays.stream(allowedOrigins.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();

        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(origins);
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"));
        configuration.setAllowedHeaders(Arrays.asList("Authorization", "Content-Type", "Accept", "X-Requested-With",
                "bypass-tunnel-reminder", "ngrok-skip-browser-warning", "Idempotency-Key"));
        configuration.setExposedHeaders(Arrays.asList("Content-Disposition", "Content-Length", "Content-Range", "Accept-Ranges"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public org.springframework.boot.autoconfigure.flyway.FlywayMigrationStrategy flywayMigrationStrategy() {
        return flyway -> {
            if (repairOnStart) {
                flyway.repair();
            }
            flyway.migrate();
        };
    }

    private static void writeError(jakarta.servlet.http.HttpServletResponse res, HttpStatus status, String message) throws java.io.IOException {
        res.setStatus(status.value());
        res.setContentType(MediaType.APPLICATION_JSON_VALUE);
        res.getWriter().write("{\"message\":\"" + message + "\"}");
    }
}
