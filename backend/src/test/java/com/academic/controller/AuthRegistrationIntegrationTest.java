package com.academic.controller;

import com.academic.dto.RegisterRequest;
import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import com.academic.repository.UserRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@SuppressWarnings("null")
class AuthRegistrationIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("1: Valid registration creates ACTIVE USER and can immediately login with email and password")
    void testValidRegistrationCreatesActiveUserAndCanLoginDirectly() throws Exception {
        String email = "alice_student_" + System.currentTimeMillis() + "@academic.com";

        RegisterRequest request = new RegisterRequest();
        request.setFullName("Alice Student");
        request.setEmail(email);
        request.setMobileNumber("9876543210");
        request.setOrganization("MIT Computer Science");
        request.setPassword("SecurePass123!");
        request.setConfirmPassword("SecurePass123!");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.role").value("USER"))
                .andExpect(jsonPath("$.status").value("ACTIVE"));

        // Verify DB State
        Optional<User> userOpt = userRepository.findByEmailAndDeletedFalse(email);
        assertTrue(userOpt.isPresent());
        User user = userOpt.get();
        assertEquals(Role.USER, user.getRole());
        assertEquals(UserStatus.ACTIVE, user.getStatus());
        assertTrue(user.isEmailVerified());

        // Immediately login with email & password
        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of("email", email, "password", "SecurePass123!"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").exists())
                .andExpect(jsonPath("$.user.email").value(email))
                .andExpect(jsonPath("$.user.role").value("USER"));
    }

    @Test
    @DisplayName("2: Indian mobile format with +91 is supported")
    void testIndianMobileWithCountryCode() throws Exception {
        String email = "indian_user_" + System.currentTimeMillis() + "@academic.com";

        RegisterRequest request = new RegisterRequest();
        request.setFullName("Rohan Sharma");
        request.setEmail(email);
        request.setMobileNumber("+91 9342666379");
        request.setOrganization("IIT Madras");
        request.setPassword("SecurePass123!");
        request.setConfirmPassword("SecurePass123!");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true));
    }

    @Test
    @DisplayName("3: Duplicate email validation prevents re-registering existing accounts")
    void testDuplicateActiveEmailValidation() throws Exception {
        String activeEmail = "active_dup_" + System.currentTimeMillis() + "@academic.com";
        User activeUser = new User(activeEmail, "passHash", "Active User", Role.USER, UserStatus.ACTIVE);
        activeUser.setEmailVerified(true);
        userRepository.save(activeUser);

        RegisterRequest request = new RegisterRequest();
        request.setFullName("Duplicate Test");
        request.setEmail(activeEmail);
        request.setMobileNumber("9876543210");
        request.setPassword("Password123!");
        request.setConfirmPassword("Password123!");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").value("An account with this email is already registered. Please login."));
    }

    @Test
    @DisplayName("4: Field validation errors (invalid mobile, password mismatch, short password)")
    void testRegistrationValidationErrors() throws Exception {
        // Invalid mobile
        RegisterRequest invalidMobile = new RegisterRequest();
        invalidMobile.setFullName("Bob");
        invalidMobile.setEmail("bob_mob@academic.com");
        invalidMobile.setMobileNumber("12345"); // Invalid Indian mobile
        invalidMobile.setPassword("Password123!");
        invalidMobile.setConfirmPassword("Password123!");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidMobile)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").value("Please provide a valid 10-digit Indian mobile number (e.g. 9876543210 or +91 9876543210)."));

        // Password mismatch
        RegisterRequest mismatch = new RegisterRequest();
        mismatch.setFullName("Bob");
        mismatch.setEmail("bob_mismatch@academic.com");
        mismatch.setMobileNumber("9876543210");
        mismatch.setPassword("Password123!");
        mismatch.setConfirmPassword("Different123!");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(mismatch)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").value("Password and Confirm Password do not match."));

        // Short password
        RegisterRequest shortPass = new RegisterRequest();
        shortPass.setFullName("Bob");
        shortPass.setEmail("bob_short@academic.com");
        shortPass.setMobileNumber("9876543210");
        shortPass.setPassword("short");
        shortPass.setConfirmPassword("short");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(shortPass)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").value("Password must be at least 8 characters long."));
    }
}
