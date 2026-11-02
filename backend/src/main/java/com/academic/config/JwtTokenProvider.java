package com.academic.config;

import io.jsonwebtoken.*;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Date;
import java.util.HexFormat;

@Component
public class JwtTokenProvider {

    private static final Logger logger = LoggerFactory.getLogger(JwtTokenProvider.class);

    // SHA-256 of the signing key that shipped in the public repository; never accepted in prod.
    // Stored as a hash so the key itself is not republished.
    private static final String LEAKED_SECRET_SHA256 =
            "8c55ec001f5e4cce133002d43c1eb9f6b866002f82c52a43776e2132792e0158";

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
        if (LEAKED_SECRET_SHA256.equals(sha256Hex(jwtSecret.trim()))) {
            if (activeProfiles != null && activeProfiles.contains("prod")) {
                throw new IllegalStateException("The JWT secret from the public repository cannot be used in production.");
            }
            logger.warn("Using the publicly known JWT secret. Acceptable for local development only; rotate it before deploying.");
        }
        signingKey = Keys.hmacShaKeyFor(keyBytes);
    }

    private static String sha256Hex(String value) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
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
