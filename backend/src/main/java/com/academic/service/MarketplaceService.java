package com.academic.service;

import com.academic.model.*;
import com.academic.repository.AssetRepository;
import com.academic.repository.CollegeProjectAllocationRepository;
import com.academic.repository.ProjectRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

/**
 * College-scoped project marketplace. Students and college admins see only published library
 * projects allocated to their college, priced at that college's effective price.
 */
@Service
public class MarketplaceService {

    @Autowired
    private CollegeProjectAllocationRepository allocationRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private AssetRepository assetRepository;

    @Autowired
    private EntitlementService entitlementService;

    @Autowired
    private AccessControlService accessControlService;

    /** One visible offer: a library project plus the price that applies to the viewer. */
    private record Offer(Project project, BigDecimal price) {}

    @Transactional(readOnly = true)
    public List<Map<String, Object>> browse(User actor, String search, String domain, String technology,
                                            BigDecimal minPrice, BigDecimal maxPrice, String sort) {
        Set<Long> owned = actor.getRole() == Role.USER ? entitlementService.entitledProjectIds(actor.getId()) : Set.of();
        String q = search == null ? "" : search.trim().toLowerCase();
        String tech = technology == null ? "" : technology.trim().toLowerCase();

        List<Map<String, Object>> rows = new ArrayList<>();
        for (Offer offer : visibleOffers(actor)) {
            Project p = offer.project();
            if (!q.isEmpty() && !matches(p, q)) continue;
            if (domain != null && !domain.isBlank() && !domain.equalsIgnoreCase(p.getDomain())) continue;
            if (!tech.isEmpty() && (p.getTechnologyStack() == null || !p.getTechnologyStack().toLowerCase().contains(tech))) continue;
            BigDecimal price = offer.price() != null ? offer.price() : BigDecimal.ZERO;
            if (minPrice != null && price.compareTo(minPrice) < 0) continue;
            if (maxPrice != null && price.compareTo(maxPrice) > 0) continue;
            Map<String, Object> row = card(p, price);
            row.put("owned", owned.contains(p.getId()));
            row.put("relevance", relevance(p, q));
            rows.add(row);
        }

        Comparator<Map<String, Object>> byPrice = Comparator.comparing(r -> (BigDecimal) r.get("price"));
        Comparator<Map<String, Object>> byCode = Comparator.comparing(r -> (String) r.get("projectCode"));
        switch (sort == null ? "relevance" : sort) {
            case "price_asc" -> rows.sort(byPrice.thenComparing(byCode));
            case "price_desc" -> rows.sort(byPrice.reversed().thenComparing(byCode));
            case "newest" -> rows.sort(Comparator.comparing((Map<String, Object> r) -> String.valueOf(r.get("createdAt"))).reversed());
            case "title" -> rows.sort(Comparator.comparing(r -> String.valueOf(r.get("projectName")).toLowerCase()));
            default -> rows.sort(Comparator.comparing((Map<String, Object> r) -> (Integer) r.get("relevance")).reversed().thenComparing(byCode));
        }
        return rows;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> filters(User actor) {
        List<Offer> offers = visibleOffers(actor);
        Set<String> domains = new TreeSet<>();
        Map<String, Integer> techCounts = new HashMap<>();
        BigDecimal min = null, max = null;
        for (Offer o : offers) {
            if (o.project().getDomain() != null) domains.add(o.project().getDomain());
            if (o.project().getTechnologyStack() != null) {
                for (String t : o.project().getTechnologyStack().split(",")) {
                    String tt = t.trim();
                    if (!tt.isEmpty()) techCounts.merge(tt, 1, Integer::sum);
                }
            }
            BigDecimal price = o.price() != null ? o.price() : BigDecimal.ZERO;
            min = min == null || price.compareTo(min) < 0 ? price : min;
            max = max == null || price.compareTo(max) > 0 ? price : max;
        }
        List<String> technologies = techCounts.entrySet().stream()
                .sorted(Map.Entry.<String, Integer>comparingByValue().reversed().thenComparing(Map.Entry.comparingByKey()))
                .map(Map.Entry::getKey).collect(Collectors.toList());
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("domains", domains);
        m.put("technologies", technologies);
        m.put("minPrice", min != null ? min : BigDecimal.ZERO);
        m.put("maxPrice", max != null ? max : BigDecimal.ZERO);
        m.put("total", offers.size());
        return m;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> detail(User actor, Long projectId) {
        Offer offer = visibleOffers(actor).stream()
                .filter(o -> o.project().getId().equals(projectId))
                .findFirst()
                .orElseThrow(() -> new AccessDeniedException("This project is not available to your college."));
        Project p = offer.project();
        AccessControlService.ProjectAccessLevel level = accessControlService.getAccessLevel(p, actor);

        Map<String, Object> m = card(p, offer.price() != null ? offer.price() : BigDecimal.ZERO);
        m.put("description", p.getDescription());
        m.put("installationInstructions", level == AccessControlService.ProjectAccessLevel.FULL ? p.getInstallationInstructions() : null);
        m.put("owned", actor.getRole() == Role.USER && entitlementService.hasAccess(actor.getId(), p.getId()));
        m.put("accessLevel", level.name());
        m.put("canPurchase", actor.getRole() == Role.USER && level != AccessControlService.ProjectAccessLevel.FULL);

        List<Asset> assets = assetRepository.findCurrentAssetsByProjectId(p.getId());
        Map<String, Long> byCategory = new TreeMap<>();
        List<Map<String, Object>> previews = new ArrayList<>();
        for (Asset a : assets) {
            byCategory.merge(a.getCategory() != null ? a.getCategory().name() : "OTHER", 1L, Long::sum);
            if (a.isPreviewable()) {
                Map<String, Object> am = new LinkedHashMap<>();
                am.put("id", a.getId());
                am.put("name", a.getOriginalFileName());
                am.put("category", a.getCategory());
                am.put("mimeType", a.getMimeType());
                am.put("fileSize", a.getFileSize());
                previews.add(am);
            }
        }
        m.put("filesByCategory", byCategory);
        m.put("previewAssets", previews);
        return m;
    }

    /** Library projects the student owns (purchased or granted). */
    @Transactional(readOnly = true)
    public List<Map<String, Object>> purchased(User actor) {
        List<Map<String, Object>> rows = new ArrayList<>();
        for (ProjectEntitlement e : entitlementService.activeFor(actor.getId())) {
            Project p = e.getProject();
            Map<String, Object> row = card(p, p.getPrice());
            row.put("owned", true);
            row.put("source", e.getSource());
            row.put("grantedAt", e.getGrantedAt());
            row.put("projectType", p.getProjectType());
            rows.add(row);
        }
        return rows;
    }

    private List<Offer> visibleOffers(User actor) {
        switch (actor.getRole()) {
            case SUPER_ADMIN:
                return projectRepository.searchLibrary(null, CatalogStatus.PUBLISHED, null).stream()
                        .map(p -> new Offer(p, p.getPrice())).toList();
            case ADMIN:
            case USER: {
                College college = accessControlService.requireCollege(actor);
                return allocationRepository.findActiveByCollegeId(college.getId()).stream()
                        .filter(a -> a.getProject().isLibrary() && a.getProject().getCatalogStatus() == CatalogStatus.PUBLISHED)
                        .map(a -> new Offer(a.getProject(), a.getEffectivePrice()))
                        .toList();
            }
            default:
                throw new AccessDeniedException("The marketplace is available to students and administrators.");
        }
    }

    private Map<String, Object> card(Project p, BigDecimal price) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", p.getId());
        m.put("projectCode", p.getProjectCode());
        m.put("projectName", p.getProjectName());
        m.put("abstractText", p.getAbstractText());
        m.put("domain", p.getDomain());
        m.put("technologyStack", p.getTechnologyStack());
        m.put("tags", p.getTags());
        m.put("price", price != null ? price : BigDecimal.ZERO);
        m.put("createdAt", p.getCreatedAt());
        return m;
    }

    private static boolean matches(Project p, String q) {
        return contains(p.getProjectName(), q) || contains(p.getProjectCode(), q) || contains(p.getAbstractText(), q)
                || contains(p.getTechnologyStack(), q) || contains(p.getTags(), q) || contains(p.getDomain(), q);
    }

    private static int relevance(Project p, String q) {
        if (q.isEmpty()) return 0;
        int score = 0;
        if (contains(p.getProjectName(), q)) score += 10;
        if (contains(p.getTags(), q) || contains(p.getTechnologyStack(), q)) score += 5;
        if (contains(p.getDomain(), q)) score += 3;
        if (contains(p.getAbstractText(), q)) score += 1;
        return score;
    }

    private static boolean contains(String s, String q) {
        return s != null && s.toLowerCase().contains(q);
    }
}
