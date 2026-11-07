# Seller Operations & Payout Monitoring System

## 1. Project Overview

The Seller Operations & Payout Monitoring System is a Python-based project designed to monitor seller performance and manage the complete order-to-payout workflow.

It covers seller management, product listings, order processing, fulfillment, customer reviews, disputes, commission calculations, and payout eligibility.

The system generates synthetic business data, applies predefined business rules, validates transactions, and identifies important business exceptions.

## 2. Problem Statement

Managing multiple sellers and their transactions can create operational challenges such as delayed shipments, incorrect commission calculations, unresolved disputes, and incorrect payouts.

This project aims to address these challenges by generating realistic business data, applying business rules, monitoring seller activities, validating financial calculations, and identifying exceptions.

## 3. Project Objectives

- Monitor seller service levels and performance.
- Track orders, shipments, and deliveries.
- Calculate commissions and payout eligibility.
- Manage disputes, refunds, and reserve holds.
- Identify incorrect transactions and business exceptions.
- Maintain event history for traceability.
- Generate validation reports and measurable outputs.
- Support reproducible synthetic data generation.

## 4. Primary Actors

The system is designed around the following business actors:

- Customer
- Store/Warehouse Operator
- Merchandising/E-commerce Analyst
- Operations Manager

## 5. Business Workflow

The project follows an end-to-end business workflow:

1. Generate seller and product listing master data.
2. Generate customer orders across multiple sellers.
3. Create order lines using valid product and order references.
4. Split multi-seller orders into fulfillment records.
5. Record shipment and delivery activities.
6. Generate customer reviews and disputes.
7. Apply commission and reserve rules.
8. Calculate payout lines based on delivery and hold conditions.
9. Validate payout calculations and transaction relationships.
10. Generate exception records and ground-truth labels.

## 6. Key Business Entities

The project includes the following entities:

| Entity | Description |
|---|---|
| Seller | Stores seller information and status |
| ProductListing | Contains seller product listings |
| Order | Stores customer order information |
| OrderLine | Contains individual order items |
| Fulfillment | Tracks shipment and delivery |
| CustomerReview | Stores customer feedback |
| Dispute | Tracks disputes and chargebacks |
| CommissionRule | Defines commission percentages and rules |
| Payout | Stores seller payout information |
| PayoutLine | Contains individual payout calculations |
| EventHistory | Maintains business event history |
| SellerMetrics | Stores calculated seller performance metrics |
| ExceptionCases | Stores identified business exceptions |

## 7. ID and Naming Conventions

The generator uses consistent, deterministic identifiers.

Examples:

- Seller: `SELL-000001`
- Product Listing: `LIST-<seller-id>-000001`
- Order: `ORD-2026-000001`
- Fulfillment: `FUL-<order-line-id>`
- Dispute: `DSP-2026-000001`
- Payout: `PAYOUT-2026-000001`

Identifiers are generated consistently to maintain relationships between records.

## 8. Synthetic Data Generation

The project uses a Python-based synthetic data generator with a fixed random seed and configurable scale.

**Full-scale dataset:**

| Dataset | Records |
|---|---:|
| Seller | 2,000 |
| Product Listing | 20,000 |
| Commission Rule | 5 |
| Order | 100,000 |
| Order Line | 250,217 |
| Fulfillment | 250,217 |
| Customer Review | 74,828 |
| Dispute | 10,000 |
| Payout | 1,327 |
| Payout Line | 246,154 |
| Event History | 510,115 |
| Seller Metrics | 2,000 |
| Exception Cases | 5 |

**Generation settings:**

- Random Seed: `20261022`
- Scale: `1.0`
- Validation Status: PASS

The same generator supports both smaller test datasets and full-scale datasets.

## 9. Business Rules and Exception Scenarios

The project includes business rules related to seller status, order fulfillment, commissions, disputes, reserve holds, and payout eligibility.

