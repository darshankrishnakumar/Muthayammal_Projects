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
    private static final Set<String> VIDEO_EXT = Set.of("mp4", "webm", "mov");
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
            row.put("hasVideo", containsFileWithExtension(dir.resolve("walkthrough"), Set.of("mp4", "webm", "mov")));
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

    public synchronized Map<String, Object> start(List<String> directories, BigDecimal defaultPrice, boolean publish, boolean refreshMetadata, String actorEmail) {
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
        executor.submit(() -> runJob(job, selected, defaultPrice, publish, refreshMetadata));
        auditLogService.log(actorEmail, "LIBRARY_IMPORT_STARTED", "Importing " + selected.size() + " project(s) into the library");
        return job.snapshot();
    }

    public Map<String, Object> status() {
        ImportJob job = currentJob;
        return job == null ? Map.of("running", false, "total", 0, "completed", 0) : job.snapshot();
    }

    private void runJob(ImportJob job, List<Path> dirs, BigDecimal defaultPrice, boolean publish, boolean refreshMetadata) {
        try {
            for (Path dir : dirs) {
                String name = dir.getFileName().toString();
                job.current = name;
                try {
                    int files = importOne(dir, defaultPrice, publish, refreshMetadata, job.actorEmail);
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

    /**
     * Imports or refreshes one project folder; returns the number of files added.
     * With {@code refreshMetadata}, descriptive fields are re-read from the repository even if set;
     * code, price and catalogue status are never changed.
     */
    int importOne(Path dir, BigDecimal defaultPrice, boolean publish, boolean refreshMetadata, String actorEmail) throws IOException {
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
                // Never publish without a price: an unpriced published project would be free to buy.
                p.setCatalogStatus(publish && defaultPrice != null ? CatalogStatus.PUBLISHED : CatalogStatus.DRAFT);
                p.setCreatedBy(actorEmail);
            }
            boolean overwrite = refreshMetadata;
            if (overwrite || isBlank(p.getProjectName())) p.setProjectName(parsed.title);
            if (overwrite || isBlank(p.getAbstractText())) p.setAbstractText(parsed.abstractText);
            if (overwrite || isBlank(p.getDescription())) p.setDescription(parsed.description);
            if (overwrite || isBlank(p.getTechnologyStack())) p.setTechnologyStack(parsed.technologyStack);
            if (overwrite || isBlank(p.getDomain())) p.setDomain(parsed.domain);
            if (overwrite || isBlank(p.getTags())) p.setTags(parsed.tags);
            if (overwrite || isBlank(p.getInstallationInstructions())) p.setInstallationInstructions(parsed.installation);
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
                f -> VIDEO_EXT.contains(ext(f)), f -> true);
        added += importFiles(dir.resolve("walkthrough"), 1, folders.get(AssetCategory.VIDEO), AssetCategory.DOCUMENTATION, project,
                f -> !VIDEO_EXT.contains(ext(f)), f -> false);
        if (refreshMetadata) {
            fixImportedCategories(folders.get(AssetCategory.VIDEO));
        }
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

    /** Earlier imports filed walkthrough scripts as VIDEO; re-label imported non-video files. */
    private void fixImportedCategories(Folder videoFolder) {
        transactionTemplate.executeWithoutResult(status -> {
            for (Asset a : assetRepository.findByFolderIdAndIsCurrentVersionTrueAndActiveTrue(videoFolder.getId())) {
                if (IMPORT_ACTOR.equals(a.getUploadedBy()) && a.getCategory() == AssetCategory.VIDEO && !VIDEO_EXT.contains(a.getExtension())) {
                    a.setCategory(AssetCategory.DOCUMENTATION);
                    a.setPreviewable(false);
                    assetRepository.save(a);
                }
            }
        });
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
        String catalogTitle = p.number != null ? catalogTitles().get(p.number) : null;
        p.title = catalogTitle != null ? truncate(prettify(cleanTitle(catalogTitle)), 255) : titleFrom(readme, dir.getFileName().toString());

        String overview = firstSection(readme, "overview", "introduction", "about", "description", "summary");
        Path docs = dir.resolve("docs");
        List<java.util.function.Supplier<String>> candidates = new ArrayList<>(List.of(
                () -> section(readme, "abstract"),
                () -> overview,
                () -> tagline(readme),
                () -> firstParagraph(readme)));
        for (String docName : List.of("README.md", "architecture.md")) {
            String doc = read(docs.resolve(docName));
            candidates.add(() -> firstSection(doc, "abstract", "overview", "introduction", "purpose", "summary"));
            candidates.add(() -> firstParagraph(doc));
        }
        // First candidate that still reads as prose once markdown, code and tables are removed.
        p.abstractText = candidates.stream()
                .map(java.util.function.Supplier::get)
                .filter(Objects::nonNull)
                .map(LibraryImportService::cleanProse)
                .filter(text -> text.length() >= 60)
                .findFirst()
                .map(text -> truncate(text, 4000))
                .orElse(null);
        String description = overview != null ? cleanProse(overview) : null;
        p.description = description != null && description.length() >= 60 ? description : p.abstractText;
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

    private Map<Integer, String> catalogTitles;

    /** Canonical titles from the master README's catalogue table: | **NN** | [Title](project_NN_x/) | ... */
    private synchronized Map<Integer, String> catalogTitles() {
        if (catalogTitles == null) {
            Map<Integer, String> titles = new HashMap<>();
            Matcher m = Pattern.compile("(?m)^\\|\\s*\\*\\*(\\d{1,4})\\*\\*\\s*\\|\\s*\\[([^\\]]+)\\]\\(project_")
                    .matcher(read(Paths.get(importRoot).resolve("README.md")));
            while (m.find()) {
                titles.put(Integer.parseInt(m.group(1)), m.group(2).trim());
            }
            catalogTitles = titles;
        }
        return catalogTitles;
    }

    private static String cleanTitle(String t) {
        String s = t.replaceFirst("(?i)^project[\\s_-]*\\d+\\s*[:\\-–]\\s*", "");
        s = s.replaceFirst("(?i)^extended abstract:\\s*", "");
        s = s.replaceAll("[*_`]", "");
        // Drop emoji and other symbols outside letters, digits, punctuation and spaces.
        s = s.replaceAll("[^\\p{L}\\p{N}\\p{P}\\p{Zs}+&]", "");
        return s.replaceAll("\\s{2,}", " ").trim();
    }

    private static String titleFrom(String readme, String fallback) {
        for (String line : readme.split("\\R")) {
            if (line.startsWith("# ")) {
                String t = cleanTitle(line.substring(2).trim());
                if (!t.isEmpty()) {
                    return truncate(prettify(t), 255);
                }
            }
        }
        String base = fallback.replaceFirst("^project_\\d+_", "").replace('_', ' ');
        return prettify(base);
    }

    private static final Set<String> ACRONYMS = Set.of("ai", "ml", "iot", "nlp", "cnn", "rnn", "lstm", "yolo", "yolov8", "gnn", "rag",
            "rul", "dea", "anpr", "api", "gps", "ui", "dl");

    /** Converts SHOUTED titles to title case; leaves mixed-case titles alone. */
    private static String prettify(String t) {
        if (!t.equals(t.toUpperCase())) {
            return Character.toUpperCase(t.charAt(0)) + t.substring(1);
        }
        StringBuilder sb = new StringBuilder();
        for (String w : t.toLowerCase().split(" ")) {
            if (w.isEmpty()) continue;
            if (sb.length() > 0) sb.append(' ');
            if (sb.length() > 0 && Set.of("and", "of", "for", "using", "with", "the", "in", "on", "a", "an", "to", "from", "through").contains(w)) {
                sb.append(w);
                continue;
            }
            String[] parts = w.split("-", -1);
            for (int i = 0; i < parts.length; i++) {
                if (i > 0) sb.append('-');
                String part = parts[i];
                if (part.isEmpty()) continue;
                if (ACRONYMS.contains(part.replaceAll("[^a-z0-9]", ""))) {
                    sb.append(part.toUpperCase());
                } else {
                    sb.append(Character.toUpperCase(part.charAt(0))).append(part.substring(1));
                }
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

    private static String firstSection(String markdown, String... keywords) {
        for (String k : keywords) {
            String s = section(markdown, k);
            if (s != null) return s;
        }
        return null;
    }

    /** The "> ..." tagline that some READMEs put under the title. */
    private static String tagline(String readme) {
        for (String line : readme.split("\\R")) {
            if (line.startsWith("## ")) break;
            if (line.startsWith(">")) {
                String t = stripInline(line.substring(1));
                if (t.length() > 40) return t;
            }
        }
        return null;
    }

    /** First prose paragraph (skipping headings, badges, tables, quotes, lists and code). */
    static String firstParagraph(String markdown) {
        StringBuilder para = new StringBuilder();
        boolean inCode = false;
        for (String raw : markdown.split("\\R")) {
            String line = raw.trim();
            if (line.startsWith("```")) {
                inCode = !inCode;
                if (para.length() > 0) break;
                continue;
            }
            if (inCode) continue;
            boolean prose = !line.isEmpty() && !line.startsWith("#") && !line.startsWith("|") && !line.startsWith(">")
                    && !line.startsWith("[![") && !line.startsWith("!") && !line.startsWith("-") && !line.startsWith("*")
                    && !line.matches("^\\d+\\..*") && !line.equals("---");
            if (prose) {
                para.append(para.length() > 0 ? " " : "").append(stripInline(line));
            } else if (para.length() > 0) {
                break;
            }
        }
        String s = para.toString().trim();
        return s.length() >= 60 ? truncate(s, 4000) : null;
    }

    /**
     * Turns a markdown fragment into plain prose for display: drops fenced code (ASCII diagrams),
     * tables, badges and images, unwraps headings, links and emphasis, and collapses blank lines.
     */
    static String cleanProse(String markdown) {
        StringBuilder out = new StringBuilder();
        boolean inCode = false;
        for (String raw : markdown.split("\\R")) {
            String line = raw.strip();
            if (line.startsWith("```")) {
                inCode = !inCode;
                continue;
            }
            if (inCode || line.startsWith("|") || line.startsWith("[![") || line.startsWith("![") || line.equals("---")) {
                continue;
            }
            line = line.replaceFirst("^#{1,6}\\s*", "").replaceFirst("^>\\s*", "");
            line = stripInline(line);
            if (line.isEmpty()) {
                if (out.length() > 0 && !out.toString().endsWith("\n\n")) out.append("\n\n");
                continue;
            }
            if (out.length() > 0 && !out.toString().endsWith("\n")) out.append('\n');
            out.append(line);
        }
        return out.toString().strip();
    }

    private static String stripInline(String s) {
        return s.replaceAll("\\[([^\\]]+)\\]\\([^)]*\\)", "$1").replaceAll("[*_`]", "").trim();
    }

    static String inferDomain(String title) {
        String t = title.toLowerCase();
        if (containsAny(t, "crop", "apple", "plant", "agricultur", "egg ")) return "Agriculture";
        if (containsAny(t, "disease", "medical", "health", "heart", "parkinson", "patient", "diagnosis", "gait")) return "Healthcare";
        if (containsAny(t, "face recognition", "attendance")) return "Computer Vision";
        if (containsAny(t, "intrusion", "phishing", "fraud", "forgery", "deepfake", "deep fake", "cyber", "security")) return "Cybersecurity";
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

    private static boolean containsFileWithExtension(Path dir, Set<String> extensions) {
        if (!Files.isDirectory(dir)) {
            return false;
        }
        try (Stream<Path> s = Files.list(dir)) {
            return s.anyMatch(f -> Files.isRegularFile(f) && extensions.contains(ext(f)));
        } catch (IOException e) {
            return false;
        }
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
