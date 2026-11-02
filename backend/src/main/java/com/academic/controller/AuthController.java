package com.academic.controller;

import com.academic.config.JwtTokenProvider;
import com.academic.dto.RegisterRequest;
import com.academic.dto.ResendOtpRequest;
import com.academic.dto.VerifyOtpRequest;
import com.academic.model.User;
import com.academic.service.AuditLogService;
import com.academic.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private com.academic.service.LoginAttemptService loginAttemptService;

    @Autowired
    private com.academic.service.CollegeService collegeService;

    /** Active colleges for the registration form (public). */
    @GetMapping("/colleges")
    public ResponseEntity<?> colleges() {
        return ResponseEntity.ok(collegeService.activeOptions());
    }

    @Autowired
    private UserService userService;

    @Autowired
    private JwtTokenProvider tokenProvider;

    @Autowired
    private AuditLogService auditLogService;

    @Value("${spring.profiles.active:dev}")
    private String activeProfile;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> request, jakarta.servlet.http.HttpServletRequest http) {
        String email = request.get("email");
        String password = request.get("password");
        String clientIp = http.getRemoteAddr();
        try {
            loginAttemptService.assertNotLocked(email, clientIp);
        } catch (IllegalStateException locked) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(Map.of("message", locked.getMessage()));
        }

        try {
            User user;
            try {
                user = userService.authenticate(email, password);
            } catch (RuntimeException authFailure) {
                if (!(authFailure instanceof IllegalStateException)) {
                    loginAttemptService.recordFailure(email, clientIp);
                }
                throw authFailure;
            }
            loginAttemptService.recordSuccess(email, clientIp);
            String token = tokenProvider.generateToken(user.getEmail(), user.getRole().name());

            auditLogService.log(user.getEmail(), "LOGIN", "User successfully authenticated as " + user.getRole());

            Map<String, Object> response = new HashMap<>();
            response.put("token", token);
            response.put("user", user);

            return ResponseEntity.ok(response);
        } catch (IllegalStateException e) {
            // Account pending verification
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                    "message", e.getMessage(),
                    "pendingVerification", true,
                    "email", email != null ? email.trim().toLowerCase() : ""
            ));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest request) {
        try {
            User user = userService.registerUser(request);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Account registered successfully! You can now log in with your email and password.");
            response.put("email", user.getEmail());
            response.put("role", user.getRole().name());
            response.put("status", user.getStatus().name());

            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("message", "Registration failed: " + e.getMessage()));
        }
    }

    @PostMapping("/verify-otp")
    public ResponseEntity<?> verifyOtp(@RequestBody VerifyOtpRequest request) {
        try {
            if (request == null || request.getEmail() == null || request.getOtp() == null) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body(Map.of("message", "Email and 6-digit OTP are required."));
            }

            User user = userService.verifyOtp(request.getEmail(), request.getOtp());
            String token = tokenProvider.generateToken(user.getEmail(), user.getRole().name());

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Account successfully verified and activated!");
            response.put("token", token);
            response.put("user", user);

            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("message", "Verification failed: " + e.getMessage()));
        }
    }

    @PostMapping("/resend-otp")
    public ResponseEntity<?> resendOtp(@RequestBody ResendOtpRequest request) {
        try {
            if (request == null || request.getEmail() == null || request.getEmail().isBlank()) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body(Map.of("message", "Email is required to resend OTP."));
            }

            String newOtp = userService.resendOtp(request.getEmail());

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "A new 6-digit verification code has been sent.");
            response.put("email", request.getEmail().trim().toLowerCase());

            if (!"prod".equalsIgnoreCase(activeProfile) && !"production".equalsIgnoreCase(activeProfile)) {
                response.put("otp", newOtp);
            }

            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("message", "Failed to resend OTP: " + e.getMessage()));
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout() {
        String email = (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        if (email != null && !email.equals("anonymousUser")) {
            auditLogService.log(email, "LOGOUT", "User logged out.");
        }
        return ResponseEntity.ok(Map.of("message", "Logged out successfully"));
    }

    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser() {
        String email = (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        if (email == null || email.equals("anonymousUser")) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("message", "Unauthenticated"));
        }

        User user = userService.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        return ResponseEntity.ok(user);
    }
}
