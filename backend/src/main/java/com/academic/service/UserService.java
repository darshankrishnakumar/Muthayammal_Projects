package com.academic.service;

import com.academic.dto.RegisterRequest;
import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import com.academic.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.regex.Pattern;

@Service
@SuppressWarnings("null")
public class UserService {

    @Autowired
    private com.academic.repository.CollegeRepository collegeRepository;

    private static final Pattern EMAIL_PATTERN = Pattern.compile("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$");
    // Indian Mobile Number: 10 digits starting with 6, 7, 8, or 9, with optional +91 or 0 prefix
    private static final Pattern MOBILE_PATTERN = Pattern.compile("^(?:\\+91[\\-\\s]?|0)?[6-9]\\d{9}$");
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private AuditLogService auditLogService;

    public User authenticate(String email, String password) {
        if (email == null || email.isBlank() || password == null || password.isBlank()) {
            throw new RuntimeException("Email and password are required.");
        }

        User user = userRepository.findByEmailAndDeletedFalse(email.trim().toLowerCase())
                .orElseThrow(() -> new RuntimeException("Invalid email or password."));

        // Check if user is inactive
        if (user.getStatus() == UserStatus.INACTIVE) {
            throw new IllegalStateException("Your account is currently inactive. Please contact administrator.");
        }

        boolean passwordMatches = false;
        try {
            passwordMatches = passwordEncoder.matches(password, user.getPassword());
        } catch (Exception e) {
            passwordMatches = false;
        }

        if (!passwordMatches && user.getPassword() != null && user.getPassword().equals(password)) {
            passwordMatches = true;
            user.setPassword(passwordEncoder.encode(password));
            userRepository.save(user);
        }

        if (!passwordMatches) {
            throw new RuntimeException("Invalid email or password.");
        }

        return user;
    }

    @Transactional
    public User registerUser(RegisterRequest req) {
        if (req == null) {
            throw new IllegalArgumentException("Registration request cannot be empty.");
        }

        String fullName = req.getFullName() != null ? req.getFullName().trim() : "";
        String email = req.getEmail() != null ? req.getEmail().trim().toLowerCase() : "";
        String mobile = req.getMobileNumber() != null ? req.getMobileNumber().trim() : "";
        String organization = req.getOrganization() != null ? req.getOrganization().trim() : "";
        String password = req.getPassword();
        String confirmPassword = req.getConfirmPassword();

        if (fullName.isBlank()) {
            throw new IllegalArgumentException("Full Name is required.");
        }
        if (email.isBlank() || !EMAIL_PATTERN.matcher(email).matches()) {
            throw new IllegalArgumentException("Please provide a valid email address.");
        }
        if (!mobile.isBlank() && !MOBILE_PATTERN.matcher(mobile).matches()) {
            throw new IllegalArgumentException("Please provide a valid 10-digit Indian mobile number (e.g. 9876543210 or +91 9876543210).");
        }
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters long.");
        }
        if (confirmPassword == null || !password.equals(confirmPassword)) {
            throw new IllegalArgumentException("Password and Confirm Password do not match.");
        }

        if (req.getCollegeId() == null) {
            throw new IllegalArgumentException("Please select your college.");
        }
        com.academic.model.College college = collegeRepository.findById(req.getCollegeId())
                .filter(com.academic.model.College::isActive)
                .orElseThrow(() -> new IllegalArgumentException("The selected college is not available."));

        // Check if email already registered in DB (including soft-deleted accounts)
        Optional<User> existingOpt = userRepository.findByEmail(email);
        if (existingOpt.isPresent()) {
            User existing = existingOpt.get();
            // If already registered and not deleted, inform user cleanly
            if (!existing.isDeleted()) {
                throw new IllegalArgumentException("An account with this email is already registered. Please login.");
            }
            // If previously soft-deleted, reactivate account with new details
            existing.setFullName(fullName);
            existing.setMobileNumber(mobile);
            existing.setOrganization(organization.isEmpty() ? college.getName() : organization);
            existing.setPassword(passwordEncoder.encode(password));
            existing.setRole(Role.USER);
            existing.setCollege(college);
            existing.setStatus(UserStatus.ACTIVE);
            existing.setEmailVerified(true);
            existing.setDeleted(false);
            User saved = userRepository.save(existing);
            auditLogService.log(email, "USER_REGISTRATION_REACTIVATION", "Account re-registered and activated with USER role.");
            return saved;
        }

        // New User creation - Directly active with USER role
        User user = new User();
        user.setEmail(email);
        user.setPassword(passwordEncoder.encode(password));
        user.setFullName(fullName);
        user.setMobileNumber(mobile);
        user.setOrganization(organization.isEmpty() ? college.getName() : organization);
        user.setRole(Role.USER); // Force USER role
        user.setCollege(college);
        user.setStatus(UserStatus.ACTIVE);
        user.setEmailVerified(true);
        user.setDeleted(false);

