package com.academic.controller;

import com.academic.model.Role;
import com.academic.model.User;
import com.academic.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    // Get current authenticated user helper
    private User getAuthenticatedUser() {
        String email = (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        return userService.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Authenticated user not found."));
    }

    @GetMapping
    public ResponseEntity<?> getUsers(
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "status", required = false) String status) {
        
        User actor = getAuthenticatedUser();
        
        // Enforce RBAC: Regular Users cannot list users
        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
        }

        List<User> users = userService.searchUsers(search, status);
        return ResponseEntity.ok(users);
    }

    @GetMapping("/assignable")
    public ResponseEntity<?> getAssignableUsers(@RequestParam(value = "role", required = false) String role) {
        User actor = getAuthenticatedUser();
        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
        }

        Role targetRole = null;
        if (actor.getRole() == Role.ADMIN) {
            targetRole = Role.USER; // Admins can only see and assign regular Users
        } else if (role != null && !role.isBlank()) {
            try {
                targetRole = Role.valueOf(role.toUpperCase());
            } catch (IllegalArgumentException e) {
                targetRole = Role.USER;
            }
        }

        List<User> users;
        if (targetRole == Role.ADMIN) {
            users = userService.getAdmins(null, "ACTIVE");
        } else {
            users = userService.getAssignableUsers();
        }
        return ResponseEntity.ok(users);
    }

    @PostMapping
    public ResponseEntity<?> createUser(@RequestBody Map<String, String> payload) {
        User actor = getAuthenticatedUser();

        // Enforce RBAC: Regular Users cannot create accounts
        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
        }

        try {
            String email = payload.get("email");
            String password = payload.get("password");
            String fullName = payload.get("fullName");
            String roleStr = payload.get("role");
            String statusStr = payload.get("status");

            Role role = Role.valueOf(roleStr.toUpperCase());
            
            // Enforce RBAC: Admin cannot create another Admin
            if (actor.getRole() == Role.ADMIN && role == Role.ADMIN) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN)
                        .body(Map.of("message", "Administrators cannot register another Admin."));
            }

            User newUser = new User(email, password, fullName, role, 
                    com.academic.model.UserStatus.valueOf(statusStr.toUpperCase()));

            User savedUser = userService.createUser(newUser, actor.getEmail());
            return ResponseEntity.status(HttpStatus.CREATED).body(savedUser);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateUser(
            @PathVariable("id") Long id,
            @RequestBody Map<String, String> payload) {
        
        User actor = getAuthenticatedUser();
        User target = userService.findById(id)
                .orElseThrow(() -> new RuntimeException("User profile not found."));

        // Enforce RBAC: Regular Users can only modify their own profile
        if (actor.getRole() == Role.USER) {
            if (!actor.getId().equals(id)) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
            }
            // Users cannot escalate their own role or status
            payload.remove("role");
            payload.remove("status");
        }

        // Enforce RBAC: Admin cannot modify Admin or Super Admin accounts
        if (actor.getRole() == Role.ADMIN) {
            if (target.getRole() == Role.ADMIN || target.getRole() == Role.SUPER_ADMIN) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN)
                        .body(Map.of("message", "Administrators are unauthorized to modify other Admins."));
            }
            // Admin cannot escalate a User to Admin
            if (payload.containsKey("role") && Role.valueOf(payload.get("role").toUpperCase()) == Role.ADMIN) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN)
                        .body(Map.of("message", "Only Super Administrators can designate Admin roles."));
            }
        }

        try {
            User updateData = new User();
            if (payload.containsKey("fullName")) updateData.setFullName(payload.get("fullName"));
            if (payload.containsKey("email")) updateData.setEmail(payload.get("email"));
            if (payload.containsKey("role")) updateData.setRole(Role.valueOf(payload.get("role").toUpperCase()));
            if (payload.containsKey("status")) updateData.setStatus(com.academic.model.UserStatus.valueOf(payload.get("status").toUpperCase()));

            String newPassword = payload.get("password");

            User updatedUser = userService.updateUser(id, updateData, newPassword, actor.getEmail());
            return ResponseEntity.ok(updatedUser);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteUser(@PathVariable("id") Long id) {
        User actor = getAuthenticatedUser();
        User target = userService.findById(id)
                .orElseThrow(() -> new RuntimeException("User profile not found."));

        // Enforce RBAC: Regular Users cannot delete accounts
        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
        }

        // Enforce RBAC: Admin cannot delete other Admin or Super Admin accounts
        if (actor.getRole() == Role.ADMIN && (target.getRole() == Role.ADMIN || target.getRole() == Role.SUPER_ADMIN)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Administrators are unauthorized to delete other Admin profiles."));
        }

        // Enforce RBAC: Cannot delete self
        if (actor.getId().equals(id)) {
            return ResponseEntity.badRequest().body(Map.of("message", "Self-deletion is prohibited."));
        }

        try {
            userService.deleteUser(id, actor.getEmail());
            return ResponseEntity.ok(Map.of("message", "User account soft deleted successfully."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping("/bulk")
    public ResponseEntity<?> bulkCreateUsers(@RequestBody com.academic.dto.BulkUserCreateRequest payload) {
        User actor = getAuthenticatedUser();

        // Enforce RBAC: Regular Users cannot create accounts in bulk
        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied. Only Admins and Super Admins can bulk create users."));
        }

        try {
            com.academic.dto.BulkUserCreateResponse response = userService.bulkCreateUsers(payload, actor);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }
}
