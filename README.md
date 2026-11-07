# Seller Operations & Payout Monitoring System

An end-to-end Data Engineering project built using Python, SQL, SQLite, Pandas, and Pytest to monitor seller operations, order fulfillment, disputes, commissions, payout eligibility, and operational exceptions.

## 1. Project Overview

This project simulates an e-commerce seller operations platform. It generates synthetic business data, validates data relationships, applies business rules, monitors seller performance, and identifies payout-related exceptions.

The system helps track seller activities and detect operational issues that may affect payout accuracy and business performance.

## 2. Key Features

- Synthetic seller and product listing data generation
- Order and order-line processing
- Multi-seller order management
- Shipment and delivery tracking
- Commission and reserve calculations
- Dispute and chargeback monitoring
- Payout eligibility validation
- Seller performance metrics
- Operational exception detection
- Data integrity and business rule validation
- CSV, JSON, and SQLite data exports
- Fixed-seed reproducible data generation

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data generation and business logic |
| SQL | Data querying and management |
| SQLite | Relational database |
| Pandas | Data processing |
| CSV / JSON | Data storage and export |
| Pytest | Automated testing |
| Git & GitHub | Version control |

## 4. Project Structure

```text
Seller-Operations-Payout-Monitoring/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── ground_truth/
│   ├── sql/
│   ├── README_generated.md
│   ├── source_manifest.json
│   └── validation_summary.json
│
├── docs/
│   └── data_dictionary.md
│
├── src/
│   ├── __init__.py
│   └── generate_data.py
│
├── tests/
│   ├── test_exceptions.py
│   └── test_validation.py
│
├── .gitignore
└── README.md
```

## 5. Main Data Entities

1. Seller
2. Product Listing
3. Commission Rule
4. Order
5. Order Line
6. Fulfillment
7. Customer Review
8. Dispute
9. Payout
10. Payout Line
11. Event History
12. Seller Metrics
13. Exception Cases

## 6. Exception Scenarios

The system includes the following business exception scenarios:

- Payout before delivery or hold release
- Duplicate commission application
- Suspended seller with an active listing
- Missing dispute deduction
- Payout reconciliation mismatch

Ground-truth labels are generated to identify expected exception outcomes.

## 7. Data Validation

The generator performs data validation checks, including:

- Primary key uniqueness
- Foreign key relationships
- Required field validation
- Business rule checks
- Date consistency
- Payout amount reconciliation
- Entity relationship consistency

## 8. Installation

Install the required Python packages:

```bash
pip install pandas pytest
```

## 9. Data Generation

Run the generator from the project root:

Starter dataset:

```bash
python src/generate_data.py --scale 0.01
```

Full-scale dataset:

```bash
python src/generate_data.py --scale 1.0
```

The project uses a fixed random seed:

```text
20261022
```

This supports reproducible synthetic data generation.

## 10. Automated Testing

Run the automated tests:

```bash
python -m pytest tests/ -v
```

The test suite checks data uniqueness, basic data validity, payout values, dispute statuses, and exception scenarios.

## 11. Generated Outputs

The project generates:

- Raw CSV files
- Processed JSON files
- Ground-truth exception data
- SQLite database and SQL exports
- Source manifest
- Validation summary

## 12. Validation Status

The starter dataset completed successfully with:

```text
Validation: PASS
Seed: 20261022
Scale: 0.01
```

Full-scale generation and reproducibility checks are pending final verification.

## 13. Documentation
docs/data_dictionary.md – Entity and field definitions.
data/README_generated.md – Generated dataset details.
data/source_manifest.json – Dataset provenance.
data/validation_summary.json – Validation results.

14. Project Objective
This project demonstrates practical skills in:

Python programming

Data engineering fundamentals

Relational database design

SQL and SQLite

Synthetic data generation

Data quality and validation

Business rule implementation

Exception and anomaly monitoring

Automated testing

Git and GitHub version control