        User saved = userRepository.save(user);
        auditLogService.log(email, "USER_REGISTRATION", "New user self-registered with USER role and activated.");
        return saved;
    }

    @Transactional
    public User verifyOtp(String email, String otp) {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("Email is required for verification.");
        }
        if (otp == null || otp.trim().length() != 6 || !otp.trim().matches("^\\d{6}$")) {
            throw new IllegalArgumentException("OTP must be exactly 6 digits.");
        }

        User user = userRepository.findByEmailAndDeletedFalse(email.trim().toLowerCase())
                .orElseThrow(() -> new IllegalArgumentException("No registration found for email: " + email));

        if (user.getStatus() == UserStatus.ACTIVE && user.isEmailVerified()) {
            return user;
        }

        if (user.getOtpExpiry() == null || user.getOtpExpiry().isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("Verification OTP has expired. Please request a new OTP.");
        }

        if (user.getOtpCode() == null || !user.getOtpCode().equals(otp.trim())) {
            throw new IllegalArgumentException("Invalid verification OTP. Please check the code and try again.");
        }

        user.setStatus(UserStatus.ACTIVE);
        user.setEmailVerified(true);
        user.setOtpCode(null);
        user.setOtpExpiry(null);

        User verified = userRepository.save(user);
        auditLogService.log(email, "OTP_VERIFIED", "User successfully verified email and activated account.");
        return verified;
    }

    @Transactional
    public String resendOtp(String email) {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("Email is required to resend OTP.");
        }

        User user = userRepository.findByEmailAndDeletedFalse(email.trim().toLowerCase())
                .orElseThrow(() -> new IllegalArgumentException("No account found with email: " + email));

        if (user.getStatus() == UserStatus.ACTIVE && user.isEmailVerified()) {
            throw new IllegalArgumentException("Account is already verified and active. Please login directly.");
        }

        String newOtp = generateSixDigitOtp();
        user.setOtpCode(newOtp);
        user.setOtpExpiry(LocalDateTime.now().plusMinutes(10));
        userRepository.save(user);

        auditLogService.log(email, "OTP_RESENT", "A fresh 6-digit OTP was generated for account verification.");
        return newOtp;
    }

    private String generateSixDigitOtp() {
        int code = 100000 + SECURE_RANDOM.nextInt(900000);
        return String.valueOf(code);
    }

    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmailAndDeletedFalse(email != null ? email.trim().toLowerCase() : "");
    }

    public Optional<User> findById(Long id) {
        return userRepository.findById(id).filter(u -> !u.isDeleted());
    }

    public List<User> searchUsers(String query, String statusStr) {
        UserStatus status = parseStatus(statusStr);
        String cleanQuery = (query != null && !query.trim().isEmpty()) ? query.trim() : null;
        return userRepository.searchUsersOnly(status, cleanQuery);
    }

    public List<User> getAssignableUsers() {
        return userRepository.searchUsersOnly(UserStatus.ACTIVE, null);
    }

    public List<User> getAdmins(String query, String statusStr) {
        UserStatus status = parseStatus(statusStr);
        String cleanQuery = (query != null && !query.trim().isEmpty()) ? query.trim() : null;
        return userRepository.searchAdminsOnly(status, cleanQuery);
    }

    private UserStatus parseStatus(String statusStr) {
        if (statusStr != null && !statusStr.trim().isEmpty()) {
            try {
                return UserStatus.valueOf(statusStr.toUpperCase());
            } catch (IllegalArgumentException e) {
                return null;
            }
        }
        return null;
    }

    @Transactional
    public User createUser(User user, String actorEmail) {
        if (userRepository.existsByEmailAndDeletedFalse(user.getEmail())) {
            throw new IllegalArgumentException("An active user with email " + user.getEmail() + " already exists.");
        }
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        user.setEmailVerified(true);
        user.setDeleted(false);
        User created = userRepository.save(user);
        auditLogService.log(actorEmail, "CREATE_USER", "Created user account: " + created.getEmail() + " with role: " + created.getRole());
        return created;
    }

    @Transactional
    public User createUser(User user) {
        return createUser(user, "SYSTEM");
    }

    @Transactional
    public User updateUser(Long id, User updateData, String newPassword, String actorEmail) {
        User existing = userRepository.findById(id)
                .filter(u -> !u.isDeleted())
                .orElseThrow(() -> new RuntimeException("User not found with id: " + id));

        if (updateData.getFullName() != null && !updateData.getFullName().isBlank()) {
            existing.setFullName(updateData.getFullName().trim());
        }
        if (updateData.getEmail() != null && !updateData.getEmail().isBlank()) {
            String newEmail = updateData.getEmail().trim().toLowerCase();
            if (!newEmail.equals(existing.getEmail()) && userRepository.existsByEmailAndDeletedFalse(newEmail)) {
                throw new IllegalArgumentException("Email " + newEmail + " is already in use.");
            }
            existing.setEmail(newEmail);
        }
        if (updateData.getMobileNumber() != null) {
            existing.setMobileNumber(updateData.getMobileNumber().trim());
        }
        if (updateData.getOrganization() != null) {
            existing.setOrganization(updateData.getOrganization().trim());
        }
        if (updateData.getStatus() != null) {
            existing.setStatus(updateData.getStatus());
        }
        if (newPassword != null && !newPassword.isBlank()) {
            existing.setPassword(passwordEncoder.encode(newPassword));
        }

        User saved = userRepository.save(existing);
        auditLogService.log(actorEmail, "UPDATE_USER", "Updated user details for: " + saved.getEmail());
        return saved;
    }

    @Transactional
    public User updateUser(Long id, User updateData) {
        return updateUser(id, updateData, null, "SYSTEM");
    }

    @Transactional
    public void deleteUser(Long id, String actorEmail) {
        User user = userRepository.findById(id)
                .filter(u -> !u.isDeleted())
                .orElseThrow(() -> new RuntimeException("User not found with id: " + id));

        user.setDeleted(true);
        user.setStatus(UserStatus.INACTIVE);
        userRepository.save(user);

        auditLogService.log(actorEmail, "DELETE_USER", "Soft-deleted user account: " + user.getEmail());
    }

    @Transactional
    public void deleteUser(Long id) {
        deleteUser(id, "SYSTEM");
    }

    @Transactional
    public com.academic.dto.BulkUserCreateResponse bulkCreateUsers(com.academic.dto.BulkUserCreateRequest request, User actor) {
        if (request == null || request.getUsers() == null || request.getUsers().isEmpty()) {
            return new com.academic.dto.BulkUserCreateResponse(0, 0, 0, 0);
        }

        boolean isSuperAdmin = actor.getRole() == Role.SUPER_ADMIN;
        boolean isAdmin = actor.getRole() == Role.ADMIN;

        if (!isSuperAdmin && !isAdmin) {
            throw new org.springframework.security.access.AccessDeniedException("Unauthorized to perform bulk user creation.");
        }

        com.academic.model.College bulkCollege = request.getCollegeId() != null
                ? collegeRepository.findById(request.getCollegeId())
                    .orElseThrow(() -> new java.util.NoSuchElementException("College not found: " + request.getCollegeId()))
                : null;
        if (isAdmin && actor.getCollege() == null) {
            throw new IllegalStateException("Your account is not linked to a college.");
        }

        List<com.academic.dto.BulkUserCreateRequest.UserCreateItemDto> items = request.getUsers();
        int total = items.size();
        int successCount = 0;
        int failedCount = 0;
        int duplicateCount = 0;

        List<User> validUsersToSave = new java.util.ArrayList<>();
        List<com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem> errorItems = new java.util.ArrayList<>();
        java.util.Set<String> processedEmailsInBatch = new java.util.HashSet<>();

        for (int i = 0; i < items.size(); i++) {
            com.academic.dto.BulkUserCreateRequest.UserCreateItemDto item = items.get(i);
            int rowNumber = i + 1;

            if (item == null) {
                errorItems.add(new com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem(rowNumber, "N/A", "Empty row"));
                failedCount++;
                continue;
            }

            String fullName = item.getFullName() != null ? item.getFullName().trim() : "";
            String email = item.getEmail() != null ? item.getEmail().trim().toLowerCase() : "";
            String rawPassword = item.getPassword() != null ? item.getPassword() : "";
            String phone = item.getPhone() != null ? item.getPhone().trim() : "";
            String roleStr = item.getRole() != null ? item.getRole().trim().toUpperCase() : "USER";
            String department = item.getDepartment() != null ? item.getDepartment().trim() : "";
            String organization = item.getOrganization() != null ? item.getOrganization().trim() : "";

            if (fullName.isEmpty()) {
                errorItems.add(new com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem(rowNumber, email, "Full Name is required"));
                failedCount++;
                continue;
            }

            if (email.isEmpty() || !EMAIL_PATTERN.matcher(email).matches()) {
                errorItems.add(new com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem(rowNumber, email, "Invalid email format"));
                failedCount++;
                continue;
            }

            // In-batch duplicate check
            if (processedEmailsInBatch.contains(email)) {
                errorItems.add(new com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem(rowNumber, email, "Duplicate email in upload batch"));
                duplicateCount++;
                failedCount++;
                continue;
            }

            // Database duplicate check
            if (userRepository.findByEmail(email).isPresent()) {
                errorItems.add(new com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem(rowNumber, email, "Email already registered in system"));
                duplicateCount++;
                failedCount++;
                continue;
            }

            // Role parsing & RBAC validation
            Role targetRole;
            try {
                targetRole = Role.valueOf(roleStr);
            } catch (Exception e) {
                targetRole = Role.USER;
            }

            // College admins provision students of their own college only
            if (isAdmin && targetRole != Role.USER) {
                errorItems.add(new com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem(rowNumber, email, "College administrators can only create student accounts"));
                failedCount++;
                continue;
            }
            if (targetRole == Role.SUPER_ADMIN) {
                errorItems.add(new com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem(rowNumber, email, "Super Admin accounts cannot be bulk-created"));
                failedCount++;
                continue;
            }

            if (rawPassword.length() < 8) {
                errorItems.add(new com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem(rowNumber, email, "Password must be at least 8 characters"));
                failedCount++;
                continue;
            }

            com.academic.model.College college = isAdmin ? actor.getCollege() : bulkCollege;
            boolean needsCollege = targetRole == Role.USER || targetRole == Role.ADMIN;
            if (needsCollege && college == null) {
                errorItems.add(new com.academic.dto.BulkUserCreateResponse.BulkUserErrorItem(rowNumber, email, "Select a college for student and administrator accounts"));
                failedCount++;
                continue;
            }

            User user = new User();
            user.setFullName(fullName);
            user.setEmail(email);
            user.setPassword(passwordEncoder.encode(rawPassword));
            user.setMobileNumber(phone);
            user.setOrganization(organization.isEmpty() ? (department.isEmpty() ? "Academic Institution" : department) : organization);
            user.setRole(targetRole);
            user.setStatus(UserStatus.ACTIVE);
            user.setEmailVerified(true);
            user.setDeleted(false);
            if (needsCollege) {
                user.setCollege(college);
            }

            validUsersToSave.add(user);
            processedEmailsInBatch.add(email);
        }

        List<User> savedUsers = new java.util.ArrayList<>();
        if (!validUsersToSave.isEmpty()) {
            savedUsers = userRepository.saveAll(validUsersToSave);
            successCount = savedUsers.size();

            // Emit a single consolidated audit log
            auditLogService.log(
                actor.getEmail(),
                "BULK_USER_CREATE",
                String.format("Bulk created %d users successfully (%d failed/skipped) out of %d records.", successCount, failedCount, total)
            );
        }

        com.academic.dto.BulkUserCreateResponse response = new com.academic.dto.BulkUserCreateResponse(total, successCount, failedCount, duplicateCount);
        response.setCreatedUsers(savedUsers);
        response.setErrors(errorItems);
        return response;
    }

    /**
     * Role/college changes. Callers must already have verified the actor is a SUPER_ADMIN.
     * ADMIN and USER accounts must belong to a college; SUPER_ADMIN and developers never do.
     */
    @Transactional
    public User changeRoleAndCollege(User target, Role role, Long collegeId, String actorEmail) {
        Role newRole = role != null ? role : target.getRole();
        com.academic.model.College college = target.getCollege();
        if (collegeId != null) {
            college = collegeRepository.findById(collegeId)
                    .orElseThrow(() -> new java.util.NoSuchElementException("College not found: " + collegeId));
        }
        if (newRole == Role.ADMIN || newRole == Role.USER) {
            if (college == null) {
                throw new IllegalArgumentException("College administrators and students must belong to a college.");
            }
            target.setCollege(college);
        } else {
            target.setCollege(null);
        }
        Role previous = target.getRole();
        target.setRole(newRole);
        User saved = userRepository.save(target);
        if (previous != newRole || collegeId != null) {
            auditLogService.log(actorEmail, "USER_ROLE_CHANGED", String.format("%s: %s -> %s%s", saved.getEmail(), previous, newRole,
                    saved.getCollege() != null ? " (" + saved.getCollege().getName() + ")" : ""));
        }
        return saved;
    }

    public List<User> searchAll(String query, String statusStr, Role role) {
        UserStatus status = parseStatus(statusStr);
        String q = (query != null && !query.trim().isEmpty()) ? query.trim().toLowerCase() : null;
        return userRepository.findAll().stream()
                .filter(u -> !u.isDeleted())
                .filter(u -> role == null || u.getRole() == role)
                .filter(u -> status == null || u.getStatus() == status)
                .filter(u -> q == null || u.getFullName().toLowerCase().contains(q) || u.getEmail().toLowerCase().contains(q))
                .sorted(java.util.Comparator.comparing(User::getCreatedAt, java.util.Comparator.nullsLast(java.util.Comparator.reverseOrder())))
                .toList();
    }

    public List<User> searchCollegeStudents(Long collegeId, String query, String statusStr) {
        String q = (query != null && !query.trim().isEmpty()) ? query.trim() : null;
        return userRepository.searchByCollegeAndRole(collegeId, Role.USER, parseStatus(statusStr), q);
    }
}
