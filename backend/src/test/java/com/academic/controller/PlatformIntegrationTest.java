package com.academic.controller;

import com.academic.config.JwtTokenProvider;
import com.academic.model.*;
import com.academic.repository.*;
import com.academic.service.payment.SimulatedPaymentGateway;
import com.academic.service.storage.FileStorageService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

import java.io.ByteArrayInputStream;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * End-to-end checks of the multi-college platform against an in-memory database:
 * college isolation, privilege boundaries, marketplace scoping, server-side pricing,
 * preview vs full file access, payment integrity and the custom development lifecycle.
 */
@SpringBootTest
@AutoConfigureMockMvc
class PlatformIntegrationTest {

    @Autowired private MockMvc mvc;
    @Autowired private ObjectMapper json;
    @Autowired private JwtTokenProvider jwt;
    @Autowired private PasswordEncoder encoder;
    @Autowired private UserRepository users;
    @Autowired private CollegeRepository colleges;
    @Autowired private ProjectRepository projects;
    @Autowired private FolderRepository folders;
    @Autowired private AssetRepository assets;
    @Autowired private CollegeProjectAllocationRepository allocations;
    @Autowired private ProjectEntitlementRepository entitlements;
    @Autowired private FileStorageService storage;
    @Autowired private SimulatedPaymentGateway simulatedGateway;

    private String run;
    private College collegeA, collegeB;
    private User adminA, adminB, studentA, studentA2, studentB, developer, developer2;
    private Project library;
    private Asset previewAsset, protectedAsset;

    @BeforeEach
    void setUp() {
        run = UUID.randomUUID().toString().substring(0, 8);
        collegeA = college("Alpha Institute", "A" + run);
        collegeB = college("Beta College", "B" + run);
        adminA = user("admin-a", Role.ADMIN, collegeA);
        adminB = user("admin-b", Role.ADMIN, collegeB);
        studentA = user("student-a", Role.USER, collegeA);
        studentA2 = user("student-a2", Role.USER, collegeA);
        studentB = user("student-b", Role.USER, collegeB);
        developer = user("dev", Role.PROJECT_DEVELOPER, null);
        developer2 = user("dev2", Role.PROJECT_DEVELOPER, null);

        library = new Project();
        library.setProjectCode("LIB-" + run);
        library.setProjectName("Crop Yield Prediction " + run);
        library.setProjectType(ProjectType.LIBRARY);
        library.setCatalogStatus(CatalogStatus.PUBLISHED);
        library.setMarketplace(true);
        library.setStatus(ProjectStatus.COMPLETED);
        library.setLifecycleStatus(ProjectStatus.COMPLETED);
        library.setDomain("Forecasting & Analytics");
        library.setTechnologyStack("Python, scikit-learn");
        library.setPrice(new BigDecimal("2000.00"));
        library = projects.save(library);

        Folder docs = folders.save(new Folder("Documentation", null, library, "test"));
        previewAsset = asset(docs, "abstract.pdf", true, AssetCategory.DOCUMENTATION);
        protectedAsset = asset(docs, "source.zip", false, AssetCategory.SOURCE_CODE);

        CollegeProjectAllocation allocation = new CollegeProjectAllocation();
        allocation.setCollege(collegeA);
        allocation.setProject(library);
        allocation.setPriceOverride(new BigDecimal("1500.00"));
        allocation.setAllocatedBy("test");
        allocations.save(allocation);
    }

    // ------------------------------------------------------------------
    // College isolation and privilege boundaries
    // ------------------------------------------------------------------

