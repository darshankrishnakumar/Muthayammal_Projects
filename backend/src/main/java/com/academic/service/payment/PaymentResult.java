package com.academic.service.payment;

public class PaymentResult {

    public enum Outcome { SUCCEEDED, FAILED, PENDING }

    private final Outcome outcome;
    private final String providerReference;
    private final String failureReason;

    private PaymentResult(Outcome outcome, String providerReference, String failureReason) {
        this.outcome = outcome;
        this.providerReference = providerReference;
        this.failureReason = failureReason;
    }

    public static PaymentResult succeeded(String providerReference) {
        return new PaymentResult(Outcome.SUCCEEDED, providerReference, null);
    }

    public static PaymentResult failed(String providerReference, String reason) {
        return new PaymentResult(Outcome.FAILED, providerReference, reason);
    }

    public static PaymentResult pending(String providerReference) {
        return new PaymentResult(Outcome.PENDING, providerReference, null);
    }

    public Outcome getOutcome() {
        return outcome;
    }

    public String getProviderReference() {
        return providerReference;
    }

    public String getFailureReason() {
        return failureReason;
    }
}
