package com.academic.service;

import com.academic.dto.CollegeRequest;
import com.academic.model.*;
import com.academic.repository.CollegeProjectAllocationRepository;
import com.academic.repository.CollegeRepository;
import com.academic.repository.OrderRepository;
import com.academic.repository.RequirementRepository;
import com.academic.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.regex.Pattern;

@Service
public class CollegeService {

    private static final Pattern EMAIL = Pattern.compile("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");

    @Autowired
    private CollegeRepository collegeRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private CollegeProjectAllocationRepository allocationRepository;

    @Autowired
    private RequirementRepository requirementRepository;

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private AuditLogService auditLogService;

    public List<Map<String, Object>> listWithStats() {
        List<Map<String, Object>> result = new ArrayList<>();
        for (College college : collegeRepository.findAllByOrderByNameAsc()) {
            result.add(summary(college));
        }
        return result;
    }

    /** Minimal list for registration and selection dropdowns. */
    public List<Map<String, Object>> activeOptions() {
        List<Map<String, Object>> result = new ArrayList<>();
        for (College c : collegeRepository.findByActiveTrueOrderByNameAsc()) {
            result.add(Map.of("id", c.getId(), "name", c.getName(), "code", c.getCode(), "city", c.getCity() != null ? c.getCity() : ""));
        }
        return result;
    }

    public College get(Long id) {
        return collegeRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("College not found with ID: " + id));
    }

    public Map<String, Object> detail(Long id) {
        College college = get(id);
        Map<String, Object> detail = summary(college);
        detail.put("admins", userRepository.findAdminsByCollegeId(id));
        return detail;
    }

    @Transactional
    public College create(CollegeRequest req, String actorEmail) {
        String code = req.getCode().trim().toUpperCase();
        if (collegeRepository.existsByCodeIgnoreCase(code)) {
            throw new IllegalArgumentException("A college with code " + code + " already exists.");
        }
        College college = new College();
        apply(college, req);
        college.setCode(code);
        college.setActive(req.getActive() == null || req.getActive());
        college.setCreatedBy(actorEmail);
        College saved = collegeRepository.save(college);
        auditLogService.log(actorEmail, "COLLEGE_CREATED", "Registered college " + saved.getName() + " (" + saved.getCode() + ")");
        return saved;
    }

    @Transactional
    public College update(Long id, CollegeRequest req, String actorEmail) {
        College college = get(id);
        String code = req.getCode().trim().toUpperCase();
        collegeRepository.findByCodeIgnoreCase(code)
                .filter(other -> !other.getId().equals(id))
                .ifPresent(other -> { throw new IllegalArgumentException("A college with code " + code + " already exists."); });
        apply(college, req);
        college.setCode(code);
        if (req.getActive() != null) {
            college.setActive(req.getActive());
        }
        College saved = collegeRepository.save(college);
        auditLogService.log(actorEmail, "COLLEGE_UPDATED", "Updated college " + saved.getName() + " (" + saved.getCode() + ")");
        return saved;
    }

    @Transactional
    public College setActive(Long id, boolean active, String actorEmail) {
        College college = get(id);
        college.setActive(active);
        College saved = collegeRepository.save(college);
        auditLogService.log(actorEmail, active ? "COLLEGE_ACTIVATED" : "COLLEGE_DEACTIVATED", saved.getName() + " (" + saved.getCode() + ")");
        return saved;
    }

    /** Creates a new college administrator account bound to the college. */
    @Transactional
    public User createCollegeAdmin(Long collegeId, String fullName, String email, String password, String mobile, String actorEmail) {
        College college = get(collegeId);
        String normalized = email != null ? email.trim().toLowerCase() : "";
        if (fullName == null || fullName.isBlank()) {
            throw new IllegalArgumentException("Full name is required.");
        }
        if (!EMAIL.matcher(normalized).matches()) {
            throw new IllegalArgumentException("Please provide a valid email address.");
        }
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters long.");
        }
        if (userRepository.existsByEmailAndDeletedFalse(normalized)) {
            throw new IllegalArgumentException("An account with email " + normalized + " already exists.");
        }
        User admin = new User(normalized, passwordEncoder.encode(password), fullName.trim(), Role.ADMIN, UserStatus.ACTIVE);
        admin.setCollege(college);
        admin.setMobileNumber(mobile);
        admin.setOrganization(college.getName());
        User saved = userRepository.save(admin);
        auditLogService.log(actorEmail, "COLLEGE_ADMIN_CREATED",
                "Created college administrator " + saved.getEmail() + " for " + college.getName());
        return saved;
    }

    /** Moves an existing ADMIN or USER account into a college. */
    @Transactional
    public User assignUserToCollege(Long collegeId, Long userId, String actorEmail) {
        College college = get(collegeId);
        User user = userRepository.findById(userId).filter(u -> !u.isDeleted())
                .orElseThrow(() -> new NoSuchElementException("User not found with ID: " + userId));
        if (user.getRole() != Role.ADMIN && user.getRole() != Role.USER) {
            throw new IllegalArgumentException("Only college administrators and students belong to a college.");
        }
        user.setCollege(college);
        User saved = userRepository.save(user);
        auditLogService.log(actorEmail, "USER_COLLEGE_ASSIGNED", saved.getEmail() + " assigned to " + college.getName());
        return saved;
    }

    public List<User> students(Long collegeId, String search) {
        get(collegeId);
        return userRepository.searchByCollegeAndRole(collegeId, Role.USER, null, blankToNull(search));
    }

    private Map<String, Object> summary(College college) {
        Long id = college.getId();
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", id);
        m.put("name", college.getName());
        m.put("code", college.getCode());
        m.put("city", college.getCity());
        m.put("state", college.getState());
        m.put("contactEmail", college.getContactEmail());
        m.put("contactPhone", college.getContactPhone());
        m.put("address", college.getAddress());
        m.put("active", college.isActive());
        m.put("createdAt", college.getCreatedAt());
        m.put("adminCount", userRepository.countByCollegeAndRole(id, Role.ADMIN));
        m.put("studentCount", userRepository.countByCollegeAndRole(id, Role.USER));
        m.put("allocatedProjects", allocationRepository.countActiveByCollegeId(id));
        m.put("requirementCount", requirementRepository.countByCollege(id));
        m.put("orderCount", orderRepository.countByCollegeId(id));
        return m;
    }

    private static void apply(College college, CollegeRequest req) {
        college.setName(req.getName().trim());
        college.setCity(trim(req.getCity()));
        college.setState(trim(req.getState()));
        college.setContactEmail(trim(req.getContactEmail()));
        college.setContactPhone(trim(req.getContactPhone()));
        college.setAddress(trim(req.getAddress()));
    }

    private static String trim(String s) {
        return s == null ? null : (s.isBlank() ? null : s.trim());
    }

    private static String blankToNull(String s) {
        return s == null || s.isBlank() ? null : s.trim();
    }
}
