package com.academic.service;

import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Slows down password guessing: after {@value #MAX_FAILURES} failed logins for the same
 * email from the same address, further attempts are refused for {@link #LOCK_DURATION}.
 * In-memory, so it resets on restart and is per instance; good enough for a single node.
 */
@Service
public class LoginAttemptService {

    static final int MAX_FAILURES = 5;
    static final Duration LOCK_DURATION = Duration.ofMinutes(15);

    private record Attempts(int failures, Instant lockedUntil) {}

    private final Map<String, Attempts> attempts = new ConcurrentHashMap<>();

    public void assertNotLocked(String email, String clientIp) {
        Attempts a = attempts.get(key(email, clientIp));
        if (a != null && a.lockedUntil() != null && Instant.now().isBefore(a.lockedUntil())) {
            long minutes = Math.max(1, Duration.between(Instant.now(), a.lockedUntil()).toMinutes());
            throw new IllegalStateException("Too many failed sign-in attempts. Try again in " + minutes + " minute(s).");
        }
    }

    public void recordFailure(String email, String clientIp) {
        attempts.compute(key(email, clientIp), (k, a) -> {
            int failures = (a == null || (a.lockedUntil() != null && Instant.now().isAfter(a.lockedUntil()))) ? 1 : a.failures() + 1;
            return new Attempts(failures, failures >= MAX_FAILURES ? Instant.now().plus(LOCK_DURATION) : null);
        });
    }

    public void recordSuccess(String email, String clientIp) {
        attempts.remove(key(email, clientIp));
    }

    private static String key(String email, String ip) {
        return (email == null ? "" : email.trim().toLowerCase()) + "|" + (ip == null ? "" : ip);
    }
}
