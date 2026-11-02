package com.academic.config;

import io.jsonwebtoken.*;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.security.Key;
import java.util.Date;

@Component
public class JwtTokenProvider {

    private static final Logger logger = LoggerFactory.getLogger(JwtTokenProvider.class);

    // Signing key that shipped in the public repository; never accepted.
    private static final String LEAKED_SECRET =
            "REMOVED_LEAKED_JWT_SECRET";

    @Value("${academic.jwt.secret:}")
    private String jwtSecret;

    @Value("${academic.jwt.expiration-ms:86400000}")
    private long jwtExpirationMs;

    @Value("${spring.profiles.active:}")
    private String activeProfiles;

    private Key signingKey;

    @PostConstruct
    void init() {
        if (jwtSecret == null || jwtSecret.isBlank()) {
            throw new IllegalStateException("JWT_SECRET is not configured. Set academic.jwt.secret (base64, >= 32 bytes).");
        }
        byte[] keyBytes;
        try {
            keyBytes = Decoders.BASE64.decode(jwtSecret.trim());
        } catch (RuntimeException e) {
            throw new IllegalStateException("JWT secret must be base64-encoded.", e);
        }
        if (keyBytes.length < 32) {
            throw new IllegalStateException("JWT secret must decode to at least 32 bytes.");
        }
        if (LEAKED_SECRET.equals(jwtSecret.trim())) {
            if (activeProfiles != null && activeProfiles.contains("prod")) {
                throw new IllegalStateException("The JWT secret from the public repository cannot be used in production.");
            }
            logger.warn("Using the publicly known JWT secret. Acceptable for local development only; rotate it before deploying.");
        }
        signingKey = Keys.hmacShaKeyFor(keyBytes);
    }

    public String generateToken(String email, String role) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + jwtExpirationMs);

        return Jwts.builder()
                .setSubject(email)
                .claim("role", role)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(signingKey, SignatureAlgorithm.HS256)
                .compact();
    }

    public String getEmailFromToken(String token) {
        return parse(token).getSubject();
    }

    public String getRoleFromToken(String token) {
        return parse(token).get("role", String.class);
    }

    public boolean validateToken(String token) {
        try {
            parse(token);
            return true;
        } catch (ExpiredJwtException ex) {
            logger.debug("Rejected expired JWT");
        } catch (JwtException | IllegalArgumentException ex) {
            logger.debug("Rejected invalid JWT: {}", ex.getClass().getSimpleName());
        }
        return false;
    }

    private Claims parse(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(signingKey)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }
}
