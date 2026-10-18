"""Profile Manager for User Profiles, Measurements, Preferences, and History."""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple
import config
from backend.database import get_db_connection, init_db


class ProfileManager:
    """Manages persistent SQLite operations for users, measurements, and preferences."""

    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)

    def get_or_create_user(self, user_id: str = "default_user", display_name: str = "User") -> Dict[str, Any]:
        """Fetches existing user or creates a new profile."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM USER_PROFILE WHERE user_id = ?;", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)

            cursor.execute(
                "INSERT INTO USER_PROFILE (user_id, display_name) VALUES (?, ?);",
                (user_id, display_name)
            )
            conn.commit()
            cursor.execute("SELECT * FROM USER_PROFILE WHERE user_id = ?;", (user_id,))
            return dict(cursor.fetchone())
        finally:
            conn.close()

    def update_profile(self, user_id: str, display_name: str) -> bool:
        """Updates display name of user."""
        conn = get_db_connection(self.db_path)
        try:
            conn.execute(
                "UPDATE USER_PROFILE SET display_name = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?;",
                (display_name, user_id)
            )
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def validate_measurements(
        self,
        height_cm: Optional[float] = None,
        shoulder_cm: Optional[float] = None,
        chest_cm: Optional[float] = None,
        waist_cm: Optional[float] = None,
        hip_cm: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Validates realistic human measurement limits."""
        limits = {
            "height_cm": (height_cm, 50.0, 250.0, "Height"),
            "shoulder_cm": (shoulder_cm, 20.0, 100.0, "Shoulder width"),
            "chest_cm": (chest_cm, 30.0, 200.0, "Chest circumference"),
            "waist_cm": (waist_cm, 30.0, 200.0, "Waist circumference"),
            "hip_cm": (hip_cm, 30.0, 200.0, "Hip circumference"),
        }
        for key, (val, min_v, max_v, label) in limits.items():
            if val is not None:
                try:
                    f_val = float(val)
                    if f_val < min_v or f_val > max_v:
                        return False, f"{label} must be between {min_v} and {max_v} cm."
                except (ValueError, TypeError):
                    return False, f"{label} must be a valid number."
        return True, None

    def save_measurements(
        self,
        user_id: str,
        height_cm: Optional[float] = None,
        shoulder_cm: Optional[float] = None,
        chest_cm: Optional[float] = None,
        waist_cm: Optional[float] = None,
        hip_cm: Optional[float] = None,
        source: str = "manual",
    ) -> Tuple[bool, Optional[str]]:
        """Saves a new measurement entry without silently overwriting previous entries."""
        if source not in ("manual", "image_estimate"):
            return False, "Measurement source must be 'manual' or 'image_estimate'."

        is_valid, err = self.validate_measurements(height_cm, shoulder_cm, chest_cm, waist_cm, hip_cm)
        if not is_valid:
            return False, err

        self.get_or_create_user(user_id)
        conn = get_db_connection(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO BODY_MEASUREMENTS (
                    user_id, height_cm, shoulder_cm, chest_cm, waist_cm, hip_cm, measurement_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (user_id, height_cm, shoulder_cm, chest_cm, waist_cm, hip_cm, source)
            )
            conn.commit()
            return True, None
        except sqlite3.Error as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def get_latest_measurements(self, user_id: str, source: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetches the most recent measurement record, optionally filtered by source."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        try:
            if source:
                cursor.execute(
                    """
                    SELECT * FROM BODY_MEASUREMENTS
                    WHERE user_id = ? AND measurement_source = ?
                    ORDER BY created_at DESC LIMIT 1;
                    """,
                    (user_id, source)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM BODY_MEASUREMENTS
                    WHERE user_id = ?
                    ORDER BY created_at DESC LIMIT 1;
                    """,
                    (user_id,)
                )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def save_preferences(
        self,
        user_id: str,
        preferred_styles: str,
        preferred_colours: str,
        preferred_occasions: str,
        preferred_categories: str,
        budget_min: float = 0.0,
        budget_max: float = 10000.0,
        preferred_season: str = "All-Season",
    ) -> Tuple[bool, Optional[str]]:
        """Upserts user clothing preferences."""
        if budget_min < 0 or budget_max < 0 or budget_min > budget_max:
            return False, "Invalid budget values. Budget minimum cannot exceed maximum."

        self.get_or_create_user(user_id)
        conn = get_db_connection(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO USER_PREFERENCES (
                    user_id, preferred_styles, preferred_colours, preferred_occasions,
                    preferred_categories, budget_min, budget_max, preferred_season, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    preferred_styles = excluded.preferred_styles,
                    preferred_colours = excluded.preferred_colours,
                    preferred_occasions = excluded.preferred_occasions,
                    preferred_categories = excluded.preferred_categories,
                    budget_min = excluded.budget_min,
                    budget_max = excluded.budget_max,
                    preferred_season = excluded.preferred_season,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (
                    user_id, preferred_styles, preferred_colours, preferred_occasions,
                    preferred_categories, budget_min, budget_max, preferred_season
                )
            )
            conn.commit()
            return True, None
        except sqlite3.Error as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetches stored user preferences."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM USER_PREFERENCES WHERE user_id = ?;", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def record_recommendation(
        self,
        user_id: str,
        outfit_id: str,
        outfit_name: str,
        category: str,
        match_score: float,
        reason: str,
    ) -> bool:
        """Appends an outfit recommendation to user history."""
        self.get_or_create_user(user_id)
        conn = get_db_connection(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO RECOMMENDATION_HISTORY (
                    user_id, outfit_id, outfit_name, category, match_score, recommendation_reason
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (user_id, outfit_id, outfit_name, category, match_score, reason)
            )
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def get_recommendation_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves past recommendation history for a user."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT * FROM RECOMMENDATION_HISTORY
                WHERE user_id = ?
                ORDER BY created_at DESC LIMIT ?;
                """,
                (user_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def clear_history(self, user_id: str) -> bool:
        """Clears recommendation history for a user."""
        conn = get_db_connection(self.db_path)
        try:
            conn.execute("DELETE FROM RECOMMENDATION_HISTORY WHERE user_id = ?;", (user_id,))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def delete_profile(self, user_id: str) -> bool:
        """Deletes user profile and all associated data via SQLite CASCADE."""
        conn = get_db_connection(self.db_path)
        try:
            conn.execute("DELETE FROM USER_PROFILE WHERE user_id = ?;", (user_id,))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()
