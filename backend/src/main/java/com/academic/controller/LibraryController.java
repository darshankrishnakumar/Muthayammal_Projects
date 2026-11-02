package com.academic.controller;

import com.academic.dto.AssetResponse;
import com.academic.dto.LibraryProjectRequest;
import com.academic.model.*;
import com.academic.service.*;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/** Central project library management. Super Admin only. */
@RestController
@RequestMapping("/api/library")
@PreAuthorize("hasRole('SUPER_ADMIN')")
public class LibraryController {

    @Autowired
    private LibraryService libraryService;

    @Autowired
    private LibraryImportService importService;

    @Autowired
    private AssetService assetService;

    @Autowired
    private FolderService folderService;

    @Autowired
    private AccessControlService accessControlService;

    @GetMapping
    public List<Map<String, Object>> list(@RequestParam(required = false) String search,
                                          @RequestParam(required = false) String status,
                                          @RequestParam(required = false) String domain) {
        return libraryService.list(search, status, domain);
    }

    @GetMapping("/stats")
    public Map<String, Object> stats() {
        return libraryService.stats();
    }

    @GetMapping("/{id}")
    public Map<String, Object> detail(@PathVariable Long id) {
        return libraryService.detail(id);
    }

    @PostMapping
    public ResponseEntity<Project> create(@Valid @RequestBody LibraryProjectRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(libraryService.create(request, actorEmail()));
    }

    @PutMapping("/{id}")
    public Project update(@PathVariable Long id, @Valid @RequestBody LibraryProjectRequest request) {
        return libraryService.update(id, request, actorEmail());
    }

    @PatchMapping("/{id}/catalog-status")
    public Project setCatalogStatus(@PathVariable Long id, @RequestBody Map<String, String> body) {
        return libraryService.setCatalogStatus(id, body.get("status"), actorEmail());
    }

    @PostMapping("/bulk-status")
    public Map<String, Object> bulkStatus(@RequestBody Map<String, Object> body) {
        @SuppressWarnings("unchecked")
        List<Number> ids = (List<Number>) body.getOrDefault("projectIds", List.of());
        int updated = libraryService.bulkSetCatalogStatus(ids.stream().map(Number::longValue).toList(),
                String.valueOf(body.get("status")), actorEmail());
        return Map.of("updated", updated);
    }

    /**
     * Uploads a file into the category folder of a library project
     * (Documentation, Source Code, Database, Demo Video, Screenshots, Presentation, Resources).
     */
    @PostMapping(value = "/{id}/files", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<AssetResponse> uploadFile(@PathVariable Long id,
                                                    @RequestParam("file") MultipartFile file,
                                                    @RequestParam(value = "category", defaultValue = "OTHER") String category,
                                                    @RequestParam(value = "previewable", defaultValue = "false") boolean previewable,
                                                    @RequestParam(value = "description", required = false) String description) {
        String actor = actorEmail();
        Project project = libraryService.getLibraryProject(id);
        AssetCategory cat = AssetCategory.valueOf(category.trim().toUpperCase());
        Folder folder = libraryService.ensureCategoryFolders(project, actor).get(cat);
        AssetResponse uploaded = assetService.uploadAsset(project.getId(), folder.getId(), file, description, actor);
        libraryService.updateAssetMetadata(uploaded.getId(), cat.name(), previewable, actor);
        uploaded.setCategory(cat.name());
        uploaded.setPreviewable(previewable);
        return ResponseEntity.status(HttpStatus.CREATED).body(uploaded);
    }

    @PatchMapping("/assets/{assetId}")
    public AssetResponse updateAsset(@PathVariable Long assetId, @RequestBody Map<String, Object> body) {
        Object previewable = body.get("previewable");
        Asset asset = libraryService.updateAssetMetadata(assetId,
                body.get("category") != null ? body.get("category").toString() : null,
                previewable != null ? Boolean.valueOf(previewable.toString()) : null,
                actorEmail());
        return folderService.mapToAssetResponse(asset);
    }

    // ---------------- Repository import ----------------

    @GetMapping("/import/scan")
    public Map<String, Object> scan() {
        return importService.scan();
    }

    @PostMapping("/import")
    public Map<String, Object> startImport(@RequestBody(required = false) Map<String, Object> body) {
        @SuppressWarnings("unchecked")
        List<String> dirs = body != null ? (List<String>) body.get("directories") : null;
        BigDecimal price = body != null && body.get("defaultPrice") != null && !body.get("defaultPrice").toString().isBlank()
                ? new BigDecimal(body.get("defaultPrice").toString()) : null;
        boolean publish = body != null && Boolean.parseBoolean(String.valueOf(body.get("publish")));
        boolean refresh = body != null && Boolean.parseBoolean(String.valueOf(body.get("refreshMetadata")));
        return importService.start(dirs, price, publish, refresh, actorEmail());
    }

    @GetMapping("/import/status")
    public Map<String, Object> importStatus() {
        return importService.status();
    }

    private String actorEmail() {
        return accessControlService.getCurrentAuthenticatedUser().getEmail();
    }
}
