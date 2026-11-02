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

    List<Order> findAllByOrderByCreatedAtDesc();

    List<Order> findByCollegeIdOrderByCreatedAtDesc(Long collegeId);

    @org.springframework.data.jpa.repository.Query("SELECT COALESCE(SUM(o.amount), 0) FROM Order o WHERE o.paymentStatus = com.academic.model.PaymentStatus.COMPLETED " +
           "AND (:collegeId IS NULL OR o.collegeId = :collegeId) AND (:simulated IS NULL OR o.simulatedPayment = :simulated)")
    Double sumCompletedRevenue(@org.springframework.data.repository.query.Param("collegeId") Long collegeId,
                               @org.springframework.data.repository.query.Param("simulated") Boolean simulated);

    long countByCollegeId(Long collegeId);
}
