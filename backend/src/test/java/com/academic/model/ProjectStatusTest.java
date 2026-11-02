package com.academic.model;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ProjectStatusTest {

    @Test
    @DisplayName("Valid status transitions should return true")
    void testValidTransitions() {
        // DRAFT transitions
        assertTrue(ProjectStatus.DRAFT.isValidTransition(ProjectStatus.APPROVED));
        assertTrue(ProjectStatus.DRAFT.isValidTransition(ProjectStatus.REJECTED));
        assertTrue(ProjectStatus.DRAFT.isValidTransition(ProjectStatus.INACTIVE));

        // APPROVED transitions
        assertTrue(ProjectStatus.APPROVED.isValidTransition(ProjectStatus.IN_PROGRESS));
        assertTrue(ProjectStatus.APPROVED.isValidTransition(ProjectStatus.REJECTED));
        assertTrue(ProjectStatus.APPROVED.isValidTransition(ProjectStatus.INACTIVE));

        // IN_PROGRESS transitions
        assertTrue(ProjectStatus.IN_PROGRESS.isValidTransition(ProjectStatus.COMPLETED));
        assertTrue(ProjectStatus.IN_PROGRESS.isValidTransition(ProjectStatus.INACTIVE));

        // COMPLETED & REJECTED transitions
        assertTrue(ProjectStatus.COMPLETED.isValidTransition(ProjectStatus.INACTIVE));
        assertTrue(ProjectStatus.REJECTED.isValidTransition(ProjectStatus.INACTIVE));
        
        // Self transition
        assertTrue(ProjectStatus.DRAFT.isValidTransition(ProjectStatus.DRAFT));
    }

    @Test
    @DisplayName("Invalid status transitions should return false")
    void testInvalidTransitions() {
        // Illegal jump from DRAFT to COMPLETED
        assertFalse(ProjectStatus.DRAFT.isValidTransition(ProjectStatus.COMPLETED));
        
        // Illegal jump from DRAFT to IN_PROGRESS (must be APPROVED first)
        assertFalse(ProjectStatus.DRAFT.isValidTransition(ProjectStatus.IN_PROGRESS));

        // Illegal backwards transition from COMPLETED to IN_PROGRESS
        assertFalse(ProjectStatus.COMPLETED.isValidTransition(ProjectStatus.IN_PROGRESS));
        assertFalse(ProjectStatus.COMPLETED.isValidTransition(ProjectStatus.APPROVED));

        // Illegal backwards transition from REJECTED to APPROVED
        assertFalse(ProjectStatus.REJECTED.isValidTransition(ProjectStatus.APPROVED));
        assertFalse(ProjectStatus.REJECTED.isValidTransition(ProjectStatus.COMPLETED));
    }
}
