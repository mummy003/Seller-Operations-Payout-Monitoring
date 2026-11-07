# Seller Operations Payout Monitoring

## 1. Project Overview
This data dictionary defines the entities, attributes, data types, constraints, relationships, and validation rules used in the Seller Operations Payout Monitoring System.

## 2. Seller

| Field | Data Type | Required | Validation |
|---|---|---|---|
| seller_id (PK) | VARCHAR(15) | Yes | Unique, format SELL-000001 |
| seller_name | VARCHAR(100) | Yes | Non-empty |
| email | VARCHAR(150) | Yes | Valid email, unique |
| phone | VARCHAR(15) | No | Valid phone format |
| registration_date | DATE | Yes | Valid date |
| seller_status | VARCHAR(20) | Yes | ACTIVE, SUSPENDED, INACTIVE |
| service_score | DECIMAL(5,2) | No | Range 0–100 |
| created_at | TIMESTAMP | Yes | Valid timestamp |

## 3. ProductListing

| Field | Data Type | Required | Validation |
|---|---|---|---|
| listing_id (PK) | VARCHAR(30) | Yes | Unique, LIST-SELL-000001 |
| seller_id (FK) | VARCHAR(15) | Yes | Must exist in Seller |
| product_name | VARCHAR(150) | Yes | Non-empty |
| category | VARCHAR(50) | Yes | Valid category |
| price | DECIMAL(12,2) | Yes | Greater than 0, currency INR |
| stock_quantity | INT | Yes | Minimum 0, unit: pieces |
| listing_status | VARCHAR(20) | Yes | ACTIVE, INACTIVE, SUSPENDED |
| created_at | TIMESTAMP | Yes | Valid timestamp |

## 4. Order

| Field | Data Type | Required | Validation |
|---|---|---|---|
| order_id (PK) | VARCHAR(20) | Yes | Unique, ORD-2026-000001 |
| customer_id | VARCHAR(20) | Yes | Valid synthetic customer ID |
| order_date | TIMESTAMP | Yes | Valid timestamp |
| order_status | VARCHAR(20) | Yes | PLACED, CONFIRMED, SHIPPED, DELIVERED, CANCELLED, RETURNED |
| total_amount | DECIMAL(12,2) | Yes | Must equal order line totals |
| currency | CHAR(3) | Yes | INR |
| created_at | TIMESTAMP | Yes | Valid timestamp |

## 5. OrderLine

| Field | Data Type | Required | Validation |
|---|---|---|---|
| order_line_id (PK) | VARCHAR(30) | Yes | Unique and immutable |
| order_id (FK) | VARCHAR(20) | Yes | Must exist in Order |
| listing_id (FK) | VARCHAR(30) | Yes | Must exist in ProductListing |
| seller_id (FK) | VARCHAR(15) | Yes | Must match listing owner |
| quantity | INT | Yes | Greater than 0 |
| unit_price | DECIMAL(12,2) | Yes | Greater than 0 |
| line_total | DECIMAL(12,2) | Yes | quantity × unit_price |

## 6. Fulfillment

| Field | Data Type | Required | Validation |
|---|---|---|---|
| fulfillment_id (PK) | VARCHAR(40) | Yes | FUL- followed by order_line_id |
| order_line_id (FK) | VARCHAR(30) | Yes | Must exist in OrderLine |
| seller_id (FK) | VARCHAR(15) | Yes | Must exist in Seller |
| shipment_date | TIMESTAMP | No | Cannot precede order date |
| delivery_date | TIMESTAMP | No | Cannot precede shipment date |
| fulfillment_status | VARCHAR(20) | Yes | PENDING, PACKED, SHIPPED, DELIVERED, RETURNED, CANCELLED |
| tracking_number | VARCHAR(50) | No | Unique when present |

## 7. CustomerReview

| Field | Data Type | Required | Validation |
|---|---|---|---|
| review_id (PK) | VARCHAR(25) | Yes | Unique |
| order_line_id (FK) | VARCHAR(30) | Yes | Must exist in OrderLine |
| seller_id (FK) | VARCHAR(15) | Yes | Must exist in Seller |
| rating | INT | Yes | Range 1–5 |
| review_text | VARCHAR(500) | No | Maximum 500 characters |
| review_date | TIMESTAMP | Yes | After order date |
 
## 8. Dispute

