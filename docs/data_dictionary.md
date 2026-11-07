# Seller Operations & Payout Monitoring
## Data Dictionary

### 1. Project Overview

This document describes the entities, attributes, relationships, identifiers, and validation rules used in the Seller Operations & Payout Monitoring project.

The project uses synthetic data to monitor seller performance, product listings, orders, fulfillment, customer reviews, disputes, commissions, and payouts.

- Data type: Synthetic
- Random seed: 20261022
- Currency: INR
- Primary keys uniquely identify records.
- Foreign keys connect related entities.
- Ground-truth labels are maintained separately from operational data.

---

### 2. Seller

**Description:** Stores seller registration and operational information.

| Column | Description | Key |
|---|---|---|
| seller_id | Unique seller identifier (SELL-000001) | PK |
| seller_name | Seller name | |
| seller_status | Seller status: ACTIVE, SUSPENDED, INACTIVE | |
| country | Seller country | |
| created_date | Seller creation date | |
| service_level_target_pct | Required service-level target percentage | |

**Rules:**
- seller_id must be unique.
- seller_status must contain an allowed value.
- Service-level target must be between 0 and 100.

---

### 3. ProductListing

**Description:** Stores products listed by sellers.

| Column | Description | Key |
|---|---|---|
| listing_id | Unique listing identifier | PK |
| seller_id | Seller who owns the listing | FK |
| product_name | Product name | |
| category | Product category | |
| unit_price | Price per product in INR | |
| listing_status | ACTIVE or INACTIVE | |
| created_date | Listing creation date | |

**Rules:**
- Every listing must reference an existing seller.
- Unit price must be greater than zero.
- A suspended seller must not create an active listing.

---

### 4. Order

**Description:** Stores customer order information.

| Column | Description | Key |
|---|---|---|
| order_id | Unique order identifier (ORD-2026-000001) | PK |
| customer_id | Customer identifier | |
| order_date | Date the order was placed | |
| order_status | CANCELLED, FULFILLED, IN_PROGRESS | |
| order_total | Total order amount in INR | |
| currency | Transaction currency (INR) | |

**Rules:**
- order_id must be unique.
- order_total must not be negative.
- An order may contain multiple order lines.

---

### 5. OrderLine

**Description:** Connects orders, products, and sellers. It supports orders containing products from multiple sellers.

| Column | Description | Key |
|---|---|---|
| order_line_id | Unique order-line identifier | PK |
| order_id | Related order identifier | FK |
| listing_id | Related product listing identifier | FK |
| seller_id | Seller responsible for the order line | FK |
| quantity | Number of units ordered | |
| unit_price | Price per unit in INR | |
| line_total | quantity × unit_price | |

**Rules:**
- Every order line must reference an existing order, listing, and seller.
- Quantity must be greater than zero.
- line_total must equal quantity multiplied by unit_price.
- An order can contain multiple order lines.

---

### 6. Fulfillment

**Description:** Tracks the shipment and delivery status of each order line.

| Column | Description | Key |
|---|---|---|
| fulfillment_id | Unique fulfillment identifier (FUL- + order_line_id) | PK |
| order_line_id | Related order line | FK |
| seller_id | Seller responsible for fulfillment | FK |
| fulfillment_status | CREATED, SHIPPED, DELIVERED, RETURNED | |
| created_date | Fulfillment creation date | |
| shipped_date | Shipment date | |
| delivered_date | Delivery date | |
| is_late | Indicates whether fulfillment was late | |
| is_returned | Indicates whether the item was returned | |

**Rules:**
- Every fulfillment must reference a valid order line and seller.
- Fulfillment dates must follow a valid chronological order.
- A delivered fulfillment must have a delivery date.
- Late and returned indicators must be Boolean values.

---

### 7. CustomerReview

**Description:** Stores customer feedback for delivered order lines.

| Column | Description | Key |
|---|---|---|
| review_id | Unique review identifier | PK |
| order_line_id | Related order line | FK |
| seller_id | Seller being reviewed | FK |
| rating | Customer rating | |
| review_date | Date of review | |
| review_text | Customer feedback text | |

