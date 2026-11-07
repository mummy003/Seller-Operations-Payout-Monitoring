# Seller Operations & Payout Monitoring System

An end-to-end data engineering project built using Python, SQL, and SQLite to monitor seller performance, order fulfillment, disputes, commissions, payout eligibility, and operational exceptions.

## 1. Project Overview

This project simulates an e-commerce seller operations platform. It generates structured business data, validates relationships and business rules, tracks seller performance, and identifies payout-related exceptions.

## 2. Key Features

- Synthetic seller and product listing data generation
- Order and order-line management
- Multi-seller order fulfillment tracking
- Shipment and delivery monitoring
- Commission and reserve calculations
- Dispute and chargeback tracking
- Payout eligibility monitoring
- Seller performance metrics
- Exception and anomaly scenario generation
- Data validation and integrity checks
- CSV, JSON, and SQL/SQLite data outputs

## 3. Technology Stack

- Python
- SQL
- SQLite
- Pandas
- CSV and JSON
- Pytest
- Git and GitHub

## 4. Project Structure

```text
Seller-Operations-Payout-Monitoring/
│
├── data/
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

## 5. Data Entities

The system contains the following major entities:

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

The project includes the following operational exception scenarios:

- Payout before delivery or hold release
- Duplicate commission
- Active listing belonging to a suspended seller
- Missing dispute deduction
- Payout total mismatch

## 7. Data Validation

The validation process includes:

- Primary key uniqueness
- Foreign key integrity
- Required field checks
- Business rule validation
- Data consistency checks

## 8. Test Execution

Install pytest:

```bash
pip install pytest
```

Run tests from the project root:

```bash
pytest -v
```

## 9. Data Generation

Run the data generator from the project root:

```bash
python src/generate_data.py --scale 0.01
```

For full-scale generation:

```bash
python src/generate_data.py --scale 1.0
```

The random seed used for reproducible data generation is:

```text
20261022
```

## 10. Validation Result

The starter dataset generation completed successfully with validation status `PASS`.

See `data/validation_summary.json` for the generated dataset's validation status and row counts.

## 11. Documentation

Refer to:

- `docs/data_dictionary.md` for entity and field definitions.
- `data/README_generated.md` for generated dataset information.
- `data/source_manifest.json` for dataset provenance information.
- `data/validation_summary.json` for validation results.

## 12. Project Purpose

This project demonstrates practical skills in Python-based data generation, SQL data management, relational data modeling, data validation, business rule implementation, and exception monitoring.