    @Test
    @DisplayName("College admin sees only their own students and cannot manage other colleges")
    void collegeAdminIsolation() throws Exception {
        JsonNode list = body(mvc.perform(as(adminA, get("/api/users"))).andExpect(status().isOk()).andReturn());
        String emails = list.toString();
        assertTrue(emails.contains(studentA.getEmail()));
        assertFalse(emails.contains(studentB.getEmail()));

        mvc.perform(as(adminA, put("/api/users/" + studentB.getId()))
                        .contentType(MediaType.APPLICATION_JSON).content("{\"fullName\":\"Hijacked\"}"))
                .andExpect(status().isForbidden());
        mvc.perform(as(adminA, delete("/api/users/" + studentB.getId()))).andExpect(status().isForbidden());
        mvc.perform(as(adminA, get("/api/allocations/colleges/" + collegeB.getId()))).andExpect(status().isForbidden());
        mvc.perform(as(adminA, get("/api/colleges"))).andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("College admins only see audit entries from their own college")
    void auditLogIsCollegeScoped() throws Exception {
        mvc.perform(as(studentA, post("/api/marketplace/" + library.getId() + "/purchase"))).andExpect(status().isOk());
        mvc.perform(as(studentB, get("/api/marketplace"))).andExpect(status().isOk());
        String a = body(mvc.perform(as(adminA, get("/api/audit-logs"))).andExpect(status().isOk()).andReturn()).toString();
        assertTrue(a.contains(studentA.getEmail()));
        String b = body(mvc.perform(as(adminB, get("/api/audit-logs"))).andExpect(status().isOk()).andReturn()).toString();
        assertFalse(b.contains(studentA.getEmail()));
        mvc.perform(as(developer, get("/api/audit-logs"))).andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("Only the Super Admin can grant roles; nobody can mint a Super Admin")
    void privilegeEscalationBlocked() throws Exception {
        String superAdminBody = "{\"email\":\"x" + run + "@t.dev\",\"password\":\"Password123\",\"fullName\":\"X\",\"role\":\"SUPER_ADMIN\"}";
        mvc.perform(as(adminA, post("/api/users")).contentType(MediaType.APPLICATION_JSON).content(superAdminBody))
                .andExpect(status().isForbidden());
        mvc.perform(as(developer, post("/api/users")).contentType(MediaType.APPLICATION_JSON).content(superAdminBody))
                .andExpect(status().isForbidden());
        mvc.perform(as(superAdmin(), post("/api/users")).contentType(MediaType.APPLICATION_JSON).content(superAdminBody))
                .andExpect(status().isForbidden());

        String adminBody = "{\"email\":\"y" + run + "@t.dev\",\"password\":\"Password123\",\"fullName\":\"Y\",\"role\":\"ADMIN\"}";
        mvc.perform(as(adminA, post("/api/users")).contentType(MediaType.APPLICATION_JSON).content(adminBody))
                .andExpect(status().isForbidden());
        mvc.perform(as(adminA, put("/api/users/" + studentA.getId())).contentType(MediaType.APPLICATION_JSON).content("{\"role\":\"ADMIN\"}"))
                .andExpect(status().isForbidden());
        mvc.perform(as(studentA, put("/api/users/" + studentA.getId())).contentType(MediaType.APPLICATION_JSON).content("{\"role\":\"SUPER_ADMIN\"}"))
                .andExpect(status().isForbidden());

        // College admin creating a student lands in the admin's own college regardless of input
        String studentBody = "{\"email\":\"z" + run + "@t.dev\",\"password\":\"Password123\",\"fullName\":\"Z\",\"role\":\"USER\",\"collegeId\":\"" + collegeB.getId() + "\"}";
        JsonNode created = body(mvc.perform(as(adminA, post("/api/users")).contentType(MediaType.APPLICATION_JSON).content(studentBody))
                .andExpect(status().isCreated()).andReturn());
        assertEquals(collegeA.getId().longValue(), created.path("college").path("id").asLong());
    }

    @Test
    @DisplayName("Deactivated accounts are rejected immediately even with a valid token")
    void deactivatedTokenRejected() throws Exception {
        String token = token(studentA2);
        studentA2.setStatus(UserStatus.INACTIVE);
        users.save(studentA2);
        mvc.perform(get("/api/marketplace").header("Authorization", "Bearer " + token)).andExpect(status().isUnauthorized());
    }

    // ------------------------------------------------------------------
    // Marketplace and purchases
    // ------------------------------------------------------------------

    @Test
    @DisplayName("Students only see projects allocated to their college, at the college price")
    void marketplaceScopedToCollege() throws Exception {
        String a = body(mvc.perform(as(studentA, get("/api/marketplace"))).andExpect(status().isOk()).andReturn()).toString();
        assertTrue(a.contains(library.getProjectCode()));
        assertTrue(a.contains("1500"));

        String b = body(mvc.perform(as(studentB, get("/api/marketplace"))).andExpect(status().isOk()).andReturn()).toString();
        assertFalse(b.contains(library.getProjectCode()));
        mvc.perform(as(studentB, get("/api/marketplace/" + library.getId()))).andExpect(status().isForbidden());
        mvc.perform(as(studentB, post("/api/marketplace/" + library.getId() + "/purchase"))).andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("Purchase is priced on the server, grants access once, and replays idempotently")
    void purchaseFlow() throws Exception {
        String key = "k-" + run;
        JsonNode first = body(mvc.perform(as(studentA, post("/api/marketplace/" + library.getId() + "/purchase"))
                        .header("Idempotency-Key", key)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"amount\":1}"))
                .andExpect(status().isOk()).andReturn());
        assertEquals(1500.0, first.path("order").path("amount").asDouble(), 0.001);
        assertEquals("COMPLETED", first.path("order").path("paymentStatus").asText());
        assertTrue(first.path("order").path("simulatedPayment").asBoolean());
        assertTrue(entitlements.hasActive(studentA.getId(), library.getId()));

        JsonNode replay = body(mvc.perform(as(studentA, post("/api/marketplace/" + library.getId() + "/purchase")).header("Idempotency-Key", key))
                .andExpect(status().isOk()).andReturn());
        assertEquals(first.path("order").path("id").asLong(), replay.path("order").path("id").asLong());

        mvc.perform(as(studentA, post("/api/marketplace/" + library.getId() + "/purchase")))
                .andExpect(status().isBadRequest());

        // Another student's key is scoped to them, not shared
        mvc.perform(as(studentA2, post("/api/marketplace/" + library.getId() + "/purchase")).header("Idempotency-Key", key))
                .andExpect(status().isOk());
        assertTrue(entitlements.hasActive(studentA2.getId(), library.getId()));
    }

    @Test
    @DisplayName("Unpriced library projects cannot be published or bought")
    void unpricedProjectsCannotBePublishedOrBought() throws Exception {
        mvc.perform(as(superAdmin(), post("/api/library")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"Unpriced " + run + "\",\"catalogStatus\":\"PUBLISHED\"}"))
                .andExpect(status().isBadRequest());

        JsonNode draft = body(mvc.perform(as(superAdmin(), post("/api/library")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"Draft " + run + "\"}"))
                .andExpect(status().isCreated()).andReturn());
        long id = draft.path("id").asLong();
        mvc.perform(as(superAdmin(), patch("/api/library/" + id + "/catalog-status")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"PUBLISHED\"}"))
                .andExpect(status().isBadRequest());

        // Even if it slipped through (legacy data), purchase refuses a missing price.
        Project legacy = projects.findById(id).orElseThrow();
        legacy.setCatalogStatus(CatalogStatus.PUBLISHED);
        projects.save(legacy);
        CollegeProjectAllocation a = new CollegeProjectAllocation();
        a.setCollege(collegeA);
        a.setProject(legacy);
        a.setAllocatedBy("test");
        allocations.save(a);
        mvc.perform(as(studentA, post("/api/marketplace/" + id + "/purchase"))).andExpect(status().isBadRequest());
        assertFalse(entitlements.hasActive(studentA.getId(), id));
    }

    @Test
    @DisplayName("Without an enabled gateway, purchases fail with 503 and grant nothing")
    void paymentsDisabled() throws Exception {
        ReflectionTestUtils.setField(simulatedGateway, "enabled", false);
        try {
            mvc.perform(as(studentA, post("/api/marketplace/" + library.getId() + "/purchase")))
                    .andExpect(status().isServiceUnavailable());
            assertFalse(entitlements.hasActive(studentA.getId(), library.getId()));
        } finally {
            ReflectionTestUtils.setField(simulatedGateway, "enabled", true);
        }
    }

    // ------------------------------------------------------------------
    // Files
    // ------------------------------------------------------------------

    @Test
    @DisplayName("Preview files are visible before purchase; deliverables only after")
    void previewVersusFullFileAccess() throws Exception {
        mvc.perform(as(studentA, get("/api/assets/" + previewAsset.getId() + "/view"))).andExpect(status().isOk());
        mvc.perform(as(studentA, get("/api/assets/" + protectedAsset.getId() + "/view"))).andExpect(status().isForbidden());
        mvc.perform(as(studentB, get("/api/assets/" + previewAsset.getId() + "/view"))).andExpect(status().isForbidden());
        mvc.perform(as(adminA, get("/api/assets/" + protectedAsset.getId() + "/view"))).andExpect(status().isForbidden());

        mvc.perform(as(studentA, post("/api/marketplace/" + library.getId() + "/purchase"))).andExpect(status().isOk());

        mvc.perform(as(studentA, get("/api/assets/" + protectedAsset.getId() + "/view").param("download", "true")))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Disposition", org.hamcrest.Matchers.startsWith("attachment")));
        mvc.perform(as(studentA2, get("/api/assets/" + protectedAsset.getId() + "/view"))).andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("Students cannot change folder or file permissions")
    void permissionsAreSuperAdminOnly() throws Exception {
        mvc.perform(as(studentA, post("/api/permissions/files")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"assetId\":" + protectedAsset.getId() + ",\"role\":\"USER\",\"status\":\"ALLOWED\"}"))
                .andExpect(status().isForbidden());
    }

    // ------------------------------------------------------------------
    // Custom development lifecycle
    // ------------------------------------------------------------------

    @Test
    @DisplayName("Full custom development lifecycle with payment-gated delivery")
    void customDevelopmentLifecycle() throws Exception {
        // 1. Student drafts and submits
        JsonNode req = body(mvc.perform(as(studentA, post("/api/requirements")).contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(Map.of("title", "Smart Attendance " + run, "problemStatement", "Face recognition attendance", "budget", 10000))))
                .andExpect(status().isCreated()).andReturn());
        long reqId = req.path("id").asLong();
        assertEquals(collegeA.getId().longValue(), req.path("college").path("id").asLong());
        mvc.perform(as(studentA, post("/api/requirements/" + reqId + "/submit"))).andExpect(status().isOk());

        // Other college cannot see it; advance cannot be paid yet
        mvc.perform(as(adminB, get("/api/requirements/" + reqId))).andExpect(status().isForbidden());
        mvc.perform(as(studentB, get("/api/requirements/" + reqId))).andExpect(status().isForbidden());
        mvc.perform(as(studentA, post("/api/requirements/" + reqId + "/pay-advance"))).andExpect(status().isBadRequest());

        // 2-3. College admin forwards
        mvc.perform(as(adminB, post("/api/requirements/" + reqId + "/college-review")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"action\":\"FORWARD\"}"))
                .andExpect(status().isForbidden());
        mvc.perform(as(adminA, post("/api/requirements/" + reqId + "/college-review")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"action\":\"FORWARD\",\"notes\":\"Looks feasible\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("SUPER_ADMIN_REVIEW"));

        // Super Admin approves with a quote
        mvc.perform(as(adminA, post("/api/requirements/" + reqId + "/review")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"action\":\"APPROVE\",\"budget\":12000,\"advanceAmount\":4000}"))
                .andExpect(status().isForbidden());
        mvc.perform(as(superAdmin(), post("/api/requirements/" + reqId + "/review")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"action\":\"APPROVE\",\"budget\":12000,\"advanceAmount\":4000}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.requirement.status").value("ADVANCE_PAYMENT_PENDING"));

        // Advance: only the owner, at the quoted amount
        mvc.perform(as(studentA2, post("/api/requirements/" + reqId + "/pay-advance"))).andExpect(status().isForbidden());
        JsonNode adv = body(mvc.perform(as(studentA, post("/api/requirements/" + reqId + "/pay-advance"))
                        .contentType(MediaType.APPLICATION_JSON).content("{\"amount\":1}"))
                .andExpect(status().isOk()).andReturn());
        assertEquals(4000.0, adv.path("order").path("amount").asDouble(), 0.001);

        // 4. Super Admin starts development
        JsonNode project = body(mvc.perform(as(superAdmin(), post("/api/requirements/" + reqId + "/start-development"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"developerId\":" + developer.getId() + ",\"reviewerId\":" + adminA.getId() + "}"))
                .andExpect(status().isOk()).andReturn());
        long projectId = project.path("id").asLong();
        assertEquals("DEVELOPER_ASSIGNED", project.path("lifecycleStatus").asText());

        // Developer isolation
        mvc.perform(as(developer2, get("/api/projects/" + projectId))).andExpect(status().isForbidden());
        mvc.perform(as(developer2, post("/api/projects/" + projectId + "/accept"))).andExpect(status().isForbidden());

        // 5-6. Developer accepts and reports progress
        mvc.perform(as(developer, post("/api/projects/" + projectId + "/accept"))).andExpect(status().isOk())
                .andExpect(jsonPath("$.lifecycleStatus").value("IN_PROGRESS"));
        mvc.perform(as(developer, post("/api/projects/" + projectId + "/progress")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"percent\":60,\"note\":\"Model trained\"}"))
                .andExpect(status().isOk());

        // Cannot submit without deliverables
        mvc.perform(as(developer, post("/api/projects/" + projectId + "/developer-submit-review"))).andExpect(status().isBadRequest());

        // 7. Upload deliverable into the project's Source Code folder
        Folder sourceFolder = folders.findRootByNameAndProjectIdIgnoreCase(projectId, "Source Code").orElseThrow();
        mvc.perform(multipart("/api/assets/upload")
                        .file(new MockMultipartFile("file", "app.zip", "application/zip", "PK-zip".getBytes(StandardCharsets.UTF_8)))
                        .param("projectId", String.valueOf(projectId))
                        .param("folderId", String.valueOf(sourceFolder.getId()))
                        .header("Authorization", "Bearer " + token(developer)))
                .andExpect(status().isCreated());
        // College admin is read-only on files
        mvc.perform(multipart("/api/assets/upload")
                        .file(new MockMultipartFile("file", "evil.zip", "application/zip", "x".getBytes(StandardCharsets.UTF_8)))
                        .param("projectId", String.valueOf(projectId))
                        .param("folderId", String.valueOf(sourceFolder.getId()))
                        .header("Authorization", "Bearer " + token(adminA)))
                .andExpect(status().isForbidden());

        mvc.perform(as(developer, post("/api/projects/" + projectId + "/developer-submit-review")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"notes\":\"Ready\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.lifecycleStatus").value("READY_FOR_REVIEW"));

        // Final payment is not possible before review approval
        mvc.perform(as(studentA, post("/api/projects/" + projectId + "/pay-remaining"))).andExpect(status().isBadRequest());

        // 8-9. Reviewer requests changes, developer resubmits, reviewer approves
        mvc.perform(as(adminB, post("/api/projects/" + projectId + "/admin-review")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"action\":\"APPROVE\"}"))
                .andExpect(status().isForbidden());
        mvc.perform(as(adminA, post("/api/projects/" + projectId + "/admin-review")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"action\":\"REQUEST_CHANGES\",\"notes\":\"Add README\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.lifecycleStatus").value("CHANGES_REQUESTED"));
        mvc.perform(as(developer, post("/api/projects/" + projectId + "/developer-submit-review"))).andExpect(status().isOk());
        mvc.perform(as(adminA, post("/api/projects/" + projectId + "/admin-review")).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"action\":\"APPROVE\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.lifecycleStatus").value("READY_FOR_FINAL_PAYMENT"));

        // Before final payment the student has preview access only
        long deliverableId = assets.findCurrentAssetsByProjectId(projectId).get(0).getId();
        mvc.perform(as(studentA, get("/api/assets/" + deliverableId + "/view"))).andExpect(status().isForbidden());

        // 10-11. Only the requester can pay, at the remaining balance
        mvc.perform(as(studentB, post("/api/projects/" + projectId + "/pay-remaining"))).andExpect(status().isForbidden());
        mvc.perform(as(studentA2, post("/api/projects/" + projectId + "/pay-remaining"))).andExpect(status().isForbidden());
        JsonNode fin = body(mvc.perform(as(studentA, post("/api/projects/" + projectId + "/pay-remaining"))
                        .contentType(MediaType.APPLICATION_JSON).content("{\"amount\":0.01}"))
                .andExpect(status().isOk()).andReturn());
        assertEquals(8000.0, fin.path("order").path("amount").asDouble(), 0.001);

        // 12. Access granted to the requester only
        mvc.perform(as(studentA, get("/api/assets/" + deliverableId + "/view"))).andExpect(status().isOk());
        mvc.perform(as(studentA2, get("/api/assets/" + deliverableId + "/view"))).andExpect(status().isForbidden());
        mvc.perform(as(studentA, get("/api/requirements/" + reqId))).andExpect(jsonPath("$.status").value("COMPLETED"));

        // Timeline recorded every step
        JsonNode timeline = body(mvc.perform(as(studentA, get("/api/projects/" + projectId + "/timeline"))).andExpect(status().isOk()).andReturn());
        assertTrue(timeline.size() >= 7, "timeline entries: " + timeline.size());
    }

    @Test
    @DisplayName("Role dashboards return live metrics for each role")
    void dashboards() throws Exception {
        mvc.perform(as(superAdmin(), get("/api/dashboard"))).andExpect(status().isOk()).andExpect(jsonPath("$.role").value("SUPER_ADMIN"))
                .andExpect(jsonPath("$.colleges").isNumber());
        mvc.perform(as(adminA, get("/api/dashboard"))).andExpect(status().isOk()).andExpect(jsonPath("$.college.id").value(collegeA.getId()))
                .andExpect(jsonPath("$.allocatedProjects").value(1));
        mvc.perform(as(developer, get("/api/dashboard"))).andExpect(status().isOk()).andExpect(jsonPath("$.role").value("PROJECT_DEVELOPER"));
        mvc.perform(as(studentA, get("/api/dashboard"))).andExpect(status().isOk()).andExpect(jsonPath("$.availableProjects").value(1));
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    private College college(String name, String code) {
        College c = new College();
        c.setName(name + " " + code);
        c.setCode(code);
        return colleges.save(c);
    }

    private User user(String prefix, Role role, College college) {
        User u = new User(prefix + "-" + run + "@test.dev", encoder.encode("Password123"), prefix + " " + run, role, UserStatus.ACTIVE);
        u.setCollege(college);
        return users.save(u);
    }

    private User superAdmin() {
        return users.findByEmailAndDeletedFalse("superadmin@academic.com").orElseThrow();
    }

    private Asset asset(Folder folder, String name, boolean previewable, AssetCategory category) {
        String path = storage.storeFile(new ByteArrayInputStream(("content of " + name).getBytes(StandardCharsets.UTF_8)), name, library.getId(), folder.getId());
        Asset a = new Asset(folder, name, name, "application/octet-stream", name.substring(name.lastIndexOf('.') + 1), 16L, path, 1, true, null, null, "test");
        a.setPreviewable(previewable);
        a.setCategory(category);
        return assets.save(a);
    }

    private String token(User u) {
        return jwt.generateToken(u.getEmail(), u.getRole().name());
    }

    private MockHttpServletRequestBuilder as(User u, MockHttpServletRequestBuilder builder) {
        return builder.header("Authorization", "Bearer " + token(u));
    }

    private JsonNode body(MvcResult result) throws Exception {
        return json.readTree(result.getResponse().getContentAsString());
    }
}
