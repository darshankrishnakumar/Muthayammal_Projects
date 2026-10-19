# Database Schema & Relational Architecture

The system implements 9 relational tables under SQLAlchemy 2.0 with full foreign key constraints and ACID transactional isolation:

```
+--------------------+        +--------------------+        +--------------------+
|     categories     |        |      products      |        |     suppliers      |
|--------------------|        |--------------------|        |--------------------|
| id (PK)            |<-------| category_id (FK)   |        | id (PK)            |<---+
| name               |        | id (PK)            |        | name               |    |
| description        |        | sku (UNIQUE)       |        | contact_person     |    |
+--------------------+        | price              |        | email / phone      |    |
                              | cost_price         |        +--------------------+    |
                              | quantity           |                                  |
                              | min_stock / ROP    |        +--------------------+    |
                              | barcode / rfid_tag |        |  purchase_orders   |    |
                              +---------+----------+        |--------------------|    |
                                        |                   | id (PK)            |    |
                    +-------------------+---+               | po_number (UNIQUE) |    |
                    |                       |               | supplier_id (FK)   |----+
+-------------------v--+        +-----------v--------+      | total_amount       |
|   stock_movements    |        |       sales        |      | status             |
|----------------------|        |--------------------|      +---------+----------+
| id (PK)              |        | id (PK)            |                |
| product_id (FK)      |        | product_id (FK)    |      +---------v----------+
| movement_type        |        | quantity_sold      |      |     shipments      |
| quantity             |        | total_amount       |      |--------------------|
| reason / device_id   |        | sale_date          |      | id (PK)            |
+----------------------+        +--------------------+      | po_id (FK)         |
                                                            | tracking_number    |
                                                            | status / location  |
                                                            +--------------------+
```
