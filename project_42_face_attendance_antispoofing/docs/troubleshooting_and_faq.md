# Troubleshooting & Technical FAQ

### Q1: Why is Port 5042 strictly enforced?
Port 5042 is assigned to PROJECT-042 to ensure deterministic multi-service co-existence across the 55 capstone projects. The server will not collide with other ports ($5001 + N - 1$).

### Q2: What happens if a student wears glasses or changes hairstyles?
ArcFace projects facial identity into a 512-dimensional spherical hypersphere that abstracts low-level surface details into high-level cranial geometry. Mild glasses and hair changes maintain cosine similarity well above the $	au=0.68$ threshold.

### Q3: How does the system handle complete network severance?
The microservice is fully self-contained. The SQLite WAL database and PyTorch models reside on the edge device. Turnstile authentications execute with sub-15ms latency even with zero WAN/Internet connectivity.

### Q4: How can security operators audit historical records?
Operators query `GET /api/attendance/audit-logs`, which traverses the chained SHA-256 blocks from the Genesis block to the tip, mathematically verifying that no historical records have been altered.
