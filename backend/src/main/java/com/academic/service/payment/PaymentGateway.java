package com.academic.service.payment;

import java.math.BigDecimal;

/**
 * Boundary for collecting payments. A real provider (Razorpay, Stripe, PayU...) implements
 * this interface; the rest of the platform only trusts results that come back from here,
 * never a status sent by the browser.
 */
public interface PaymentGateway {

    /** Short provider identifier stored on each transaction, e.g. "simulated" or "razorpay". */
    String name();

    /** Whether this gateway is configured and allowed to take payments in this environment. */
    boolean isEnabled();

    /** Whether results from this gateway are simulated (development only). */
    boolean isSimulated();

    /**
     * Collect {@code amount} for the order identified by {@code orderReference}.
     * Synchronous providers return a final result; redirect/webhook providers would return
     * {@code pending} here and complete through a verified callback.
     */
    PaymentResult charge(String orderReference, BigDecimal amount, String currency, String customerEmail);
}
