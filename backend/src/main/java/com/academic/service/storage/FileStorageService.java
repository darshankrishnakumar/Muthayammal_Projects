package com.academic.service.storage;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.NoSuchElementException;
import java.util.UUID;

/**
 * Private on-disk storage for project deliverables.
 *
 * Files live outside any public web root under {@code academic.storage.root} and are
 * addressed by a relative path ({@code project_{id}/folder_{id}/{uuid}.{ext}}) that is
 * stored in ASSET_MASTER. Original filenames are never used on disk, so uploads cannot
 * collide or traverse directories. Files are only ever streamed back through
 * authorization-checked controllers.
 */
@Service
public class FileStorageService {

    private static final Logger logger = LoggerFactory.getLogger(FileStorageService.class);

    @Value("${academic.storage.root:uploads}")
    private String storageRoot;

    private Path rootPath;

    @PostConstruct
    void init() {
        rootPath = Paths.get(storageRoot).toAbsolutePath().normalize();
        try {
            Files.createDirectories(rootPath);
        } catch (IOException e) {
            throw new IllegalStateException("Could not initialise private file storage at " + rootPath, e);
        }
        logger.info("Private file storage initialised at {}", rootPath);
    }

    /**
     * Streams the payload to private storage and returns the relative storage path.
     */
    public String storeFile(InputStream inputStream, String originalFilename, Long projectId, Long folderId) {
        String extension = extensionOf(originalFilename);
        String storedName = UUID.randomUUID() + (extension.isEmpty() ? "" : "." + extension);
        String relative = "project_" + projectId + "/folder_" + folderId + "/" + storedName;

        Path target = resolveSafely(relative);
        try {
            Files.createDirectories(target.getParent());
            Files.copy(inputStream, target, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new RuntimeException("Failed to write file to private storage: " + e.getMessage(), e);
        }
        return relative;
    }

    public Resource loadFileAsResource(String storagePath) {
        Path file = resolveSafely(storagePath);
        if (!Files.isRegularFile(file)) {
            throw new NoSuchElementException("Stored file is missing from private storage.");
        }
        try {
            return new UrlResource(file.toUri());
        } catch (MalformedURLException e) {
            throw new NoSuchElementException("Stored file could not be opened.");
        }
    }

    /**
     * Best-effort delete used for rollback when metadata persistence fails.
     */
    public void deleteFile(String storagePath) {
        if (storagePath == null || storagePath.isBlank()) {
            return;
        }
        try {
            Files.deleteIfExists(resolveSafely(storagePath));
        } catch (IOException | SecurityException e) {
            logger.warn("Could not delete stored file {}: {}", storagePath, e.getMessage());
        }
    }

    private Path resolveSafely(String relative) {
        Path resolved = rootPath.resolve(relative).normalize();
        if (!resolved.startsWith(rootPath)) {
            throw new SecurityException("Rejected storage path outside the private storage root.");
        }
        return resolved;
    }

    private static String extensionOf(String filename) {
        if (filename == null) {
            return "";
        }
        int dot = filename.lastIndexOf('.');
        if (dot < 0 || dot == filename.length() - 1) {
            return "";
        }
        String ext = filename.substring(dot + 1).toLowerCase();
        return ext.matches("[a-z0-9]{1,10}") ? ext : "";
    }
}
