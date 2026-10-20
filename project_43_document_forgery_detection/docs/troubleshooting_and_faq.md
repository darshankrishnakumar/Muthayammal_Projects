# Troubleshooting & Technical FAQ

### Q1: Why is Port 5043 strictly enforced?
Port 5043 is assigned to PROJECT-043 to ensure deterministic multi-service co-existence across the 55 capstone projects ($5001 + N - 1$).

### Q2: How does the system handle high-resolution PDF scans?
PDF documents are rasterized into uncompressed 300 DPI image buffers in memory, cropped into 64x64 forensic patches, and evaluated in parallel before assembling the full-page tampering heatmap.

### Q3: What is the difference between Spatial ELA and Frequency DCT?
Spatial ELA captures localized lossy JPEG compression rate discrepancies. Frequency DCT isolates high-frequency sensor noise irregularities and splicing boundary discontinuities. Fusing both streams achieves near-zero false positive rates.

### Q4: Are audit ledger records legally admissible?
Yes. Every audit entry is cryptographically sealed with a SHA-256 Merkle chain back to Genesis Block #0, establishing an unbroken legal chain of custody.