**Rules:**
- Every review must reference a valid order line and seller.
- Rating must be between 1 and 5.
- Review date must not be earlier than the order date.

---

### 8. Dispute

**Description:** Stores customer disputes and chargeback-related records.

| Column | Description | Key |
|---|---|---|
| dispute_id | Unique dispute identifier (DSP-2026-000001) | PK |
| order_line_id | Related order line | FK |
| seller_id | Seller involved in the dispute | FK |
| dispute_type | CHARGEBACK, ITEM_NOT_RECEIVED, NOT_AS_DESCRIBED | |
| dispute_status | OPEN, WON, LOST | |
| dispute_amount | Disputed amount in INR | |
| created_date | Date the dispute was created | |
| resolved_date | Date the dispute was resolved | |

**Rules:**
- Every dispute must reference an existing order line and seller.
- Dispute amount must be greater than zero.
- A resolved dispute must have a resolution date.
- Open disputes may cause payout holds.

---

### 9. CommissionRule

**Description:** Defines commission and reserve percentages for product categories.

| Column | Description | Key |
|---|---|---|
| commission_rule_id | Unique commission rule identifier | PK |
| category | Product category | |
| commission_rate_pct | Commission percentage | |
| reserve_rate_pct | Reserve percentage | |
| effective_from | Rule start date | |
| effective_to | Rule end date | |
| is_active | Indicates whether the rule is active | |

**Rules:**
- Commission and reserve percentages must be between 0 and 100.
- Effective end date must not be earlier than effective start date.
- The applicable rule must be selected using the product category and effective dates.
- Commission must not be applied more than once to the same payout line.

---

### 10. Payout

**Description:** Stores seller payout summary information.

| Column | Description | Key |
|---|---|---|
| payout_id | Unique payout identifier (PAYOUT-2026-000001) | PK |
| seller_id | Seller receiving the payout | FK |
| payout_date | Payout processing date | |
| payout_status | ELIGIBLE | |
| payout_total | Total payout amount in INR | |
| currency | Payout currency (INR) | |

**Rules:**
- Every payout must reference an existing seller.
- Payout total must match the sum of its payout lines.
- Only eligible delivered order lines should be considered for payout.
- Payouts must respect the configured hold period.
- Returned orders and applicable disputes must be considered before payout eligibility.

---

### 11. PayoutLine

**Description:** Stores the payout calculation for individual order lines.

| Column | Description | Key |
|---|---|---|
| payout_line_id | Unique payout-line identifier | PK |
| payout_id | Related payout identifier | FK |
| order_line_id | Related order line | FK |
| gross_amount | Original order-line amount in INR | |
| commission_amount | Commission deducted in INR | |
| reserve_amount | Reserve amount held in INR | |
| refund_amount | Refund amount in INR | |
| net_amount | Final payout amount in INR | |

**Calculation:**

net_amount = gross_amount - commission_amount - reserve_amount - refund_amount

**Rules:**
- Every payout line must reference an existing payout and order line.
- Amounts must not be negative.
- Commission must not be deducted twice.
- Payout totals must reconcile with payout-line totals.

---

### 12. EventHistory

**Description:** Maintains an audit trail of operational state changes.

| Column | Description | Key |
|---|---|---|
| event_id | Unique event identifier | PK |
| entity_type | Type of entity affected | |
| entity_id | Identifier of the affected record | |
| event_type | Event or action performed | |
| event_date | Date and time of the event | |
| from_state | Previous state | |
| to_state | New state | |

**Rules:**
- Each event must have a unique event_id.
- Events should preserve state-change history.
- Previous records must not be silently overwritten.
- Event dates must follow a valid sequence.

---

### 13. SellerMetrics

**Description:** Stores calculated seller performance metrics.

| Column | Description |
|---|---|
| seller_id | Seller identifier |
| delivered_fulfillment_count | Number of delivered fulfillments |
| late_fulfillment_count | Number of late fulfillments |
| on_time_rate_pct | On-time fulfillment percentage |
| average_review_rating | Average customer rating |
| seller_status | Current seller status |
| meets_service_target | Indicates whether seller meets the service target |

