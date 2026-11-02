package com.academic.dto;

import com.academic.model.Requirement;
import com.academic.model.RequirementStatus;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public class RequirementSummaryDto {
    private Long id;
    private String title;
    private String problemStatement;
    private BigDecimal budget;
    private String technologyStack;
    private RequirementStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private UserSummary user;

    public static class UserSummary {
        private Long id;
        private String fullName;
        private String email;
        private String role;

        public UserSummary() {}

        public UserSummary(Long id, String fullName, String email, String role) {
            this.id = id;
            this.fullName = fullName;
            this.email = email;
            this.role = role;
        }

        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        public String getFullName() { return fullName; }
        public void setFullName(String fullName) { this.fullName = fullName; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        public String getRole() { return role; }
        public void setRole(String role) { this.role = role; }
    }

    public RequirementSummaryDto() {}

    public static RequirementSummaryDto fromEntity(Requirement req) {
        RequirementSummaryDto dto = new RequirementSummaryDto();
        dto.setId(req.getId());
        dto.setTitle(req.getTitle());
        dto.setProblemStatement(req.getProblemStatement());
        dto.setBudget(req.getBudget());
        dto.setTechnologyStack(req.getTechnologyStack());
        dto.setStatus(req.getStatus());
        dto.setCreatedAt(req.getCreatedAt());
        dto.setUpdatedAt(req.getUpdatedAt());

        if (req.getUser() != null) {
            dto.setUser(new UserSummary(
                req.getUser().getId(),
                req.getUser().getFullName(),
                req.getUser().getEmail(),
                req.getUser().getRole() != null ? req.getUser().getRole().name() : "USER"
            ));
        }
        return dto;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getProblemStatement() { return problemStatement; }
    public void setProblemStatement(String problemStatement) { this.problemStatement = problemStatement; }

    public BigDecimal getBudget() { return budget; }
    public void setBudget(BigDecimal budget) { this.budget = budget; }

    public String getTechnologyStack() { return technologyStack; }
    public void setTechnologyStack(String technologyStack) { this.technologyStack = technologyStack; }

    public RequirementStatus getStatus() { return status; }
    public void setStatus(RequirementStatus status) { this.status = status; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }

    public UserSummary getUser() { return user; }
    public void setUser(UserSummary user) { this.user = user; }
}
