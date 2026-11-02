package com.academic.dto;

import com.academic.model.ItemType;

public class CatalogItemDto {

    private String id;
    private String title;
    private String category;
    private ItemType itemType;
    private String description;
    private Double price;
    private String technologyStack;
    private String deliverable;
    private String badge;
    private Double rating;
    private Integer reviewCount;

    public CatalogItemDto() {}

    public CatalogItemDto(String id, String title, String category, ItemType itemType, 
                          String description, Double price, String technologyStack, 
                          String deliverable, String badge, Double rating, Integer reviewCount) {
        this.id = id;
        this.title = title;
        this.category = category;
        this.itemType = itemType;
        this.description = description;
        this.price = price;
        this.technologyStack = technologyStack;
        this.deliverable = deliverable;
        this.badge = badge;
        this.rating = rating;
        this.reviewCount = reviewCount;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public ItemType getItemType() {
        return itemType;
    }

    public void setItemType(ItemType itemType) {
        this.itemType = itemType;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Double getPrice() {
        return price;
    }

    public void setPrice(Double price) {
        this.price = price;
    }

    public String getTechnologyStack() {
        return technologyStack;
    }

    public void setTechnologyStack(String technologyStack) {
        this.technologyStack = technologyStack;
    }

    public String getDeliverable() {
        return deliverable;
    }

    public void setDeliverable(String deliverable) {
        this.deliverable = deliverable;
    }

    public String getBadge() {
        return badge;
    }

    public void setBadge(String badge) {
        this.badge = badge;
    }

    public Double getRating() {
        return rating;
    }

    public void setRating(Double rating) {
        this.rating = rating;
    }

    public Integer getReviewCount() {
        return reviewCount;
    }

    public void setReviewCount(Integer reviewCount) {
        this.reviewCount = reviewCount;
    }
}
