package com.academic.controller;

import com.academic.dto.FolderRequest;
import com.academic.dto.FolderResponse;
import com.academic.service.FolderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/projects")
public class FolderController {

    @Autowired
    private FolderService folderService;

    /**
     * Exact Required API: GET /api/projects/{id}/folders
     * Retrieves folder hierarchy and contents for a project.
     */
    @GetMapping("/{id}/folders")
    public ResponseEntity<List<FolderResponse>> getProjectFolders(@PathVariable("id") Long projectId) {
        List<FolderResponse> folders = folderService.getProjectFolders(projectId);
        return ResponseEntity.ok(folders);
    }

    /**
     * Exact Required API: POST /api/projects/{id}/folders
     * Creates a new folder (root or nested) in a project.
     */
    @PostMapping("/{id}/folders")
    public ResponseEntity<FolderResponse> createFolder(
            @PathVariable("id") Long projectId,
            @RequestBody FolderRequest request,
            Authentication authentication) {
        String actorEmail = authentication != null ? authentication.getName() : "system";
        FolderResponse created = folderService.createFolder(projectId, request, actorEmail);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    /**
     * Supporting API: GET /api/projects/{id}/folders/{folderId}
     * Retrieves details for a specific folder including breadcrumbs, subfolders, and files.
     */
    @GetMapping("/{id}/folders/{folderId}")
    public ResponseEntity<FolderResponse> getFolderDetails(
            @PathVariable("id") Long projectId,
            @PathVariable("folderId") Long folderId) {
        FolderResponse folder = folderService.getFolderDetails(projectId, folderId);
        return ResponseEntity.ok(folder);
    }

    /**
     * Supporting API: PUT /api/projects/{id}/folders/{folderId}
     * Renames or moves a folder.
     */
    @PutMapping("/{id}/folders/{folderId}")
    public ResponseEntity<FolderResponse> updateFolder(
            @PathVariable("id") Long projectId,
            @PathVariable("folderId") Long folderId,
            @RequestBody FolderRequest request,
            Authentication authentication) {
        String actorEmail = authentication != null ? authentication.getName() : "system";
        FolderResponse updated = folderService.updateFolder(projectId, folderId, request, actorEmail);
        return ResponseEntity.ok(updated);
    }

    /**
     * Supporting API: DELETE /api/projects/{id}/folders/{folderId}
     * Deactivates/deletes a folder.
     */
    @DeleteMapping("/{id}/folders/{folderId}")
    public ResponseEntity<?> deleteFolder(
            @PathVariable("id") Long projectId,
            @PathVariable("folderId") Long folderId,
            Authentication authentication) {
        String actorEmail = authentication != null ? authentication.getName() : "system";
        folderService.deleteFolder(projectId, folderId, actorEmail);
        return ResponseEntity.ok().body("{\"message\": \"Folder deactivated successfully.\"}");
    }
}
