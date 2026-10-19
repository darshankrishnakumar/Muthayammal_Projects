# 04. Data Pipeline & Benchmark Engineering (PROJECT-026)

## Benchmark Dataset Topology
The training and validation dataset (`source_code/data/nids_traffic_dataset.csv`) contains 6,000 realistic network flow sessions synthesized according to NSL-KDD and CICIDS2018 distribution parameters.

| Class Label | Category | Sample Count | Percentage | Primary Signature Characteristics |
|---|---|---|---|---|
| **Normal** | Benign | 3,000 | 50.0% | Standard byte distribution, duration ~1.5s, serror=0, rerror=0, same_srv=1.0 |
| **DoS_SYN_Flood** | Denial of Service | 900 | 15.0% | Bursts 180-500 pps, duration <0.02s, S0 flag, serror=1.0, dst_bytes=0 |
| **Probe_PortScan** | Reconnaissance | 720 | 12.0% | REJ flag across diverse ports, diff_srv >0.85, rerror >0.80 |
| **R2L_SSH_BruteForce** | Remote to Local | 480 | 8.0% | Repeated port 22 connections, bursts 35-110 count, rerror ~0.55 |
| **Botnet_Mirai_C2** | Malware C2 | 420 | 7.0% | Long duration (15-60s), uniform 64-192 byte packets, same_srv=0.5 |
| **U2R_BufferOverflow** | Privilege Escalation | 240 | 4.0% | Abnormal payload byte volumes (2.2k-9.5k), shellcode injection |
| **ZeroDay_Anomaly** | Unknown Zero-Day | 240 | 4.0% | High payload (15k-48k bytes), RSTOS0 flags, anomalous reconstruction error |

## Monitored Feature Vector (12 Dimensions)
1. `duration`: Length of connection in seconds.
2. `src_bytes`: Bytes sent from source to destination.
3. `dst_bytes`: Bytes sent from destination to source.
4. `count`: Connections to same host in past 2 seconds.
5. `srv_count`: Connections to same service in past 2 seconds.
6. `serror_rate`: Percentage of connections with SYN errors.
7. `rerror_rate`: Percentage of connections with REJ errors.
8. `same_srv_rate`: Percentage of connections to same service.
9. `diff_srv_rate`: Percentage of connections to different services.
10. `dst_host_count`: Destination host count in past 100 connections.
11. `dst_host_srv_count`: Destination service count in past 100 connections.
12. `dst_host_same_src_port_rate`: Percentage originating from same client port.
