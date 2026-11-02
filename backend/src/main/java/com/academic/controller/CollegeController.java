package com.academic.controller;

import com.academic.dto.CollegeRequest;
import com.academic.model.College;
import com.academic.model.User;
import com.academic.service.AccessControlService;
import com.academic.service.CollegeService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** College registry. Super Admin only (also enforced in SecurityConfig). */
@RestController
@RequestMapping("/api/colleges")
@PreAuthorize("hasRole('SUPER_ADMIN')")
public class CollegeController {

    @Autowired
    private CollegeService collegeService;

    @Autowired
    private AccessControlService accessControlService;

    @GetMapping
    public List<Map<String, Object>> list() {
        return collegeService.listWithStats();
    }

    @GetMapping("/{id}")
    public Map<String, Object> detail(@PathVariable Long id) {
        return collegeService.detail(id);
    }

    @PostMapping
    public ResponseEntity<College> create(@Valid @RequestBody CollegeRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(collegeService.create(request, actorEmail()));
    }

    @PutMapping("/{id}")
    public College update(@PathVariable Long id, @Valid @RequestBody CollegeRequest request) {
        return collegeService.update(id, request, actorEmail());
    }

    @PatchMapping("/{id}/status")
    public College setStatus(@PathVariable Long id, @RequestBody Map<String, Boolean> body) {
        Boolean active = body.get("active");
        if (active == null) {
            throw new IllegalArgumentException("'active' is required.");
        }
        return collegeService.setActive(id, active, actorEmail());
    }

    @PostMapping("/{id}/admins")
    public ResponseEntity<User> createAdmin(@PathVariable Long id, @RequestBody Map<String, String> body) {
        User admin = collegeService.createCollegeAdmin(id, body.get("fullName"), body.get("email"), body.get("password"),
                body.get("mobileNumber"), actorEmail());
        return ResponseEntity.status(HttpStatus.CREATED).body(admin);
    }

    @PostMapping("/{id}/members/{userId}")
    public User assignMember(@PathVariable Long id, @PathVariable Long userId) {
        return collegeService.assignUserToCollege(id, userId, actorEmail());
    }

    @GetMapping("/{id}/students")
    public List<User> students(@PathVariable Long id, @RequestParam(required = false) String search) {
        return collegeService.students(id, search);
    }

    private String actorEmail() {
        return accessControlService.getCurrentAuthenticatedUser().getEmail();
    }
}
