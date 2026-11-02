package com.academic.dto;

import java.util.List;

public class BulkUserCreateRequest {

    private List<UserCreateItemDto> users;

    /** College for USER and ADMIN rows (Super Admin only; college admins always use their own). */
    private Long collegeId;

    public Long getCollegeId() {
        return collegeId;
    }

    public void setCollegeId(Long collegeId) {
        this.collegeId = collegeId;
    }

    public BulkUserCreateRequest() {}

    public BulkUserCreateRequest(List<UserCreateItemDto> users) {
        this.users = users;
    }

    public List<UserCreateItemDto> getUsers() {
        return users;
    }

    public void setUsers(List<UserCreateItemDto> users) {
        this.users = users;
    }

    public static class UserCreateItemDto {
        private String fullName;
        private String email;
        private String password;
        private String phone;
        private String role;
        private String department;
        private String organization;

        public UserCreateItemDto() {}

        public String getFullName() {
            return fullName;
        }

        public void setFullName(String fullName) {
            this.fullName = fullName;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }

        public String getPhone() {
            return phone;
        }

        public void setPhone(String phone) {
            this.phone = phone;
        }

        public String getRole() {
            return role;
        }

        public void setRole(String role) {
            this.role = role;
        }

        public String getDepartment() {
            return department;
        }

        public void setDepartment(String department) {
            this.department = department;
        }

        public String getOrganization() {
            return organization;
        }

        public void setOrganization(String organization) {
            this.organization = organization;
        }
    }
}
