package com.academic.service.payment;

/** Raised when no enabled payment gateway exists in this environment (HTTP 503). */
public class PaymentUnavailableException extends RuntimeException {
    public PaymentUnavailableException(String message) {
        super(message);
    }
}
