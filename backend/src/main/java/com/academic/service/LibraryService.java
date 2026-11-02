package com.academic.service;

import com.academic.dto.LibraryProjectRequest;
import com.academic.model.*;
import com.academic.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

/**
 * Central project library owned by the Super Admin. Each project is stored once; colleges
 * receive it through allocations (see {@link AllocationService}).
 */
@Service
public class LibraryService {

    /** Root folder used for each file category in a library project. */
    public static final Map<AssetCategory, String> CATEGORY_FOLDERS = Map.of(
            AssetCategory.DOCUMENTATION, "Documentation",
            AssetCategory.SOURCE_CODE, "Source Code",
            AssetCategory.DATABASE, "Database",
            AssetCategory.VIDEO, "Demo Video",
            AssetCategory.SCREENSHOT, "Screenshots",
            AssetCategory.PRESENTATION, "Presentation",
            AssetCategory.OTHER, "Resources"
    );

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private FolderRepository folderRepository;

    @Autowired
    private AssetRepository assetRepository;

    @Autowired
    private CollegeProjectAllocationRepository allocationRepository;

    @Autowired
    private ProjectEntitlementRepository entitlementRepository;

    @Autowired
    private AuditLogService auditLogService;

    @Transactional(readOnly = true)
    public List<Map<String, Object>> list(String search, String status, String domain) {
        CatalogStatus catalogStatus = parseStatus(status, true);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (Project p : projectRepository.searchLibrary(blank(search), catalogStatus, blank(domain))) {
            rows.add(row(p));
        }
        return rows;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> stats() {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("total", projectRepository.countByProjectType(ProjectType.LIBRARY));
        m.put("published", projectRepository.countByProjectTypeAndCatalogStatus(ProjectType.LIBRARY, CatalogStatus.PUBLISHED));
        m.put("draft", projectRepository.countByProjectTypeAndCatalogStatus(ProjectType.LIBRARY, CatalogStatus.DRAFT));
        m.put("archived", projectRepository.countByProjectTypeAndCatalogStatus(ProjectType.LIBRARY, CatalogStatus.ARCHIVED));
        m.put("allocatedProjects", allocationRepository.countDistinctAllocatedProjects());
        m.put("activeAllocations", allocationRepository.countByActiveTrue());
        m.put("domains", projectRepository.findLibraryDomains());
        return m;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> detail(Long id) {
        Project p = getLibraryProject(id);
        Map<String, Object> m = row(p);
        m.put("allocations", allocationRepository.findActiveByProjectId(id).stream().map(a -> {
            Map<String, Object> am = new LinkedHashMap<>();
            am.put("allocationId", a.getId());
            am.put("collegeId", a.getCollege().getId());
            am.put("collegeName", a.getCollege().getName());
            am.put("collegeCode", a.getCollege().getCode());
            am.put("priceOverride", a.getPriceOverride());
            am.put("effectivePrice", a.getEffectivePrice());
            am.put("allocatedAt", a.getAllocatedAt());
            return am;
        }).toList());
        return m;
    }

    @Transactional
    public Project create(LibraryProjectRequest req, String actorEmail) {
        String code = req.getCode() != null && !req.getCode().isBlank()
                ? req.getCode().trim().toUpperCase()
                : nextLibraryCode();
        if (projectRepository.existsByProjectCode(code)) {
            throw new IllegalArgumentException("Project code " + code + " is already in use.");
        }
        Project p = new Project();
        p.setProjectCode(code);
        p.setProjectType(ProjectType.LIBRARY);
        p.setMarketplace(true);
        p.setStatus(ProjectStatus.COMPLETED);
        p.setLifecycleStatus(ProjectStatus.COMPLETED);
        p.setProgressPercent(100);
        p.setCreatedBy(actorEmail);
        apply(p, req);
        p.setCatalogStatus(parseStatus(req.getCatalogStatus(), false) != null ? parseStatus(req.getCatalogStatus(), false) : CatalogStatus.DRAFT);
        Project saved = projectRepository.save(p);
        ensureCategoryFolders(saved, actorEmail);
        auditLogService.log(actorEmail, "LIBRARY_PROJECT_CREATED", "Added " + saved.getProjectCode() + " (" + saved.getProjectName() + ") to the library");
        return saved;
    }

    @Transactional
    public Project update(Long id, LibraryProjectRequest req, String actorEmail) {
        Project p = getLibraryProject(id);
        apply(p, req);
        if (req.getCode() != null && !req.getCode().isBlank() && !req.getCode().trim().equalsIgnoreCase(p.getProjectCode())) {
            String code = req.getCode().trim().toUpperCase();
            if (projectRepository.existsByProjectCode(code)) {
                throw new IllegalArgumentException("Project code " + code + " is already in use.");
            }
            p.setProjectCode(code);
        }
        CatalogStatus status = parseStatus(req.getCatalogStatus(), false);
        if (status != null) {
            p.setCatalogStatus(status);
        }
        p.setUpdatedBy(actorEmail);
        Project saved = projectRepository.save(p);
        auditLogService.log(actorEmail, "LIBRARY_PROJECT_UPDATED", "Updated " + saved.getProjectCode());
        return saved;
    }

    @Transactional
    public Project setCatalogStatus(Long id, String status, String actorEmail) {
        Project p = getLibraryProject(id);
        CatalogStatus next = parseStatus(status, false);
        if (next == null) {
            throw new IllegalArgumentException("Catalog status is required (DRAFT, PUBLISHED or ARCHIVED).");
        }
        CatalogStatus previous = p.getCatalogStatus();
        p.setCatalogStatus(next);
        p.setUpdatedBy(actorEmail);
        Project saved = projectRepository.save(p);
        auditLogService.log(actorEmail, "LIBRARY_PROJECT_" + next.name(),
                saved.getProjectCode() + " catalog status " + previous + " -> " + next);
        return saved;
    }

    @Transactional
    public int bulkSetCatalogStatus(List<Long> ids, String status, String actorEmail) {
        int n = 0;
        for (Long id : ids) {
            setCatalogStatus(id, status, actorEmail);
            n++;
        }
        return n;
    }

    @Transactional
    public Asset updateAssetMetadata(Long assetId, String category, Boolean previewable, String actorEmail) {
        Asset asset = assetRepository.findByIdAndActiveTrue(assetId)
                .orElseThrow(() -> new NoSuchElementException("Asset not found with ID: " + assetId));
        if (category != null && !category.isBlank()) {
            asset.setCategory(AssetCategory.valueOf(category.trim().toUpperCase()));
        }
        if (previewable != null) {
            asset.setPreviewable(previewable);
        }
        Asset saved = assetRepository.save(asset);
        auditLogService.log(actorEmail, "ASSET_METADATA_UPDATED",
                String.format("Asset '%s' category=%s previewable=%s", saved.getOriginalFileName(), saved.getCategory(), saved.isPreviewable()));
        return saved;
    }

    /** Ensures the standard category folders exist and returns them keyed by category. */
    @Transactional
    public Map<AssetCategory, Folder> ensureCategoryFolders(Project project, String actorEmail) {
        Map<AssetCategory, Folder> folders = new EnumMap<>(AssetCategory.class);
        for (Map.Entry<AssetCategory, String> e : CATEGORY_FOLDERS.entrySet()) {
            Folder folder = folderRepository.findRootByNameAndProjectIdIgnoreCase(project.getId(), e.getValue())
                    .orElseGet(() -> folderRepository.save(new Folder(e.getValue(), null, project, actorEmail)));
            folders.put(e.getKey(), folder);
        }
        return folders;
    }

    public Project getLibraryProject(Long id) {
        Project p = projectRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Project not found with ID: " + id));
        if (!p.isLibrary()) {
            throw new IllegalArgumentException("Project " + p.getProjectCode() + " is not a library project.");
        }
        return p;
    }

    public String nextLibraryCode() {
        long n = projectRepository.countByProjectType(ProjectType.LIBRARY) + 1;
        String code;
        do {
            code = String.format("LIB-%03d", n++);
        } while (projectRepository.existsByProjectCode(code));
        return code;
    }

    private Map<String, Object> row(Project p) {
        List<Asset> assets = assetRepository.findCurrentAssetsByProjectId(p.getId());
        Map<String, Long> byCategory = new TreeMap<>();
        long totalBytes = 0;
        for (Asset a : assets) {
            byCategory.merge(a.getCategory() != null ? a.getCategory().name() : "OTHER", 1L, Long::sum);
            totalBytes += a.getFileSize() != null ? a.getFileSize() : 0;
        }
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", p.getId());
        m.put("projectCode", p.getProjectCode());
        m.put("projectName", p.getProjectName());
        m.put("abstractText", p.getAbstractText());
        m.put("description", p.getDescription());
        m.put("technologyStack", p.getTechnologyStack());
        m.put("domain", p.getDomain());
        m.put("tags", p.getTags());
        m.put("price", p.getPrice());
        m.put("installationInstructions", p.getInstallationInstructions());
        m.put("catalogStatus", p.getCatalogStatus());
        m.put("sourceRef", p.getSourceRef());
        m.put("createdAt", p.getCreatedAt());
        m.put("updatedAt", p.getUpdatedAt());
        m.put("fileCount", assets.size());
        m.put("totalBytes", totalBytes);
        m.put("filesByCategory", byCategory);
        m.put("hasDemoVideo", byCategory.containsKey(AssetCategory.VIDEO.name()));
        m.put("hasSourceCode", byCategory.containsKey(AssetCategory.SOURCE_CODE.name()));
        m.put("allocatedColleges", allocationRepository.findActiveByProjectId(p.getId()).size());
        m.put("entitledUsers", entitlementRepository.countActiveByProjectId(p.getId()));
        return m;
    }

    private static void apply(Project p, LibraryProjectRequest req) {
        p.setProjectName(req.getTitle().trim());
        p.setAbstractText(req.getAbstractText());
        p.setDescription(req.getDescription());
        p.setTechnologyStack(req.getTechnologyStack());
        p.setDomain(blank(req.getDomain()));
        p.setTags(req.getTags());
        p.setPrice(req.getPrice());
        p.setBudget(req.getPrice());
        p.setInstallationInstructions(req.getInstallationInstructions());
    }

    private static CatalogStatus parseStatus(String status, boolean allowAll) {
        if (status == null || status.isBlank() || (allowAll && "ALL".equalsIgnoreCase(status))) {
            return null;
        }
        try {
            return CatalogStatus.valueOf(status.trim().toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Unknown catalog status: " + status);
        }
    }

    private static String blank(String s) {
        return s == null || s.isBlank() ? null : s.trim();
    }
}
