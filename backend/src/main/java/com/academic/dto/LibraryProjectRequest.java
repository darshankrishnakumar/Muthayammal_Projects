package com.academic.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;

public class LibraryProjectRequest {

    @NotBlank
    @Size(max = 255)
    private String title;

    @Size(max = 50)
    private String code;

    private String abstractText;

    private String description;

    @Size(max = 255)
    private String technologyStack;

    @Size(max = 100)
    private String domain;

    @Size(max = 500)
    private String tags;

    @DecimalMin(value = "0.0")
    private BigDecimal price;

    private String installationInstructions;

    private String catalogStatus;

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    public String getAbstractText() { return abstractText; }
    public void setAbstractText(String abstractText) { this.abstractText = abstractText; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getTechnologyStack() { return technologyStack; }
    public void setTechnologyStack(String technologyStack) { this.technologyStack = technologyStack; }
    public String getDomain() { return domain; }
    public void setDomain(String domain) { this.domain = domain; }
    public String getTags() { return tags; }
    public void setTags(String tags) { this.tags = tags; }
    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }
    public String getInstallationInstructions() { return installationInstructions; }
    public void setInstallationInstructions(String installationInstructions) { this.installationInstructions = installationInstructions; }
    public String getCatalogStatus() { return catalogStatus; }
    public void setCatalogStatus(String catalogStatus) { this.catalogStatus = catalogStatus; }
}
