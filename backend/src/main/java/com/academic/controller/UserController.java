package com.academic.controller;

import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import com.academic.service.AccessControlService;
import com.academic.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

/**
 * Account management.
 * <ul>
 *   <li>SUPER_ADMIN: every account; the only role that can grant roles.</li>
 *   <li>ADMIN: student (USER) accounts of their own college only.</li>
 *   <li>Everyone: their own profile (name, mobile, password) but never their own role or status.</li>
 * </ul>
 */
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    @Autowired
    private AccessControlService accessControlService;

    @GetMapping
    public List<User> getUsers(@RequestParam(value = "search", required = false) String search,
                               @RequestParam(value = "status", required = false) String status,
                               @RequestParam(value = "role", required = false) String role) {
        User actor = accessControlService.getCurrentAuthenticatedUser();
        return switch (actor.getRole()) {
            case SUPER_ADMIN -> role == null || role.isBlank()
                    ? userService.searchUsers(search, status)
                    : userService.searchAll(search, status, Role.valueOf(role.trim().toUpperCase()));
            case ADMIN -> userService.searchCollegeStudents(accessControlService.requireCollege(actor).getId(), search, status);
            default -> throw new AccessDeniedException("Access denied.");
        };
    }

    @GetMapping("/assignable")
    public List<User> getAssignableUsers(@RequestParam(value = "role", required = false) String role) {
        User actor = accessControlService.getCurrentAuthenticatedUser();
        if (actor.getRole() == Role.ADMIN) {
            return userService.searchCollegeStudents(accessControlService.requireCollege(actor).getId(), null, "ACTIVE");
        }
        if (actor.getRole() != Role.SUPER_ADMIN) {
            throw new AccessDeniedException("Access denied.");
        }
        Role target = role != null && !role.isBlank() ? Role.valueOf(role.trim().toUpperCase()) : Role.USER;
        return userService.searchAll(null, "ACTIVE", target);
    }

    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody Map<String, String> payload) {
        User actor = accessControlService.getCurrentAuthenticatedUser();
        Role role = Role.valueOf(required(payload, "role").toUpperCase());
        UserStatus status = payload.get("status") != null ? UserStatus.valueOf(payload.get("status").toUpperCase()) : UserStatus.ACTIVE;
        Long collegeId = payload.get("collegeId") != null && !payload.get("collegeId").isBlank() ? Long.valueOf(payload.get("collegeId")) : null;

        switch (actor.getRole()) {
            case SUPER_ADMIN -> {
                if (role == Role.SUPER_ADMIN) {
                    throw new AccessDeniedException("Additional Super Admin accounts must be created directly in the database by the platform owner.");
                }
            }
            case ADMIN -> {
                if (role != Role.USER) {
                    throw new AccessDeniedException("College administrators can only create student accounts.");
                }
                collegeId = accessControlService.requireCollege(actor).getId();
            }
            default -> throw new AccessDeniedException("Access denied.");
        }

        String password = required(payload, "password");
        if (password.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters long.");
        }
        User newUser = new User(required(payload, "email").trim().toLowerCase(), password, required(payload, "fullName").trim(), role, status);
        newUser.setMobileNumber(payload.get("mobileNumber"));
        User saved = userService.createUser(newUser, actor.getEmail());
        if (role == Role.USER || role == Role.ADMIN) {
            saved = userService.changeRoleAndCollege(saved, role, collegeId, actor.getEmail());
        }
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @PutMapping("/{id}")
    public User updateUser(@PathVariable("id") Long id, @RequestBody Map<String, String> payload) {
        User actor = accessControlService.getCurrentAuthenticatedUser();
        User target = userService.findById(id).orElseThrow(() -> new NoSuchElementException("User profile not found."));
        boolean self = actor.getId().equals(id);

        if (!self) {
            accessControlService.assertCanManageUser(actor, target);
        }

        User updateData = new User();
        if (payload.containsKey("fullName")) updateData.setFullName(payload.get("fullName"));
        if (payload.containsKey("mobileNumber")) updateData.setMobileNumber(payload.get("mobileNumber"));
        if (payload.containsKey("organization")) updateData.setOrganization(payload.get("organization"));
        if (payload.containsKey("email") && actor.getRole() != Role.USER) updateData.setEmail(payload.get("email"));
        if (payload.containsKey("status") && !self) updateData.setStatus(UserStatus.valueOf(payload.get("status").toUpperCase()));

        String newPassword = payload.get("password");
        if (newPassword != null && !newPassword.isBlank() && newPassword.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters long.");
        }

        User saved = userService.updateUser(id, updateData, newPassword, actor.getEmail());

        boolean roleChange = payload.containsKey("role") && payload.get("role") != null && !payload.get("role").isBlank()
                && Role.valueOf(payload.get("role").toUpperCase()) != target.getRole();
        boolean collegeChange = payload.containsKey("collegeId") && payload.get("collegeId") != null && !payload.get("collegeId").isBlank();
        if (roleChange || collegeChange) {
            if (actor.getRole() != Role.SUPER_ADMIN) {
                throw new AccessDeniedException("Only the Super Admin can change roles or college membership.");
            }
            if (self) {
                throw new AccessDeniedException("You cannot change your own role.");
            }
            Role newRole = roleChange ? Role.valueOf(payload.get("role").toUpperCase()) : null;
            if (newRole == Role.SUPER_ADMIN) {
                throw new AccessDeniedException("Super Admin cannot be granted through the API.");
            }
            saved = userService.changeRoleAndCollege(saved, newRole, collegeChange ? Long.valueOf(payload.get("collegeId")) : null, actor.getEmail());
        }
        return saved;
    }

    @DeleteMapping("/{id}")
    public Map<String, String> deleteUser(@PathVariable("id") Long id) {
        User actor = accessControlService.getCurrentAuthenticatedUser();
        User target = userService.findById(id).orElseThrow(() -> new NoSuchElementException("User profile not found."));
        if (actor.getId().equals(id)) {
            throw new IllegalArgumentException("Self-deletion is prohibited.");
        }
        accessControlService.assertCanManageUser(actor, target);
        if (target.getRole() == Role.SUPER_ADMIN) {
            throw new AccessDeniedException("Super Admin accounts cannot be deleted through the API.");
        }
        userService.deleteUser(id, actor.getEmail());
        return Map.of("message", "User account soft deleted successfully.");
    }

    @PostMapping("/bulk")
    public ResponseEntity<?> bulkCreateUsers(@RequestBody com.academic.dto.BulkUserCreateRequest payload) {
        User actor = accessControlService.getCurrentAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN && actor.getRole() != Role.ADMIN) {
            throw new AccessDeniedException("Access denied. Only administrators can bulk create users.");
        }
        return ResponseEntity.status(HttpStatus.CREATED).body(userService.bulkCreateUsers(payload, actor));
    }

    private static String required(Map<String, String> payload, String key) {
        String v = payload.get(key);
        if (v == null || v.isBlank()) {
            throw new IllegalArgumentException(key + " is required.");
        }
        return v;
    }
}
