## 1. Project Overview

The Seller Operations & Payout Monitoring System is a Python-based project designed to monitor seller performance and manage the order-to-payout workflow.

It handles seller information, product listings, orders, fulfillment, customer reviews, disputes, commissions, and payouts. The system also identifies important exceptions and maintains records of relevant events.

## 2. Problem Statement

Managing multiple sellers and their transactions can lead to issues such as delayed shipments, incorrect commission calculations, unresolved disputes, and incorrect payouts.

This project addresses these challenges by generating related business data, applying predefined business rules, validating transactions, and identifying exceptions.

## 3. Project Objectives

- Monitor seller service levels and performance.
- Track orders and fulfillment activities.
- Calculate commissions and payout eligibility.
- Account for disputes, refunds, and reserve holds.
- Identify incorrect transactions and business exceptions.
- Maintain event history for traceability.
- Generate measurable validation results.

## 4. Business Workflow

The system follows an end-to-end workflow:

1. Create seller and product listing records.
2. Generate customer orders across sellers.
3. Create order lines and fulfillment records.
4. Track shipment and delivery activities.
5. Record customer reviews and disputes.
6. Apply commission and reserve rules.
7. Calculate eligible payout lines.
8. Validate payout totals and identify exceptions.
9. Generate ground-truth records and validation reports.

## 5. Key Entities

The project includes the following business entities:

- Seller
- ProductListing
- Order
- OrderLine
- Fulfillment
- CustomerReview
- Dispute
- CommissionRule
- Payout
- PayoutLine
- EventHistory
- SellerMetrics
- ExceptionCases

Each entity has its own identifiers and related records to support data consistency and traceability.

## 6. Business Exception Scenarios

The project covers five important negative scenarios:

1. Payout generated before delivery or hold release.
2. Commission applied more than once.
3. Suspended seller continues listing products.
4. Dispute amount not deducted from payout.
5. Payout total does not match the sum of payout lines.

These scenarios are used to evaluate whether the system identifies incorrect business outcomes.

## 7. Synthetic Dataset

The generator supports configurable dataset sizes using a fixed random seed.

Full-scale dataset:

- Sellers: 2,000
- Product Listings: 20,000
- Orders: 100,000
- Disputes: 10,000

The generated dataset also includes related order lines, fulfillment records, reviews, payouts, event history, seller metrics, and exception cases.

## 8. Validation and Quality Checks

The project performs validation checks to ensure:

- Primary keys are unique.
- Foreign key relationships are valid.
- Business status values follow allowed rules.
- Dates follow the expected order.
- Financial calculations are consistent.
- Duplicate records and business exceptions are identified.
- Generated outcomes follow documented rules.

## 9. Ground Truth and Reproducibility

Separate ground-truth CSV and JSON files are generated to identify known exception scenarios and expected outcomes.

The generator uses seed `20261022` to support reproducible results. Two full-scale runs were compared across 37 files, and all 37 files matched.

## 10. Data Provenance

This project uses synthetic data generated specifically for testing and demonstration. No real customer or seller personal information is required.

## 11. Project Execution

Generate the full dataset:

```bash
python src/generate_data.py --scale 1.0
```

Run automated tests:

```bash
python -m pytest tests/ -v
```

## 12. Project Outcome

The project successfully generated the full-scale dataset, completed validation without errors, passed all 10 automated tests, and produced matching results across two reproducibility runs.
