# 04. Data Pipeline & Corpus Engineering

## Dataset Synthesis Methodology
To overcome the lack of publicly available, high-fidelity customer complaint data with verified multi-industry operational targets, a specialized corpus generator was implemented in `source_code/data/train_and_save_models.py`.

### Corpus Characteristics
- **Total Records:** 6,000 multi-industry complaint documents.
- **Sectors Represented:** Cloud SaaS, FinTech, Consumer Electronics, Freight Logistics, Enterprise Security, and E-Commerce.
- **Feature Set:** `id`, `text`, `category`, `category_label`, `department`, `priority`, `urgency_score`, `sentiment_score`.

### Category Distribution
| Category Key | Category Label | Assigned Department | Sample Count |
|---|---|---|---|
| `payment_issue` | Payment & Billing Dispute | FinOps Billing & Fraud Team | 1,006 |
| `product_complaint` | Product Defect & Hardware RMA | Quality Engineering & RMA Desk | 1,038 |
| `delivery_problem` | Logistics & Dispatch Delay | Global Supply Chain & Logistics | 999 |
| `technical_issue` | Software Bug & Platform Outage | Tier-3 Engineering & DevOps | 986 |
| `account_issue` | IAM & Account Security | Identity & Access Management (IAM) | 972 |
| `service_dissatisfaction` | Customer Experience Escalation | Executive Customer Relations | 999 |
| **Total** | | | **6,000** |

### Priority Distribution
- **Medium (36.1%):** 2,166 samples
- **High (29.9%):** 1,795 samples
- **Low (19.8%):** 1,185 samples
- **Critical (14.2%):** 854 samples
