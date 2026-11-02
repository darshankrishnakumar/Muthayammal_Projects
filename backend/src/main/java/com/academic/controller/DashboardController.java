package com.academic.controller;

import com.academic.service.AccessControlService;
import com.academic.service.DashboardService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    @Autowired
    private DashboardService dashboardService;

    @Autowired
    private AccessControlService accessControlService;

    @GetMapping
    public Map<String, Object> dashboard() {
        return dashboardService.forActor(accessControlService.getCurrentAuthenticatedUser());
    }
}
