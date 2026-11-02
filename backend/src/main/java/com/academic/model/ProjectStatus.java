package com.academic.model;

public enum ProjectStatus {
    DRAFT,
    CREATED,
    DEVELOPER_ASSIGNED,
    IN_PROGRESS,
    TESTING,
    READY_FOR_REVIEW,
    CHANGES_REQUESTED,
    REVIEW_APPROVED,
    READY_FOR_FINAL_PAYMENT,
    FINAL_PAYMENT_COMPLETED,
    ACCESS_GRANTED,
    COMPLETED,
    MARKETPLACE_AVAILABLE,
    APPROVED,
    REJECTED,
    INACTIVE;

    public boolean isValidTransition(ProjectStatus nextStatus) {
        if (this == nextStatus) {
            return true;
        }

        switch (this) {
            case DRAFT:
            case CREATED:
                return nextStatus == DEVELOPER_ASSIGNED || nextStatus == APPROVED || nextStatus == MARKETPLACE_AVAILABLE || nextStatus == REJECTED || nextStatus == INACTIVE;
            case DEVELOPER_ASSIGNED:
                return nextStatus == IN_PROGRESS || nextStatus == DEVELOPER_ASSIGNED || nextStatus == REJECTED || nextStatus == INACTIVE;
            case IN_PROGRESS:
                return nextStatus == TESTING || nextStatus == READY_FOR_REVIEW || nextStatus == COMPLETED || nextStatus == INACTIVE;
            case TESTING:
                return nextStatus == READY_FOR_REVIEW || nextStatus == IN_PROGRESS || nextStatus == INACTIVE;
            case READY_FOR_REVIEW:
                return nextStatus == CHANGES_REQUESTED || nextStatus == REVIEW_APPROVED || nextStatus == REJECTED || nextStatus == INACTIVE;
            case CHANGES_REQUESTED:
                return nextStatus == IN_PROGRESS || nextStatus == READY_FOR_REVIEW || nextStatus == INACTIVE;
            case REVIEW_APPROVED:
                return nextStatus == READY_FOR_FINAL_PAYMENT || nextStatus == ACCESS_GRANTED || nextStatus == INACTIVE;
            case READY_FOR_FINAL_PAYMENT:
                return nextStatus == FINAL_PAYMENT_COMPLETED || nextStatus == ACCESS_GRANTED || nextStatus == INACTIVE;
            case FINAL_PAYMENT_COMPLETED:
                return nextStatus == ACCESS_GRANTED || nextStatus == COMPLETED || nextStatus == INACTIVE;
            case ACCESS_GRANTED:
            case MARKETPLACE_AVAILABLE:
            case APPROVED:
                return nextStatus == IN_PROGRESS || nextStatus == REJECTED || nextStatus == COMPLETED || nextStatus == INACTIVE;
            case COMPLETED:
            case REJECTED:
                return nextStatus == INACTIVE;
            case INACTIVE:
                return nextStatus == DRAFT || nextStatus == CREATED;
            default:
                return true;
        }
    }
}
