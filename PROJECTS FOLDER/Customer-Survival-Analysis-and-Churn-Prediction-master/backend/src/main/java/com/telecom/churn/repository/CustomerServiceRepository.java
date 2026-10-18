package com.telecom.churn.repository;

import com.telecom.churn.entity.CustomerServiceEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CustomerServiceRepository extends JpaRepository<CustomerServiceEntity, Long> {
    List<CustomerServiceEntity> findByCustomerId(Long customerId);
}
