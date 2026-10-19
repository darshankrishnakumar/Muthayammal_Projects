import os
import sys
import random
from datetime import datetime, timedelta

# Ensure source_code is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "project_12_egg_gender_prediction", "source_code"))
import database as db

def seed_database():
    db.init_db()
    existing = db.get_database_stats()["total_records"]
    if existing >= 20:
        print(f"Database already has {existing} records. Seeding skipped.")
        return

    specimens = [
        ("Specimen_F01_Leghorn_Oval", "Female (Hen)", "♀", 88.4, 88.4, 11.6, 79.2, 1.26, 0.034, "Recommended for egg laying pullet flock."),
        ("Specimen_M01_Plymouth_Pointed", "Male (Rooster)", "♂", 84.1, 15.9, 84.1, 68.5, 1.46, 0.082, "Diverted to broiler / meat production."),
        ("Specimen_F02_Rhode_Island_Round", "Female (Hen)", "♀", 91.2, 91.2, 8.8, 82.5, 1.21, 0.028, "Recommended for egg laying pullet flock."),
        ("Specimen_M02_Sussex_Conical", "Male (Rooster)", "♂", 86.7, 13.3, 86.7, 69.8, 1.43, 0.076, "Diverted to broiler / meat production."),
        ("Specimen_F03_Australorp_Spherical", "Female (Hen)", "♀", 94.0, 94.0, 6.0, 84.1, 1.19, 0.022, "Recommended for high-yield breeder pullet."),
        ("Specimen_M03_Brahma_Elongated", "Male (Rooster)", "♂", 89.5, 10.5, 89.5, 66.4, 1.51, 0.091, "Diverted to meat grow-out flock."),
        ("Specimen_F04_Orpington_Broad", "Female (Hen)", "♀", 85.3, 85.3, 14.7, 78.4, 1.28, 0.039, "Recommended for egg laying pullet flock."),
        ("Specimen_M04_Wyandotte_Tapered", "Male (Rooster)", "♂", 82.8, 17.2, 82.8, 70.1, 1.43, 0.074, "Diverted to meat production."),
        ("Specimen_F05_Ancona_Pullet", "Female (Hen)", "♀", 87.6, 87.6, 12.4, 77.9, 1.28, 0.036, "Recommended for commercial layer development."),
        ("Specimen_M05_Cornish_Sharp", "Male (Rooster)", "♂", 92.3, 7.7, 92.3, 67.2, 1.49, 0.088, "Diverted to broiler lines."),
        ("Specimen_F06_Barnevelder_Oval", "Female (Hen)", "♀", 86.0, 86.0, 14.0, 78.8, 1.27, 0.035, "Layer flock development."),
        ("Specimen_M06_Marans_Conical", "Male (Rooster)", "♂", 85.0, 15.0, 85.0, 69.1, 1.45, 0.078, "Broiler line rearing."),
        ("Specimen_F07_Silkie_Round", "Female (Hen)", "♀", 90.5, 90.5, 9.5, 81.3, 1.23, 0.030, "Breeder layer candidate."),
        ("Specimen_M07_Welsummer_Sharp", "Male (Rooster)", "♂", 88.0, 12.0, 88.0, 67.8, 1.47, 0.085, "Grow-out meat bird candidate."),
        ("Specimen_F08_Hamburg_Broad", "Female (Hen)", "♀", 84.7, 84.7, 15.3, 77.2, 1.30, 0.041, "Egg production pipeline."),
        ("Specimen_M08_Campine_Tapered", "Male (Rooster)", "♂", 83.4, 16.6, 83.4, 70.5, 1.42, 0.072, "Alternative poultry meat sector."),
        ("Specimen_F09_Minorca_Spherical", "Female (Hen)", "♀", 92.8, 92.8, 7.2, 83.0, 1.20, 0.025, "Top tier layer candidate."),
        ("Specimen_M09_Dorking_Pointed", "Male (Rooster)", "♂", 87.2, 12.8, 87.2, 68.2, 1.47, 0.080, "Meat grow-out flock."),
        ("Specimen_F10_Faverolles_Oval", "Female (Hen)", "♀", 86.9, 86.9, 13.1, 79.5, 1.26, 0.033, "High-efficiency layer."),
        ("Specimen_M10_Cochin_ApexSharp", "Male (Rooster)", "♂", 90.1, 9.9, 90.1, 67.0, 1.49, 0.086, "Commercial broiler flock.")
    ]

    base_time = datetime.now() - timedelta(days=5)
    for i, s in enumerate(specimens):
        t_str = (base_time + timedelta(hours=i*5, minutes=random.randint(2, 45))).strftime("%Y-%m-%d %H:%M:%S")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO egg_predictions (
                    timestamp, specimen_name, predicted_sex, symbol,
                    confidence, female_prob, male_prob, shape_index,
                    elongation, apex_sharpness, recommendation, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t_str, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], "hatchery_batch"
            ))
            conn.commit()

    stats = db.get_database_stats()
    print(f"Successfully seeded database! Total records now: {stats['total_records']}")

if __name__ == "__main__":
    seed_database()
