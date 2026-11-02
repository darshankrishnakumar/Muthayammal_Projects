package com.academic.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

@Component
@Order(2)
public class ProjectDataInitializer implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(ProjectDataInitializer.class);

    @Override
    public void run(String... args) throws Exception {
        // Clean slate: Projects are created and assigned explicitly via Super Admin workflow
        logger.info("ProjectDataInitializer: Ready for Super Admin project creation workflow.");
    }
}
