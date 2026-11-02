package com.academic.service;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/** Parsing rules for the master project repository's READMEs (cases taken from the real repository). */
class LibraryImportParsingTest {

    @Test
    @DisplayName("cleanProse drops code diagrams, tables and badges and unwraps markdown")
    void cleanProse() {
        String md = """
                ### Objective
                **VeriNews AI** is a [platform](https://example.com) for news.

                ```
                [Camera] --> [Model]
                ```
                | a | b |
                [![badge](x.svg)](y)
                > Quoted line
                """;
        String out = LibraryImportService.cleanProse(md);
        assertTrue(out.startsWith("Objective\nVeriNews AI is a platform for news."), out);
        assertFalse(out.contains("```"));
        assertFalse(out.contains("[Camera]"));
        assertFalse(out.contains("|"));
        assertFalse(out.contains("**"));
        assertTrue(out.contains("Quoted line"));
    }

    @Test
    @DisplayName("firstParagraph skips headings, badges and code to find real prose")
    void firstParagraph() {
        String md = """
                # PROJECT 38: Title

                [![Python](https://img.shields.io/x.svg)](https://python.org)

                ```
                diagram
                ```

                The system segments pavement cracks and rates their severity for maintenance planning teams.
                Second line of the same paragraph.

                ## Quickstart
                """;
        String p = LibraryImportService.firstParagraph(md);
        assertNotNull(p);
        assertTrue(p.startsWith("The system segments pavement cracks"), p);
        assertTrue(p.endsWith("Second line of the same paragraph."), p);
        assertNull(LibraryImportService.firstParagraph("# Title\n\nToo short.\n"));
    }

    @Test
    @DisplayName("Domains follow the project's subject")
    void domains() {
        assertEquals("Agriculture", LibraryImportService.inferDomain("Apple Disease Detection"));
        assertEquals("Agriculture", LibraryImportService.inferDomain("Crop Yield Prediction using Machine Learning"));
        assertEquals("Healthcare", LibraryImportService.inferDomain("Child Gait Prediction using Machine Learning"));
        assertEquals("Healthcare", LibraryImportService.inferDomain("Heart Disease Prediction"));
        assertEquals("Computer Vision", LibraryImportService.inferDomain("Automated Attendance Monitoring using Face Recognition and Anti-Spoofing"));
        assertEquals("Cybersecurity", LibraryImportService.inferDomain("Phishing Email Detection using Deep Learning"));
        assertEquals("Natural Language & Speech", LibraryImportService.inferDomain("Fake News Detection using Deep learning"));
    }
}
