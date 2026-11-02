package com.academic.dto;

import com.academic.model.User;
import java.util.ArrayList;
import java.util.List;

public class BulkUserCreateResponse {

    private int totalRecords;
    private int successCount;
    private int failedCount;
    private int duplicateCount;
    private List<User> createdUsers = new ArrayList<>();
    private List<BulkUserErrorItem> errors = new ArrayList<>();

    public BulkUserCreateResponse() {}

    public BulkUserCreateResponse(int totalRecords, int successCount, int failedCount, int duplicateCount) {
        this.totalRecords = totalRecords;
        this.successCount = successCount;
        this.failedCount = failedCount;
        this.duplicateCount = duplicateCount;
    }

    public int getTotalRecords() {
        return totalRecords;
    }

    public void setTotalRecords(int totalRecords) {
        this.totalRecords = totalRecords;
    }

    public int getSuccessCount() {
        return successCount;
    }

    public void setSuccessCount(int successCount) {
        this.successCount = successCount;
    }

    public int getFailedCount() {
        return failedCount;
    }

    public void setFailedCount(int failedCount) {
        this.failedCount = failedCount;
    }

    public int getDuplicateCount() {
        return duplicateCount;
    }

    public void setDuplicateCount(int duplicateCount) {
        this.duplicateCount = duplicateCount;
    }

    public List<User> getCreatedUsers() {
        return createdUsers;
    }

    public void setCreatedUsers(List<User> createdUsers) {
        this.createdUsers = createdUsers;
    }

    public List<BulkUserErrorItem> getErrors() {
        return errors;
    }

    public void setErrors(List<BulkUserErrorItem> errors) {
        this.errors = errors;
    }

    public static class BulkUserErrorItem {
        private int rowIndex;
        private String email;
        private String reason;

        public BulkUserErrorItem() {}

        public BulkUserErrorItem(int rowIndex, String email, String reason) {
            this.rowIndex = rowIndex;
            this.email = email;
            this.reason = reason;
        }

        public int getRowIndex() {
            return rowIndex;
        }

        public void setRowIndex(int rowIndex) {
            this.rowIndex = rowIndex;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public String getReason() {
            return reason;
        }

        public void setReason(String reason) {
            this.reason = reason;
        }
    }
}