| Field | Data Type | Required | Validation |
|---|---|---|---|
| dispute_id (PK) | VARCHAR(20) | Yes | DSP-2026-000001 |
| order_id (FK) | VARCHAR(20) | Yes | Must exist in Order |
| seller_id (FK) | VARCHAR(15) | Yes | Must exist in Seller |
| dispute_type | VARCHAR(30) | Yes | REFUND, CHARGEBACK, PRODUCT_ISSUE, DELIVERY_ISSUE |
| dispute_amount | DECIMAL(12,2) | Yes | Greater than 0 |
| dispute_status | VARCHAR(20) | Yes | OPEN, UNDER_REVIEW, RESOLVED, REJECTED |
| resolution_date | DATE | No | Cannot precede dispute date |
| created_at | TIMESTAMP | Yes | Valid timestamp |

## 9. CommissionRule

| Field | Data Type | Required | Validation |
|---|---|---|---|
| commission_rule_id (PK) | VARCHAR(20) | Yes | Unique |
| seller_id (FK) | VARCHAR(15) | No | Null means general rule |
| category | VARCHAR(50) | Yes | Valid product category |
| commission_rate | DECIMAL(5,2) | Yes | Range 0–100, percentage |
| reserve_rate | DECIMAL(5,2) | Yes | Range 0–100, percentage |
| hold_days | INT | Yes | Minimum 0, unit: days |
| effective_from | DATE | Yes | Valid date |
| effective_to | DATE | No | Must be after effective_from |
| rule_status | VARCHAR(20) | Yes | ACTIVE, INACTIVE |

## 10. Payout

| Field | Data Type | Required | Validation |
|---|---|---|---|
| payout_id (PK) | VARCHAR(25) | Yes | PAYOUT-2026-000001 |
| seller_id (FK) | VARCHAR(15) | Yes | Must exist in Seller |
| payout_date | DATE | Yes | Valid date |
| gross_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| commission_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| refund_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| dispute_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| reserve_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| net_amount | DECIMAL(12,2) | Yes | Calculated from payout components |
| payout_status | VARCHAR(20) | Yes | PENDING, APPROVED, PAID, ON_HOLD, FAILED |

## 11. PayoutLine

| Field | Data Type | Required | Validation |
|---|---|---|---|
| payout_line_id (PK) | VARCHAR(30) | Yes | Unique |
| payout_id (FK) | VARCHAR(25) | Yes | Must exist in Payout |
| order_line_id (FK) | VARCHAR(30) | Yes | Must exist in OrderLine |
| gross_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| commission_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| refund_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| dispute_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| reserve_amount | DECIMAL(12,2) | Yes | Minimum 0 |
| net_amount | DECIMAL(12,2) | Yes | Calculated from line components |

## 12. Entity Relationships and Cardinality

1. Seller → ProductListing: One-to-Many (1:N).
2. Order → OrderLine: One-to-Many (1:N).
3. ProductListing → OrderLine: One-to-Many (1:N).
4. Seller → OrderLine: One-to-Many (1:N).
5. OrderLine → Fulfillment: One-to-One (1:1) in the baseline design.
6. OrderLine → CustomerReview: One-to-Zero-or-One (1:0..1).
7. Order → Dispute: One-to-Many (1:N).
8. Seller → Dispute: One-to-Many (1:N).
9. Seller → Payout: One-to-Many (1:N).
10. Payout → PayoutLine: One-to-Many (1:N).
11. OrderLine → PayoutLine: One-to-Many (1:N) when partial payouts are allowed.
12. CommissionRule → Seller: Optional seller-specific rule; general rules may apply to multiple sellers.

An Order can contain products from multiple sellers. OrderLine acts as the bridge between Order, ProductListing, and Seller.

## 13. Common Data Validation Rules

- All primary keys must be unique and non-null.
- All foreign keys must reference existing parent records.
- Dates must follow valid chronological order.
- Monetary values must use INR and DECIMAL precision.
- Quantities must be positive integers.
- Commission and reserve rates must be between 0 and 100.
- Suspended sellers must not create new active listings.
- Payouts must only include eligible delivered order lines after applicable hold periods.
- Commission must not be applied more than once to the same eligible transaction.
- Payout totals must reconcile with their payout lines.
- Disputes and refunds must be deducted according to documented rules.
- Historical status changes must be retained as separate events rather than overwriting history.

## 14. Synthetic Data and Reproducibility

- Use synthetic data only for the baseline dataset.
- Use fixed random seed: 20261022.
- Keep entity IDs immutable and consistently referenced.
- Generate valid baseline records before injecting anomalies.
- Store anomaly labels separately in ground_truth.
- Validate primary keys, foreign keys, arithmetic, lifecycle transitions, and duplicate records.
- Regenerate datasets using the same seed and compare row counts and checksums.

**Document Status:** Initial Data Dictionary Specification  
**Project:** Seller Operations Payout Monitoring  
**Technology:** Python, SQL, CSV and JSON
