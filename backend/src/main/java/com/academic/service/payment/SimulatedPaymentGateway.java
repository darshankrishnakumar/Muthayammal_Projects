package com.academic.service.payment;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.UUID;

/**
 * Development-only gateway. Approves every charge instantly and marks it as simulated.
 * Disabled unless {@code academic.payments.simulation-enabled=true}; the production profile
 * forces it off.
 */
@Component
public class SimulatedPaymentGateway implements PaymentGateway {

    @Value("${academic.payments.simulation-enabled:false}")
    private boolean enabled;

    @Override
    public String name() {
        return "simulated";
    }

    @Override
    public boolean isEnabled() {
        return enabled;
    }

    @Override
    public boolean isSimulated() {
        return true;
    }

    @Override
    public PaymentResult charge(String orderReference, BigDecimal amount, String currency, String customerEmail) {
        return PaymentResult.succeeded("SIM-" + UUID.randomUUID().toString().replace("-", "").substring(0, 20).toUpperCase());
    }
}
