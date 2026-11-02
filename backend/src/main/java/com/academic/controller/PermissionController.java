package com.academic.controller;

import com.academic.model.*;
import com.academic.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/permissions")
@SuppressWarnings("null")
public class PermissionController {

    @Autowired
    private FolderPermissionRepository folderPermissionRepository;

    @Autowired
    private FilePermissionRepository filePermissionRepository;

    @Autowired
    private FolderRepository folderRepository;

    @Autowired
    private AssetRepository assetRepository;

    @Autowired
    private UserRepository userRepository;

    // --- FOLDER PERMISSIONS ---

    @GetMapping("/folders/{folderId}")
    public ResponseEntity<List<FolderPermission>> getFolderPermissions(@PathVariable Long folderId) {
        return ResponseEntity.ok(folderPermissionRepository.findByFolderId(folderId));
    }

    @PostMapping("/folders")
    public ResponseEntity<?> setFolderPermission(@RequestBody Map<String, Object> body) {
        Long folderId = Long.valueOf(body.get("folderId").toString());
        String statusStr = body.getOrDefault("status", "ALLOWED").toString();
        PermissionStatus status = PermissionStatus.valueOf(statusStr);

        Folder folder = folderRepository.findById(folderId)
                .orElseThrow(() -> new IllegalArgumentException("Folder not found"));

        FolderPermission perm;
        if (body.get("userId") != null && !body.get("userId").toString().isEmpty()) {
            Long userId = Long.valueOf(body.get("userId").toString());
            User user = userRepository.findById(userId)
                    .orElseThrow(() -> new IllegalArgumentException("User not found"));
            perm = folderPermissionRepository.findByFolderIdAndUserId(folderId, userId)
                    .orElse(new FolderPermission(folder, user, null, status));
            perm.setPermissionStatus(status);
        } else if (body.get("role") != null && !body.get("role").toString().isEmpty()) {
            Role role = Role.valueOf(body.get("role").toString());
            perm = folderPermissionRepository.findByFolderIdAndRole(folderId, role)
                    .orElse(new FolderPermission(folder, null, role, status));
            perm.setPermissionStatus(status);
        } else {
            return ResponseEntity.badRequest().body("Either userId or role must be provided.");
        }

        folderPermissionRepository.save(perm);
        return ResponseEntity.ok(perm);
    }

    @DeleteMapping("/folders/{permissionId}")
    public ResponseEntity<?> deleteFolderPermission(@PathVariable Long permissionId) {
        folderPermissionRepository.deleteById(permissionId);
        return ResponseEntity.ok().build();
    }

    // --- FILE PERMISSIONS ---

    @GetMapping("/files/{assetId}")
    public ResponseEntity<List<FilePermission>> getFilePermissions(@PathVariable Long assetId) {
        return ResponseEntity.ok(filePermissionRepository.findByAssetId(assetId));
    }

    @PostMapping("/files")
    public ResponseEntity<?> setFilePermission(@RequestBody Map<String, Object> body) {
        Long assetId = Long.valueOf(body.get("assetId").toString());
        String statusStr = body.getOrDefault("status", "ALLOWED").toString();
        PermissionStatus status = PermissionStatus.valueOf(statusStr);

        Asset asset = assetRepository.findById(assetId)
                .orElseThrow(() -> new IllegalArgumentException("Asset file not found"));

        FilePermission perm;
        if (body.get("userId") != null && !body.get("userId").toString().isEmpty()) {
            Long userId = Long.valueOf(body.get("userId").toString());
            User user = userRepository.findById(userId)
                    .orElseThrow(() -> new IllegalArgumentException("User not found"));
            perm = filePermissionRepository.findByAssetIdAndUserId(assetId, userId)
                    .orElse(new FilePermission(asset, user, null, status));
            perm.setPermissionStatus(status);
        } else if (body.get("role") != null && !body.get("role").toString().isEmpty()) {
            Role role = Role.valueOf(body.get("role").toString());
            perm = filePermissionRepository.findByAssetIdAndRole(assetId, role)
                    .orElse(new FilePermission(asset, null, role, status));
            perm.setPermissionStatus(status);
        } else {
            return ResponseEntity.badRequest().body("Either userId or role must be provided.");
        }

        filePermissionRepository.save(perm);
        return ResponseEntity.ok(perm);
    }

    @DeleteMapping("/files/{permissionId}")
    public ResponseEntity<?> deleteFilePermission(@PathVariable Long permissionId) {
        filePermissionRepository.deleteById(permissionId);
        return ResponseEntity.ok().build();
    }
}
