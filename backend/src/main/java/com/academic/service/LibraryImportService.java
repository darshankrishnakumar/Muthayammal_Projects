package com.academic.service;

import com.academic.model.*;
import com.academic.repository.AssetRepository;
import com.academic.repository.ProjectRepository;
import com.academic.service.storage.FileStorageService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;

import jakarta.annotation.PreDestroy;
import java.io.*;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * Imports completed projects from a local checkout of the master project repository into
 * the central library.
 *
 * Expected layout (one folder per project):
 * <pre>
 * project_NN_name/
 *   README.md            title (H1), "Abstract" section, quickstart/setup section
 *   requirements.txt     used to infer the technology stack
 *   docs/                DOCX/PDF/Markdown documentation, docs/screenshots/* images
 *   presentations/*.pptx
 *   walkthrough/*.mp4    demonstration video (+ script/timestamps)
 *   source_code/         zipped into one archive; *.db / *.sql also listed under Database
 * </pre>
 * Re-running the import is safe: projects are matched by folder name ({@code source_ref})
 * and files already present in a folder are skipped. Metadata is only filled where empty,
 * so edits made in the UI are preserved.
 */
@Service
public class LibraryImportService {

    private static final Logger logger = LoggerFactory.getLogger(LibraryImportService.class);
    private static final Pattern PROJECT_DIR = Pattern.compile("^project_(\\d{1,4})_[A-Za-z0-9_\\-]+$");
    private static final Set<String> SKIP_DIRS = Set.of("__pycache__", ".git", ".venv", "venv", "node_modules", ".idea", ".pytest_cache", ".mypy_cache");
    private static final Set<String> IMAGE_EXT = Set.of("png", "jpg", "jpeg", "gif", "webp", "svg");
    private static final Set<String> DATABASE_EXT = Set.of("db", "sqlite", "sqlite3", "sql");
    private static final String IMPORT_ACTOR = "library-import";

    @Value("${academic.library.import-root:}")
    private String importRoot;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private AssetRepository assetRepository;

    @Autowired
    private LibraryService libraryService;

    @Autowired
    private FileStorageService storageService;

    @Autowired
    private AuditLogService auditLogService;

    @Autowired
    private TransactionTemplate transactionTemplate;

    private final ExecutorService executor = Executors.newSingleThreadExecutor(r -> {
        Thread t = new Thread(r, "library-import");
        t.setDaemon(true);
        return t;
    });

    private volatile ImportJob currentJob;

    @PreDestroy
    void shutdown() {
        executor.shutdownNow();
    }

    // ------------------------------------------------------------------
    // Scan
    // ------------------------------------------------------------------

    public boolean isConfigured() {
        return importRoot != null && !importRoot.isBlank() && Files.isDirectory(Paths.get(importRoot));
    }

