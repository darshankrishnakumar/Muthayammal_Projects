package com.academic.controller;

import com.academic.dto.AssetResponse;
import com.academic.dto.AssetVersionDto;
import com.academic.service.AssetService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/assets")
@CrossOrigin(origins = "*")
public class AssetController {

    @Autowired
    private AssetService assetService;

    /**
     * Exact Required API: POST /api/assets/upload
     * Uploads a file with full backend validations to private storage and MySQL metadata.
     */
    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<AssetResponse> uploadAsset(
            @RequestParam("projectId") Long projectId,
            @RequestParam("folderId") Long folderId,
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "description", required = false) String description,
            Authentication authentication) {
        String actorEmail = authentication != null ? authentication.getName() : "system";
        AssetResponse response = assetService.uploadAsset(projectId, folderId, file, description, actorEmail);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Exact Required API: GET /api/assets/{id}/view
     * Streams asset content inline for the secure viewer after the 4-tier server authorization check.
     */
    @GetMapping("/{id}/view")
    public ResponseEntity<Resource> viewAsset(
            @PathVariable("id") Long assetId,
            @RequestParam(value = "version", required = false) Integer versionNo) {
        Map<String, Object> viewData = assetService.getAssetForSecureView(assetId, versionNo);

        Resource resource = (Resource) viewData.get("resource");
        String mimeType = (String) viewData.get("mimeType");
        String fileName = (String) viewData.get("fileName");

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(mimeType != null ? mimeType : "application/octet-stream"))
                .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + fileName + "\"")
                .header(HttpHeaders.CACHE_CONTROL, "no-cache, no-store, must-revalidate")
                .header(HttpHeaders.PRAGMA, "no-cache")
                .header(HttpHeaders.EXPIRES, "0")
                .header("X-Content-Type-Options", "nosniff")
                .body(resource);
    }

    /**
     * Exact Required API: PUT /api/assets/{id}/replace
     * Replaces an asset by uploading a new version (v1 -> v2) retaining version history.
     */
    @PutMapping(value = "/{id}/replace", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<AssetResponse> replaceAsset(
            @PathVariable("id") Long assetId,
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "changeNotes", required = false) String changeNotes,
            Authentication authentication) {
        String actorEmail = authentication != null ? authentication.getName() : "system";
        AssetResponse response = assetService.replaceAsset(assetId, file, changeNotes, actorEmail);
        return ResponseEntity.ok(response);
    }

    /**
     * Supporting API: GET /api/assets/{id}/versions
     * Retrieves version history list for an asset.
     */
    @GetMapping("/{id}/versions")
    public ResponseEntity<List<AssetVersionDto>> getVersionHistory(@PathVariable("id") Long assetId) {
        List<AssetVersionDto> history = assetService.getVersionHistory(assetId);
        return ResponseEntity.ok(history);
    }

    /**
     * Supporting API: POST /api/assets/{id}/restore/{versionNo}
     * Restores a superseded version as the active version.
     */
    @PostMapping("/{id}/restore/{versionNo}")
    public ResponseEntity<AssetResponse> restoreVersion(
            @PathVariable("id") Long assetId,
            @PathVariable("versionNo") Integer versionNo,
            Authentication authentication) {
        String actorEmail = authentication != null ? authentication.getName() : "system";
        AssetResponse response = assetService.restoreVersion(assetId, versionNo, actorEmail);
        return ResponseEntity.ok(response);
    }
}
