import os
import sqlite3
import mysql.connector
from datetime import datetime

# Database paths & credentials
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_DB = os.path.join(BASE_DIR, "Customer-Survival-Analysis-and-Churn-Prediction-master", "predictions.db")

MYSQL_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "telecom_churn"),
}

def map_binary_str(val):
    if val is None:
        return "No"
    s = str(val).strip().lower()
    return "Yes" if s in ["1", "true", "yes"] else "No"

def migrate():
    print(f"Connecting to legacy SQLite database at: {SQLITE_DB}")
    if not os.path.exists(SQLITE_DB):
        print("SQLite database not found. Skipping SQLite data migration.")
        return

    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    sqlite_cur.execute("SELECT * FROM predictions ORDER BY id ASC")
    rows = sqlite_cur.fetchall()
    print(f"Found {len(rows)} legacy predictions in SQLite database.")

    print(f"Connecting to MySQL server at {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}...")
    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    mysql_cur = mysql_conn.cursor()

    migrated_count = 0

    for r in rows:
        cust_code = r["customer_id"] if r["customer_id"] else f"CUST-{r['id']:05d}"
        gender = r["gender"] if r["gender"] in ["Male", "Female"] else "Male"
        senior = int(r["senior_citizen"]) if r["senior_citizen"] is not None else 0
        partner = map_binary_str(r["partner"])
        dependents = map_binary_str(r["dependents"])
        tenure = int(r["tenure"]) if r["tenure"] is not None else 1

        phone_svc = map_binary_str(r["phone_service"])
        mult_lines = "Yes" if map_binary_str(r["multiple_lines"]) == "Yes" else ("No phone service" if phone_svc == "No" else "No")
        net_svc = r["internet_service"] if r["internet_service"] in ["Fiber optic", "DSL", "No"] else "DSL"
        sec = map_binary_str(r["online_security"])
        bkp = map_binary_str(r["online_backup"])
        dev = map_binary_str(r["device_protection"])
        tech = map_binary_str(r["tech_support"])
        tv = map_binary_str(r["streaming_tv"])
        movies = map_binary_str(r["streaming_movies"])

        contract = r["contract"] if r["contract"] in ["Month-to-month", "One year", "Two year"] else "Month-to-month"
        paperless = map_binary_str(r["paperless_billing"])
        payment = r["payment_method"] if r["payment_method"] else "Electronic check"
        monthly = float(r["monthly_charges"]) if r["monthly_charges"] is not None else 50.0
        total = float(r["total_charges"]) if r["total_charges"] is not None else (monthly * max(1, tenure))

        pred_class = "Churn" if "churn" in str(r["prediction_status"]).lower() else "No Churn"
        prob = float(r["churn_probability"])
        if prob > 1.0: # Normalize percentage like 43.416 to 0.43416
            prob = prob / 100.0
        prob = min(1.0, max(0.0, round(prob, 4)))

        risk = r["risk_level"] if r["risk_level"] in ["High", "Medium", "Low"] else ("High" if prob >= 0.65 else ("Medium" if prob >= 0.35 else "Low"))
        rec = r["action_suggested"] if r["action_suggested"] else "Standard account review."
        ts_str = r["prediction_date"] if r["prediction_date"] else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # 1. Insert into customers
            mysql_cur.execute("""
                INSERT INTO customers (customer_code, gender, senior_citizen, partner, dependents, tenure)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
            """, (cust_code, gender, senior, partner, dependents, tenure))
            cust_id = mysql_cur.lastrowid

            # 2. Insert into customer_services
            mysql_cur.execute("""
                INSERT INTO customer_services 
                (customer_id, phone_service, multiple_lines, internet_service, online_security, online_backup, device_protection, tech_support, streaming_tv, streaming_movies)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (cust_id, phone_svc, mult_lines, net_svc, sec, bkp, dev, tech, tv, movies))

            # 3. Insert into billing_accounts
            mysql_cur.execute("""
                INSERT INTO billing_accounts
                (customer_id, contract_type, paperless_billing, payment_method, monthly_charges, total_charges)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cust_id, contract, paperless, payment, monthly, total))

            # 4. Insert into prediction_history
            mysql_cur.execute("""
                INSERT INTO prediction_history
                (customer_id, customer_code, timestamp, predicted_class, churn_probability, risk_level, recommendation, model_version,
                 gender, senior_citizen, partner, dependents, tenure, phone_service, multiple_lines, internet_service,
                 online_security, online_backup, device_protection, tech_support, streaming_tv, streaming_movies,
                 contract, paperless_billing, payment_method, monthly_charges, total_charges)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (cust_id, cust_code, ts_str, pred_class, prob, risk, rec, "Random Forest",
                  gender, senior, partner, dependents, tenure, phone_svc, mult_lines, net_svc,
                  sec, bkp, dev, tech, tv, movies, contract, paperless, payment, monthly, total))

            migrated_count += 1
        except Exception as e:
            print(f"Error migrating record ID {r['id']}: {e}")

    mysql_conn.commit()
    print(f"Successfully migrated {migrated_count} of {len(rows)} records into MySQL!")

    # Verify counts in MySQL
    mysql_cur.execute("SELECT COUNT(*) FROM customers")
    c_count = mysql_cur.fetchone()[0]
    mysql_cur.execute("SELECT COUNT(*) FROM prediction_history")
    p_count = mysql_cur.fetchone()[0]

    print(f"Validation: Total customers in MySQL: {c_count}")
    print(f"Validation: Total prediction_history records in MySQL: {p_count}")

    sqlite_conn.close()
    mysql_conn.close()

if __name__ == "__main__":
    migrate()
