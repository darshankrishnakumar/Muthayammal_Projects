package com.academic.repository;

import com.academic.model.Order;
import com.academic.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    List<Order> findByUserOrderByCreatedAtDesc(User user);

    Optional<Order> findByOrderNumber(String orderNumber);

    Optional<Order> findByInvoiceNumber(String invoiceNumber);

    Optional<Order> findByIdempotencyKey(String idempotencyKey);

    List<Order> findByUserIdAndProjectIdAndPaymentStatus(Long userId, Long projectId, com.academic.model.PaymentStatus paymentStatus);

    List<Order> findByProjectIdAndPaymentStatus(Long projectId, com.academic.model.PaymentStatus paymentStatus);

    boolean existsByOrderNumber(String orderNumber);

    boolean existsByInvoiceNumber(String invoiceNumber);
}