The following five exception scenarios are covered:

1. Payout generated before delivery or hold release.
2. Commission applied more than once.
3. Suspended seller continues listing products.
4. Dispute amount not deducted from payout.
5. Payout total does not match the sum of payout lines.

These scenarios help evaluate whether incorrect business outcomes can be identified.

## 10. Data Validation

The project performs validation checks to maintain data quality and consistency.

Validation includes:

- Primary key uniqueness.
- Foreign key integrity.
- Allowed status and enum values.
- Date ordering and consistency.
- Financial calculation checks.
- Duplicate record detection.
- Lifecycle and business rule checks.
- Exception identification.

**Full-scale validation result: PASS**

No validation errors were reported in the completed full-scale run.

## 11. Ground Truth

Separate ground-truth files are generated in CSV and JSON formats.

They contain known exception scenarios and expected labels based on documented business rules.

Ground-truth records are maintained separately from the generated input datasets.

## 12. Reproducibility

The generator uses a fixed seed (`20261022`) to produce reproducible results.

Two full-scale runs were compared using SHA-256 checksums.

| Check | Result |
|---|---:|
| Files Compared | 37 |
| Identical Files | 37 |
| Different Files | 0 |
| Missing Files | 0 |
| New Files | 0 |

**Reproducibility Status: PASS**

## 13. Test Execution Results

The project was tested using Python and Pytest.

**Test Environment:**
- Python: 3.13.18
- Pytest: 8.4.2

| Test Case | Result |
|---|---|
| Payout Before Delivery | PASS |
| Duplicate Commission | PASS |
| Suspended Seller Listing | PASS |
| Missing Dispute Deduction | PASS |
| Payout Total Mismatch | PASS |
| Seller Validation | PASS |
| Order Validation | PASS |
| Order Line Validation | PASS |
| Payout Validation | PASS |
| Dispute Validation | PASS |

**Test Summary:**
- Total Tests: 10
- Passed: 10
- Failed: 0
- Execution Time: 1.75 seconds

See [Test Execution Report](test-results/test_execution_report.md) for the detailed results.

## 14. Project Structure

```text
Seller-Operations-Payout-Monitoring/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── ground_truth/
│   ├── source_manifest.json
│   └── validation_summary.json
│
├── src/
│   └── generate_data.py
│
├── tests/
│   ├── test_validation.py
│   └── test_exceptions.py
│
├── docs/
│
├── test-results/
│   └── test_execution_report.md
│
└── README.md
```

Some large generated datasets and SQL exports may not be committed because of GitHub file-size limitations. They can be recreated using the generator.

## 15. Technologies Used

- Python
- Pandas
- SQLite
- CSV
- JSON
- SQL
- Pytest
- Git
- GitHub
- SHA-256

## 16. How to Run the Project

**Step 1: Clone the repository**

```bash
git clone https://github.com/mummy003/Seller-Operations-Payout-Monitoring.git
```

**Step 2: Open the project directory**

```bash
cd Seller-Operations-Payout-Monitoring
```

**Step 3: Install dependencies**

```bash
pip install pandas pytest
```

**Step 4: Generate the full-scale dataset**

```bash
python src/generate_data.py --scale 1.0
```

**Step 5: Run automated tests**

```bash
python -m pytest tests/ -v
```

## 17. Data Provenance

This project uses synthetic data generated specifically for development, testing, and demonstration.

No real customer or seller personal information is required. The generated records are intended to simulate business transactions and operational scenarios.

## 18. Project Outcome

The project successfully generated the full-scale synthetic dataset, completed data validation, covered five required exception scenarios, passed all 10 automated tests, and demonstrated reproducibility across two full-scale runs.

It provides a foundation for monitoring seller operations, validating payout calculations, and identifying business exceptions.
## Test Results

For detailed test execution results, data validation, and reproducibility details, see the [Test Execution Report](test-results/test_execution_report.md).
