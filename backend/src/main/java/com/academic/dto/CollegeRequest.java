package com.academic.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public class CollegeRequest {

    @NotBlank
    @Size(max = 200)
    private String name;

    @NotBlank
    @Size(max = 30)
    @Pattern(regexp = "^[A-Za-z0-9_-]+$", message = "may contain letters, digits, '-' and '_' only")
    private String code;

    @Size(max = 100)
    private String city;

    @Size(max = 100)
    private String state;

    @Email
    @Size(max = 150)
    private String contactEmail;

    @Size(max = 30)
    private String contactPhone;

    @Size(max = 1000)
    private String address;

    private Boolean active;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    public String getState() { return state; }
    public void setState(String state) { this.state = state; }
    public String getContactEmail() { return contactEmail; }
    public void setContactEmail(String contactEmail) { this.contactEmail = contactEmail; }
    public String getContactPhone() { return contactPhone; }
    public void setContactPhone(String contactPhone) { this.contactPhone = contactPhone; }
    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }
    public Boolean getActive() { return active; }
    public void setActive(Boolean active) { this.active = active; }
}
