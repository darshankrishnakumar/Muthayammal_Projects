package com.academic.controller;

import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import com.academic.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admins")
public class AdminController {

    @Autowired
    private UserService userService;

    private User getAuthenticatedUser() {
        String email = (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        return userService.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Authenticated user not found."));
    }

    @GetMapping
    public ResponseEntity<?> getAdmins(
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "status", required = false) String status) {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Super Admin is authorized to view administrators."));
        }
        List<User> admins = userService.getAdmins(search, status);
        return ResponseEntity.ok(admins);
    }

    @PostMapping
    public ResponseEntity<?> createAdmin(@RequestBody Map<String, String> payload) {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Super Admin is authorized to create administrators."));
        }

        try {
            String email = payload.get("email");
            String password = payload.get("password");
            String fullName = payload.get("fullName");
            String statusStr = payload.get("status");

            String collegeIdStr = payload.get("collegeId");
            if (collegeIdStr == null || collegeIdStr.isBlank()) {
                return ResponseEntity.badRequest().body(Map.of("message", "Select the college this administrator manages."));
            }
            if (password == null || password.length() < 8) {
                return ResponseEntity.badRequest().body(Map.of("message", "Password must be at least 8 characters long."));
            }
            User newAdmin = new User(email, password, fullName, Role.ADMIN,
                    UserStatus.valueOf(statusStr != null ? statusStr.toUpperCase() : "ACTIVE"));
            User savedAdmin = userService.createUser(newAdmin, actor.getEmail());
            savedAdmin = userService.changeRoleAndCollege(savedAdmin, Role.ADMIN, Long.valueOf(collegeIdStr), actor.getEmail());
            return ResponseEntity.status(HttpStatus.CREATED).body(savedAdmin);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateAdmin(
            @PathVariable("id") Long id,
            @RequestBody Map<String, String> payload) {
        
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Super Admin is authorized to update administrators."));
        }
        
        try {
            User updateData = new User();
            if (payload.containsKey("fullName")) updateData.setFullName(payload.get("fullName"));
            if (payload.containsKey("email")) updateData.setEmail(payload.get("email"));
            if (payload.containsKey("status")) updateData.setStatus(UserStatus.valueOf(payload.get("status").toUpperCase()));

            String newPassword = payload.get("password");

            User updatedAdmin = userService.updateUser(id, updateData, newPassword, actor.getEmail());
            if (payload.get("collegeId") != null && !payload.get("collegeId").isBlank() && updatedAdmin.getRole() == Role.ADMIN) {
                updatedAdmin = userService.changeRoleAndCollege(updatedAdmin, Role.ADMIN, Long.valueOf(payload.get("collegeId")), actor.getEmail());
            }
            return ResponseEntity.ok(updatedAdmin);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteAdmin(@PathVariable("id") Long id) {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Super Admin is authorized to delete administrators."));
        }

        if (actor.getId().equals(id)) {
            return ResponseEntity.badRequest().body(Map.of("message", "Self-deletion is prohibited."));
        }

        try {
            userService.deleteUser(id, actor.getEmail());
            return ResponseEntity.ok(Map.of("message", "Administrator account successfully deleted."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }
}
