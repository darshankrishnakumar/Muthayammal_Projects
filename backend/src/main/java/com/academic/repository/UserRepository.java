package com.academic.repository;

import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmailAndDeletedFalse(String email);

    Optional<User> findByEmail(String email);

    boolean existsByEmailAndDeletedFalse(String email);

    boolean existsByEmail(String email);

    List<User> findByRoleAndDeletedFalse(Role role);

    // Fetch only regular users (role = USER) from user_management table
    @Query("SELECT u FROM User u WHERE u.deleted = false AND u.role = com.academic.model.Role.USER " +
           "AND (:status IS NULL OR u.status = :status) " +
           "AND (:query IS NULL OR LOWER(u.fullName) LIKE LOWER(CONCAT('%', :query, '%')) OR LOWER(u.email) LIKE LOWER(CONCAT('%', :query, '%')))")
    List<User> searchUsersOnly(@Param("status") UserStatus status,
                               @Param("query") String query);

    // College administrators (role = ADMIN). Super Admins are platform owners, not listed here.
    @Query("SELECT u FROM User u WHERE u.deleted = false AND u.role = com.academic.model.Role.ADMIN " +
           "AND (:status IS NULL OR u.status = :status) " +
           "AND (:query IS NULL OR LOWER(u.fullName) LIKE LOWER(CONCAT('%', :query, '%')) OR LOWER(u.email) LIKE LOWER(CONCAT('%', :query, '%')))")
    List<User> searchAdminsOnly(@Param("status") UserStatus status,
                                @Param("query") String query);

    @Query("SELECT u FROM User u WHERE u.deleted = false AND u.college.id = :collegeId AND u.role = :role " +
           "AND (:status IS NULL OR u.status = :status) " +
           "AND (:query IS NULL OR LOWER(u.fullName) LIKE LOWER(CONCAT('%', :query, '%')) OR LOWER(u.email) LIKE LOWER(CONCAT('%', :query, '%'))) " +
           "ORDER BY u.createdAt DESC")
    List<User> searchByCollegeAndRole(@Param("collegeId") Long collegeId,
                                      @Param("role") Role role,
                                      @Param("status") UserStatus status,
                                      @Param("query") String query);

    @Query("SELECT COUNT(u) FROM User u WHERE u.deleted = false AND u.college.id = :collegeId AND u.role = :role")
    long countByCollegeAndRole(@Param("collegeId") Long collegeId, @Param("role") Role role);

    long countByRoleAndDeletedFalse(Role role);

    @Query("SELECT u FROM User u WHERE u.deleted = false AND u.college.id = :collegeId AND u.role = com.academic.model.Role.ADMIN ORDER BY u.fullName ASC")
    List<User> findAdminsByCollegeId(@Param("collegeId") Long collegeId);
}
