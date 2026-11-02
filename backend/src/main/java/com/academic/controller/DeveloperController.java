package com.academic.controller;

import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import com.academic.model.ProjectAssignment;
import com.academic.repository.UserRepository;
import com.academic.repository.ProjectRepository;
import com.academic.repository.ProjectAssignmentRepository;
import com.academic.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.lang.NonNull;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

@RestController
@RequestMapping("/api/developers")
public class DeveloperController {

    @Autowired
    private UserService userService;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private ProjectAssignmentRepository assignmentRepository;

    private User getAuthenticatedUser() {
        String email = (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        return userService.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Authenticated user not found."));
    }

    private void enforceSuperAdmin(User actor) {
        if (actor.getRole() != Role.SUPER_ADMIN) {
            throw new org.springframework.security.access.AccessDeniedException("Access denied. Only Super Administrators can manage developers.");
        }
    }

    @GetMapping
    public ResponseEntity<?> getDevelopers(
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "status", required = false) String status) {
        User actor = getAuthenticatedUser();
        enforceSuperAdmin(actor);

        List<User> allDevs = userRepository.findAll().stream()
                .filter(u -> !u.isDeleted() && u.getRole() == Role.PROJECT_DEVELOPER)
                .filter(u -> {
                    if (status != null && !status.isBlank()) {
                        return u.getStatus().name().equalsIgnoreCase(status);
                    }
                    return true;
                })
                .filter(u -> {
                    if (search != null && !search.isBlank()) {
                        String q = search.toLowerCase();
                        return (u.getFullName() != null && u.getFullName().toLowerCase().contains(q)) ||
                               (u.getEmail() != null && u.getEmail().toLowerCase().contains(q));
                    }
                    return true;
                })
                .toList();

        return ResponseEntity.ok(allDevs);
    }

    @PostMapping
    public ResponseEntity<?> createDeveloper(@RequestBody Map<String, String> payload) {
        User actor = getAuthenticatedUser();
        enforceSuperAdmin(actor);

        try {
            String email = payload.get("email");
            String password = payload.get("password");
            String fullName = payload.get("fullName");
            String phone = payload.get("phone");
            String department = payload.get("department");
            String organization = payload.get("organization");
            String statusStr = payload.getOrDefault("status", "ACTIVE");

            User newDev = new User(email, password, fullName, Role.PROJECT_DEVELOPER, 
                    UserStatus.valueOf(statusStr.toUpperCase()));
            newDev.setMobileNumber(phone);
            newDev.setOrganization(organization != null && !organization.isBlank() ? organization : department);

            User saved = userService.createUser(newDev, actor.getEmail());
            return ResponseEntity.status(HttpStatus.CREATED).body(saved);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateDeveloper(
            @PathVariable("id") @NonNull Long id,
            @RequestBody Map<String, String> payload) {
        User actor = getAuthenticatedUser();
        enforceSuperAdmin(actor);

        try {
            Long safeId = Objects.requireNonNull(id, "Developer ID must not be null");
            User target = userRepository.findById(safeId)
                    .filter(u -> !u.isDeleted())
                    .orElseThrow(() -> new RuntimeException("Developer not found"));

            if (payload.containsKey("fullName")) target.setFullName(payload.get("fullName"));
            if (payload.containsKey("email")) target.setEmail(payload.get("email"));
            if (payload.containsKey("phone")) target.setMobileNumber(payload.get("phone"));
            if (payload.containsKey("organization")) target.setOrganization(payload.get("organization"));
            if (payload.containsKey("status")) target.setStatus(UserStatus.valueOf(payload.get("status").toUpperCase()));

            String newPassword = payload.get("password");
            User updated = userService.updateUser(safeId, target, newPassword, actor.getEmail());
            return ResponseEntity.ok(updated);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteDeveloper(@PathVariable("id") @NonNull Long id) {
        User actor = getAuthenticatedUser();
        enforceSuperAdmin(actor);

        try {
            Long safeId = Objects.requireNonNull(id, "Developer ID must not be null");
            userService.deleteUser(safeId, actor.getEmail());
            return ResponseEntity.ok(Map.of("message", "Developer profile deleted successfully."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @GetMapping("/{id}/projects")
    public ResponseEntity<?> getDeveloperProjects(@PathVariable("id") @NonNull Long id) {
        User actor = getAuthenticatedUser();
        enforceSuperAdmin(actor);

        Long safeId = Objects.requireNonNull(id, "Developer ID must not be null");
        List<ProjectAssignment> assignments = assignmentRepository.findByUserId(safeId);
        return ResponseEntity.ok(assignments);
    }

    @PostMapping("/{id}/assign-project")
    public ResponseEntity<?> assignProjectToDeveloper(
            @PathVariable("id") @NonNull Long id,
            @RequestBody Map<String, Object> payload) {
        User actor = getAuthenticatedUser();
        enforceSuperAdmin(actor);

        try {
            Long safeDevId = Objects.requireNonNull(id, "Developer ID must not be null");
            Long safeProjectId = Objects.requireNonNull(Long.valueOf(payload.get("projectId").toString()), "Project ID must not be null");
            String notes = payload.getOrDefault("notes", "Assigned by Super Admin").toString();
            String expiredAtStr = payload.containsKey("expiredAt") && payload.get("expiredAt") != null ? payload.get("expiredAt").toString() : null;

            User dev = userRepository.findById(safeDevId)
                    .filter(u -> !u.isDeleted())
                    .orElseThrow(() -> new RuntimeException("Developer not found"));

            com.academic.model.Project project = projectRepository.findById(safeProjectId)
                    .orElseThrow(() -> new RuntimeException("Project not found"));

            // Associate developer to project
            project.setDeveloper(dev);
            projectRepository.save(project);

            // Check if assignment record already exists
            Optional<ProjectAssignment> existing = assignmentRepository.findByProjectIdAndUserId(safeProjectId, safeDevId);
            ProjectAssignment assignment;
            if (existing.isPresent()) {
                assignment = existing.get();
                assignment.setActive(true);
                assignment.setNotes(notes);
                if (expiredAtStr != null && !expiredAtStr.isBlank()) {
                    assignment.setExpiredAt(LocalDateTime.parse(expiredAtStr.replace("Z", "")));
                }
            } else {
                assignment = new ProjectAssignment();
                assignment.setProject(project);
                assignment.setUser(dev);
                assignment.setNotes(notes);
                assignment.setActive(true);
                assignment.setAssignedBy(actor.getEmail());
                assignment.setAssignedAt(LocalDateTime.now());
                if (expiredAtStr != null && !expiredAtStr.isBlank()) {
                    assignment.setExpiredAt(LocalDateTime.parse(expiredAtStr.replace("Z", "")));
                }
            }

            ProjectAssignment saved = assignmentRepository.save(assignment);
            return ResponseEntity.status(HttpStatus.CREATED).body(saved);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }
}