**Rules:**
- Metrics must be calculated from source records.
- Counts must not be negative.
- On-time rate must be between 0 and 100.
- Seller metrics must be traceable to fulfillment and review records.

---

### 14. ExceptionCases

**Description:** Stores documented business exception scenarios and their ground-truth labels.

| Column | Description |
|---|---|
| case_id | Unique exception case identifier |
| issue_type | Type of business exception |
| ground_truth | Expected anomaly label |
| expected_decision | Expected business decision |
| affected_entity | Entity affected by the exception |
| affected_record_id | Identifier of the affected record |

**Supported exception scenarios:**
1. Payout attempted before delivery or hold-period release.
2. Commission applied more than once.
3. Suspended seller continues creating active listings.
4. Applicable dispute amount is not deducted.
5. Payout total does not match payout-line totals.

**Rules:**
- Every exception must have a documented issue type.
- Ground-truth labels must be derived from defined business rules.
- Ground-truth information must be kept separate from model input features.

---

### 15. Entity Relationships

| Parent Entity | Child Entity | Relationship |
|---|---|---|
| Seller | ProductListing | One-to-Many |
| Seller | OrderLine | One-to-Many |
| Seller | Fulfillment | One-to-Many |
| Seller | CustomerReview | One-to-Many |
| Seller | Dispute | One-to-Many |
| Seller | Payout | One-to-Many |
| Order | OrderLine | One-to-Many |
| ProductListing | OrderLine | One-to-Many |
| OrderLine | Fulfillment | One-to-One |
| OrderLine | CustomerReview | One-to-Zero-or-One |
| OrderLine | Dispute | One-to-Many |
| Payout | PayoutLine | One-to-Many |
| OrderLine | PayoutLine | One-to-Many |

**Many-to-Many relationship:**

Order and ProductListing have a many-to-many relationship resolved through OrderLine.

An order may contain multiple products, and a product listing may appear in multiple orders.

---

### 16. Primary and Foreign Key Rules

- Primary keys must uniquely identify each record.
- Primary keys must not be null.
- Foreign keys must reference existing parent records.
- Duplicate primary-key values are not allowed.
- Relationships must be validated before generating dependent records.

---

### 17. Business Validation Rules

1. Suspended sellers must not have new active listings.
2. Every order line must reference a valid order, listing, and seller.
3. Fulfillment records must reference valid order lines.
4. Delivery dates must not precede shipment dates.
5. Customer ratings must be between 1 and 5.
6. Commission and reserve rates must be between 0 and 100.
7. Commission must not be deducted more than once.
8. Payout eligibility must depend on delivery and the configured hold period.
9. Returned orders and applicable disputes must be considered in payout calculations.
10. Payout totals must reconcile with payout-line totals.
11. All state changes must be traceable through event history.
12. Exception cases must have documented ground-truth labels.

---

### 18. Data Generation and Reproducibility

- All project data is synthetically generated.
- Random seed: 20261022.
- The generator supports configurable scale.
- Starter and full-scale datasets use the same generation logic.
- Master records are generated before dependent transaction records.
- Dependent records use valid parent identifiers.
- Business exceptions are documented separately.
- Validation results are exported in validation_summary.json.
- Source information is documented in source_manifest.json.
- Generated data is available in CSV, JSON, and SQL formats.

---

### 19. Expected Validation Checks

| Validation | Expected Result |
|---|---|
| Primary key uniqueness | PASS |
| Foreign key integrity | PASS |
| Allowed status values | PASS |
| Date ordering | PASS |
| Positive quantity and price | PASS |
| Commission and reserve range | PASS |
| Payout arithmetic | PASS |
| Payout reconciliation | PASS |
| Duplicate commission detection | PASS |
| Exception ground-truth availability | PASS |
| Reproducibility with fixed seed | PASS |

---

**Document Status:** Corrected Data Dictionary Specification  
**Project:** Seller Operations & Payout Monitoring  
**Data Type:** Synthetic  
**Random Seed:** 20261022