    public Map<String, Object> scan() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("configured", isConfigured());
        result.put("root", importRoot == null || importRoot.isBlank() ? null : Paths.get(importRoot).getFileName().toString());
        if (!isConfigured()) {
            result.put("projects", List.of());
            result.put("message", "Set LIBRARY_IMPORT_ROOT (academic.library.import-root) to a local checkout of the project repository.");
            return result;
        }
        List<Map<String, Object>> projects = new ArrayList<>();
        for (Path dir : projectDirs()) {
            ParsedProject parsed = parse(dir);
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("directory", dir.getFileName().toString());
            row.put("number", parsed.number);
            row.put("title", parsed.title);
            row.put("domain", parsed.domain);
            row.put("technologyStack", parsed.technologyStack);
            row.put("hasVideo", Files.isDirectory(dir.resolve("walkthrough")));
            row.put("hasSourceCode", Files.isDirectory(dir.resolve("source_code")));
            Optional<Project> existing = projectRepository.findBySourceRef(dir.getFileName().toString());
            row.put("imported", existing.isPresent());
            row.put("projectId", existing.map(Project::getId).orElse(null));
            projects.add(row);
        }
        result.put("projects", projects);
        return result;
    }

    // ------------------------------------------------------------------
    // Import job
    // ------------------------------------------------------------------

    public synchronized Map<String, Object> start(List<String> directories, BigDecimal defaultPrice, boolean publish, String actorEmail) {
        if (!isConfigured()) {
            throw new IllegalStateException("Library import root is not configured on the server.");
        }
        if (currentJob != null && currentJob.running) {
            throw new IllegalStateException("An import is already running.");
        }
        Map<String, Path> available = new LinkedHashMap<>();
        for (Path dir : projectDirs()) {
            available.put(dir.getFileName().toString(), dir);
        }
        List<Path> selected = new ArrayList<>();
        if (directories == null || directories.isEmpty()) {
            selected.addAll(available.values());
        } else {
            for (String name : directories) {
                Path dir = available.get(name);
                if (dir == null) {
                    throw new IllegalArgumentException("Unknown project directory: " + name);
                }
                selected.add(dir);
            }
        }

        ImportJob job = new ImportJob(selected.size(), actorEmail);
        currentJob = job;
        executor.submit(() -> runJob(job, selected, defaultPrice, publish));
        auditLogService.log(actorEmail, "LIBRARY_IMPORT_STARTED", "Importing " + selected.size() + " project(s) into the library");
        return job.snapshot();
    }

    public Map<String, Object> status() {
        ImportJob job = currentJob;
        return job == null ? Map.of("running", false, "total", 0, "completed", 0) : job.snapshot();
    }

    private void runJob(ImportJob job, List<Path> dirs, BigDecimal defaultPrice, boolean publish) {
        try {
            for (Path dir : dirs) {
                String name = dir.getFileName().toString();
                job.current = name;
                try {
                    int files = importOne(dir, defaultPrice, publish, job.actorEmail);
                    job.log.add(Map.of("directory", name, "status", "OK", "files", files));
                } catch (Exception e) {
                    logger.error("Library import failed for {}", name, e);
                    job.failed++;
                    job.log.add(Map.of("directory", name, "status", "FAILED", "error", String.valueOf(e.getMessage())));
                }
                job.completed++;
            }
        } finally {
            job.running = false;
            job.current = null;
            auditLogService.log(job.actorEmail, "LIBRARY_IMPORT_FINISHED",
                    String.format("Library import finished: %d/%d processed, %d failed", job.completed, job.total, job.failed));
        }
    }

    /** Imports or refreshes one project folder; returns the number of files added. */
    int importOne(Path dir, BigDecimal defaultPrice, boolean publish, String actorEmail) throws IOException {
        ParsedProject parsed = parse(dir);
        String sourceRef = dir.getFileName().toString();

        Project project = transactionTemplate.execute(status -> {
            Project p = projectRepository.findBySourceRef(sourceRef).orElseGet(Project::new);
            boolean isNew = p.getId() == null;
            if (isNew) {
                String code = parsed.number != null ? String.format("LIB-%03d", parsed.number) : libraryService.nextLibraryCode();
                if (projectRepository.existsByProjectCode(code)) {
                    code = libraryService.nextLibraryCode();
                }
                p.setProjectCode(code);
                p.setSourceRef(sourceRef);
                p.setProjectType(ProjectType.LIBRARY);
                p.setMarketplace(true);
                p.setStatus(ProjectStatus.COMPLETED);
                p.setLifecycleStatus(ProjectStatus.COMPLETED);
                p.setProgressPercent(100);
                p.setCatalogStatus(publish ? CatalogStatus.PUBLISHED : CatalogStatus.DRAFT);
                p.setCreatedBy(actorEmail);
            }
            if (isBlank(p.getProjectName())) p.setProjectName(parsed.title);
            if (isBlank(p.getAbstractText())) p.setAbstractText(parsed.abstractText);
            if (isBlank(p.getDescription())) p.setDescription(parsed.description);
            if (isBlank(p.getTechnologyStack())) p.setTechnologyStack(parsed.technologyStack);
            if (isBlank(p.getDomain())) p.setDomain(parsed.domain);
            if (isBlank(p.getTags())) p.setTags(parsed.tags);
            if (isBlank(p.getInstallationInstructions())) p.setInstallationInstructions(parsed.installation);
            if (p.getPrice() == null && defaultPrice != null) {
                p.setPrice(defaultPrice);
                p.setBudget(defaultPrice);
            }
            p.setUpdatedBy(actorEmail);
            return projectRepository.save(p);
        });

        Map<AssetCategory, Folder> folders = transactionTemplate.execute(status -> libraryService.ensureCategoryFolders(project, actorEmail));
        int added = 0;

        added += importFiles(dir.resolve("docs"), 1, folders.get(AssetCategory.DOCUMENTATION), AssetCategory.DOCUMENTATION, project,
                f -> !isImage(f), f -> f.getFileName().toString().toLowerCase().contains("abstract"));
        added += importFiles(dir.resolve("docs").resolve("screenshots"), 2, folders.get(AssetCategory.SCREENSHOT), AssetCategory.SCREENSHOT, project,
                this::isImage, f -> true);
        added += importFiles(dir.resolve("presentations"), 1, folders.get(AssetCategory.PRESENTATION), AssetCategory.PRESENTATION, project,
                f -> true, f -> false);
        added += importFiles(dir, 1, folders.get(AssetCategory.PRESENTATION), AssetCategory.PRESENTATION, project,
                f -> ext(f).equals("pptx"), f -> false);
        added += importFiles(dir.resolve("walkthrough"), 1, folders.get(AssetCategory.VIDEO), AssetCategory.VIDEO, project,
                f -> true, f -> ext(f).equals("mp4") || ext(f).equals("webm"));
        added += importFiles(dir, 1, folders.get(AssetCategory.OTHER), AssetCategory.OTHER, project,
                f -> Set.of("README.md", "requirements.txt", ".env.example").contains(f.getFileName().toString()), f -> false);

        Path source = dir.resolve("source_code");
        if (Files.isDirectory(source)) {
            added += importFiles(source, 4, folders.get(AssetCategory.DATABASE), AssetCategory.DATABASE, project,
                    f -> DATABASE_EXT.contains(ext(f)), f -> false);
            String zipName = sourceRef + "_source_code.zip";
            if (!exists(folders.get(AssetCategory.SOURCE_CODE), zipName)) {
                Path zip = Files.createTempFile("library-src-", ".zip");
                try {
                    zipDirectory(source, zip);
                    store(zip, zipName, folders.get(AssetCategory.SOURCE_CODE), AssetCategory.SOURCE_CODE, false, project,
                            "Complete source code archive");
                    added++;
                } finally {
                    Files.deleteIfExists(zip);
                }
            }
        }

        auditLogService.log(actorEmail, "LIBRARY_PROJECT_IMPORTED",
                String.format("Imported %s (%s) from %s, %d new file(s)", project.getProjectCode(), project.getProjectName(), sourceRef, added));
        return added;
    }

    private int importFiles(Path dir, int depth, Folder folder, AssetCategory category, Project project,
                            java.util.function.Predicate<Path> include, java.util.function.Predicate<Path> previewable) throws IOException {
        if (!Files.isDirectory(dir)) {
            return 0;
        }
        List<Path> files;
        try (Stream<Path> stream = Files.walk(dir, depth)) {
            files = stream.filter(Files::isRegularFile)
                    .filter(f -> !isSkipped(dir, f))
                    .filter(f -> !f.getFileName().toString().startsWith("."))
                    .filter(f -> depth > 1 || f.getParent().equals(dir) || category == AssetCategory.DATABASE)
                    .filter(include)
                    .sorted()
                    .toList();
        }
        int added = 0;
        for (Path f : files) {
            if (category == AssetCategory.DOCUMENTATION && f.getParent().getFileName().toString().equals("screenshots")) {
                continue;
            }
            String name = f.getFileName().toString();
            if (exists(folder, name)) {
                continue;
            }
            store(f, name, folder, category, previewable.test(f), project, null);
            added++;
        }
        return added;
    }

    private void store(Path file, String displayName, Folder folder, AssetCategory category, boolean previewable, Project project, String description) throws IOException {
        long size = Files.size(file);
        String extension = ext(file).isEmpty() ? extOf(displayName) : extOf(displayName);
        String storagePath;
        try (InputStream in = new BufferedInputStream(Files.newInputStream(file))) {
            storagePath = storageService.storeFile(in, displayName, project.getId(), folder.getId());
        }
        try {
            transactionTemplate.executeWithoutResult(status -> {
                Asset asset = new Asset(folder, displayName, displayName, mimeFor(extension), extension, size, storagePath,
                        1, true, null, description, IMPORT_ACTOR);
                asset.setCategory(category);
                asset.setPreviewable(previewable);
                assetRepository.save(asset);
            });
        } catch (RuntimeException e) {
            storageService.deleteFile(storagePath);
            throw e;
        }
    }

    private boolean exists(Folder folder, String name) {
        return assetRepository.findActiveInFolderByOriginalFileName(folder.getId(), name).isPresent();
    }

    // ------------------------------------------------------------------
    // Parsing
    // ------------------------------------------------------------------

    static final class ParsedProject {
        Integer number;
        String title;
        String abstractText;
        String description;
        String technologyStack;
        String domain;
        String tags;
        String installation;
    }

    ParsedProject parse(Path dir) {
        ParsedProject p = new ParsedProject();
        Matcher m = PROJECT_DIR.matcher(dir.getFileName().toString());
        if (m.matches()) {
            p.number = Integer.parseInt(m.group(1));
        }
        String readme = read(dir.resolve("README.md"));
        p.title = titleFrom(readme, dir.getFileName().toString());
        p.abstractText = section(readme, "abstract");
        String overview = section(readme, "overview");
        p.description = overview != null ? overview : p.abstractText;
        String install = section(readme, "quickstart");
        if (install == null) install = section(readme, "setup");
        if (install == null) install = section(readme, "running");
        if (install == null) install = section(readme, "installation");
        p.installation = install;

        Set<String> techs = new LinkedHashSet<>();
        techs.add("Python");
        String reqs = read(dir.resolve("requirements.txt")) + "\n" + read(dir.resolve("source_code").resolve("requirements.txt"));
        String lower = (reqs + "\n" + readme).toLowerCase();
        addIf(techs, lower, "fastapi", "FastAPI");
        addIf(techs, lower, "flask", "Flask");
        addIf(techs, lower, "django", "Django");
        addIf(techs, lower, "streamlit", "Streamlit");
        addIf(techs, lower, "torch", "PyTorch");
        addIf(techs, lower, "tensorflow", "TensorFlow");
        addIf(techs, lower, "keras", "Keras");
        addIf(techs, lower, "scikit-learn", "scikit-learn");
        addIf(techs, lower, "xgboost", "XGBoost");
        addIf(techs, lower, "ultralytics", "YOLO");
        addIf(techs, lower, "opencv", "OpenCV");
        addIf(techs, lower, "transformers", "Transformers");
        addIf(techs, lower, "langchain", "LangChain");
        addIf(techs, lower, "sqlite", "SQLite");
        addIf(techs, lower, "react", "React");
        p.technologyStack = truncate(String.join(", ", techs), 255);
        p.domain = inferDomain(p.title);
        p.tags = truncate(String.join(", ", techs.stream().filter(t -> !t.equals("Python")).toList()), 500);
        return p;
    }

    private static String titleFrom(String readme, String fallback) {
        for (String line : readme.split("\\R")) {
            if (line.startsWith("# ")) {
                String t = line.substring(2).trim();
                t = t.replaceFirst("(?i)^project\\s*\\d+\\s*[:\\-–]\\s*", "");
                t = t.replaceAll("[*_`]", "").trim();
                if (!t.isEmpty()) {
                    return truncate(prettify(t), 255);
                }
            }
        }
        String base = fallback.replaceFirst("^project_\\d+_", "").replace('_', ' ');
        return prettify(base);
    }

    /** Converts SHOUTED titles to title case; leaves mixed-case titles alone. */
    private static String prettify(String t) {
        if (!t.equals(t.toUpperCase())) {
            return Character.toUpperCase(t.charAt(0)) + t.substring(1);
        }
        StringBuilder sb = new StringBuilder();
        for (String w : t.toLowerCase().split(" ")) {
            if (w.isEmpty()) continue;
            if (sb.length() > 0) sb.append(' ');
            if (Set.of("ai", "ml", "iot", "nlp", "cnn", "rnn", "lstm", "yolo", "gnn", "rag", "rul").contains(w.replaceAll("[^a-z]", ""))) {
                sb.append(w.toUpperCase());
            } else if (sb.length() > 0 && Set.of("and", "of", "for", "using", "with", "the", "in", "on", "a", "an", "to", "from").contains(w)) {
                sb.append(w);
            } else {
                sb.append(Character.toUpperCase(w.charAt(0))).append(w.substring(1));
            }
        }
        return sb.toString();
    }

    /** Body of the first "##" section whose heading contains {@code keyword}. */
    private static String section(String readme, String keyword) {
        String[] lines = readme.split("\\R");
        StringBuilder sb = null;
        for (String line : lines) {
            if (line.startsWith("## ")) {
                if (sb != null) break;
                if (line.toLowerCase().contains(keyword)) {
                    sb = new StringBuilder();
                }
                continue;
            }
            if (sb != null) {
                if (line.trim().equals("---")) break;
                sb.append(line).append('\n');
            }
        }
        if (sb == null) return null;
        String s = sb.toString().trim();
        return s.isEmpty() ? null : truncate(s, 20000);
    }

    static String inferDomain(String title) {
        String t = title.toLowerCase();
        if (containsAny(t, "disease", "medical", "health", "heart", "parkinson", "patient", "diagnosis")) return "Healthcare";
        if (containsAny(t, "intrusion", "phishing", "fraud", "forgery", "deepfake", "deep fake", "cyber", "spoof", "security")) return "Cybersecurity";
        if (containsAny(t, "news", "text", "nlp", "natural language", "summariz", "resume", "complaint", "question answering", "speech", "emotion", "sign language", "handwritten")) return "Natural Language & Speech";
        if (containsAny(t, "detection", "image", "vision", "yolo", "face", "crack", "damage", "classification", "grading", "weapon", "drowsiness", "crowd", "waste", "engagement", "freshness", "egg")) return "Computer Vision";
        if (containsAny(t, "iot", "sensor", "maintenance", "useful life", "railway", "manufacturing", "energy")) return "IoT & Industrial AI";
        if (containsAny(t, "prediction", "forecast", "price", "yield", "churn", "weather", "air quality", "flood", "stock", "crime")) return "Forecasting & Analytics";
        if (containsAny(t, "career", "recommendation", "skill", "dress")) return "Recommender Systems";
        return "Artificial Intelligence";
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    private List<Path> projectDirs() {
        Path root = Paths.get(importRoot).toAbsolutePath().normalize();
        try (Stream<Path> s = Files.list(root)) {
            return s.filter(Files::isDirectory)
                    .filter(d -> PROJECT_DIR.matcher(d.getFileName().toString()).matches())
                    .sorted(Comparator.comparing(d -> {
                        Matcher m = PROJECT_DIR.matcher(d.getFileName().toString());
                        return m.matches() ? Integer.parseInt(m.group(1)) : Integer.MAX_VALUE;
                    }))
                    .toList();
        } catch (IOException e) {
            throw new IllegalStateException("Could not read library import root: " + e.getMessage());
        }
    }

    private static void zipDirectory(Path source, Path zipFile) throws IOException {
        try (ZipOutputStream zos = new ZipOutputStream(new BufferedOutputStream(Files.newOutputStream(zipFile)));
             Stream<Path> walk = Files.walk(source)) {
            for (Path p : (Iterable<Path>) walk.filter(Files::isRegularFile).filter(f -> !isSkipped(source, f)).sorted()::iterator) {
                String entry = source.getFileName() + "/" + source.relativize(p).toString().replace('\\', '/');
                zos.putNextEntry(new ZipEntry(entry));
                Files.copy(p, zos);
                zos.closeEntry();
            }
        }
    }

    private static boolean isSkipped(Path root, Path file) {
        for (Path part : root.relativize(file)) {
            if (SKIP_DIRS.contains(part.toString())) {
                return true;
            }
        }
        return file.getFileName().toString().endsWith(".pyc") || file.getFileName().toString().equals(".DS_Store");
    }

    private boolean isImage(Path f) {
        return IMAGE_EXT.contains(ext(f));
    }

    private static String ext(Path f) {
        return extOf(f.getFileName().toString());
    }

    private static String extOf(String name) {
        int i = name.lastIndexOf('.');
        return i < 0 || i == name.length() - 1 ? "" : name.substring(i + 1).toLowerCase();
    }

    static String mimeFor(String ext) {
        return switch (ext) {
            case "pdf" -> "application/pdf";
            case "docx" -> "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
            case "doc" -> "application/msword";
            case "pptx" -> "application/vnd.openxmlformats-officedocument.presentationml.presentation";
            case "png" -> "image/png";
            case "jpg", "jpeg" -> "image/jpeg";
            case "gif" -> "image/gif";
            case "webp" -> "image/webp";
            case "svg" -> "image/svg+xml";
            case "mp4" -> "video/mp4";
            case "webm" -> "video/webm";
            case "zip" -> "application/zip";
            case "json" -> "application/json";
            case "db", "sqlite", "sqlite3" -> "application/vnd.sqlite3";
            case "md", "txt", "sql", "example" -> "text/plain";
            default -> "application/octet-stream";
        };
    }

    private static String read(Path file) {
        try {
            return Files.isRegularFile(file) ? Files.readString(file, StandardCharsets.UTF_8) : "";
        } catch (IOException e) {
            return "";
        }
    }

    private static void addIf(Set<String> techs, String haystack, String needle, String label) {
        if (haystack.contains(needle)) techs.add(label);
    }

    private static boolean containsAny(String s, String... needles) {
        for (String n : needles) if (s.contains(n)) return true;
        return false;
    }

    private static boolean isBlank(String s) {
        return s == null || s.isBlank();
    }

    private static String truncate(String s, int max) {
        return s == null || s.length() <= max ? s : s.substring(0, max);
    }

    private static final class ImportJob {
        final int total;
        final String actorEmail;
        final List<Map<String, Object>> log = Collections.synchronizedList(new ArrayList<>());
        volatile boolean running = true;
        volatile int completed;
        volatile int failed;
        volatile String current;

        ImportJob(int total, String actorEmail) {
            this.total = total;
            this.actorEmail = actorEmail;
        }

        Map<String, Object> snapshot() {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("running", running);
            m.put("total", total);
            m.put("completed", completed);
            m.put("failed", failed);
            m.put("current", current);
            synchronized (log) {
                m.put("log", new ArrayList<>(log));
            }
            return m;
        }
    }
}
