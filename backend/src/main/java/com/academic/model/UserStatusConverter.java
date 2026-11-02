package com.academic.model;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

@Converter(autoApply = true)
public class UserStatusConverter implements AttributeConverter<UserStatus, Integer> {

    @Override
    public Integer convertToDatabaseColumn(UserStatus status) {
        if (status == null) {
            return 0;
        }
        switch (status) {
            case ACTIVE:
                return 0;
            case INACTIVE:
                return 1;
            case PENDING_VERIFICATION:
                return 2;
            default:
                return 0;
        }
    }

    @Override
    public UserStatus convertToEntityAttribute(Integer dbData) {
        if (dbData == null || dbData == 0) {
            return UserStatus.ACTIVE;
        } else if (dbData == 1) {
            return UserStatus.INACTIVE;
        } else if (dbData == 2) {
            return UserStatus.PENDING_VERIFICATION;
        }
        return UserStatus.ACTIVE;
    }
}
