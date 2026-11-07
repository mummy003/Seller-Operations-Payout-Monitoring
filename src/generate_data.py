
import argparse
import csv
import hashlib
import json
import random
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

# ============================================================
# SELLER OPERATIONS PAYOUT MONITORING
# Fixed-seed, reproducible synthetic data generator
# ============================================================

SEED = 20261022
AS_OF = date(2026, 11, 7)
YEAR = 2026

CATEGORIES = [
    "Electronics", "Fashion", "Home", "Beauty", "Books"
]

COMMISSION = {
    "Electronics": 12.0,
    "Fashion": 15.0,
    "Home": 10.0,
    "Beauty": 14.0,
    "Books": 8.0
}

RESERVE_RATE = 5.0
HOLD_DAYS = 7

STATUSES = ["ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE", "UNDER_REVIEW", "SUSPENDED"]


def iso(value):
    return value.isoformat() if value else None


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(rows, indent=2, default=str),
        encoding="utf-8"
    )


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def generate(scale=1.0):
    random.seed(SEED)

    root = Path(__file__).resolve().parents[1]
    out = root / "data"

    raw_dir = out / "raw"
    processed_dir = out / "processed"
    truth_dir = out / "ground_truth"
    sql_dir = out / "sql"

    for folder in [raw_dir, processed_dir, truth_dir, sql_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    def scaled(number):
        return max(1, int(number * scale))

    seller_count = scaled(2000)
    listing_count = scaled(20000)
    order_count = scaled(100000)
    dispute_count = scaled(10000)

    rng = random.Random(SEED)

    tables = {}
    events = []
    ground_truth = []

    # --------------------------------------------------------
    # 1. SELLER MASTER
    # --------------------------------------------------------

    sellers = []

    for i in range(1, seller_count + 1):
        status = rng.choice(STATUSES)

        sellers.append({
            "seller_id": f"SELL-{i:06d}",
            "seller_name": f"Seller {i:06d}",
            "email": f"seller{i:06d}@example.com",
            "registration_date": iso(
                date(2024, 1, 1) + timedelta(days=rng.randint(0, 900))
            ),
            "seller_status": status,
            "rating": round(rng.uniform(2.5, 5.0), 2),
            "created_at": iso(AS_OF)
        })

    tables["seller"] = sellers
    seller_by_id = {s["seller_id"]: s for s in sellers}

    # --------------------------------------------------------
    # 2. PRODUCT LISTING MASTER
    # --------------------------------------------------------

    listings = []
    listings_by_seller = defaultdict(list)
    listing_counter = defaultdict(int)

    for i in range(1, listing_count + 1):
        seller = rng.choice(sellers)
        sid = seller["seller_id"]

        listing_counter[sid] += 1
        category = rng.choice(CATEGORIES)

        listing = {
            "listing_id": f"LIST-{sid}-{listing_counter[sid]:06d}",
            "seller_id": sid,
            "product_name": f"{category} Product {i:06d}",
            "category": category,
            "price": round(rng.uniform(100, 15000), 2),
            "stock_quantity": rng.randint(0, 500),
            "listing_status": (
                "ACTIVE" if seller["seller_status"] == "ACTIVE"
                else "INACTIVE"
            ),
            "created_at": iso(AS_OF - timedelta(days=rng.randint(1, 500)))
        }

        listings.append(listing)
        listings_by_seller[sid].append(listing)

    tables["product_listing"] = listings

    # --------------------------------------------------------
    # 3. COMMISSION RULES
    # --------------------------------------------------------

    commission_rules = []

    for category in CATEGORIES:
        commission_rules.append({
            "commission_rule_id": f"CR-{category.upper()}",
            "category": category,
            "commission_rate_pct": COMMISSION[category],
            "reserve_rate_pct": RESERVE_RATE,
            "effective_from": "2026-01-01",
            "effective_to": None,
            "is_active": True
        })

    tables["commission_rule"] = commission_rules
    commission_by_category = {
        r["category"]: r for r in commission_rules
    }

    # --------------------------------------------------------
    # 4. ORDERS AND ORDER LINES
    # --------------------------------------------------------

    orders = []
    order_lines = []
    fulfillments = []
    reviews = []

    order_line_counter = 0

    for i in range(1, order_count + 1):
        order_date = date(2026, 1, 1) + timedelta(
            days=rng.randint(0, (AS_OF - date(2026, 1, 1)).days - 10)
        )

        orders.append({
            "order_id": f"ORD-{YEAR}-{i:06d}",
            "customer_id": f"CUST-{rng.randint(1, 50000):06d}",
            "order_date": iso(order_date),
            "order_status": "COMPLETED",
            "currency": "INR"
        })

        # One to four lines per order; each line can belong
        # to a different seller.
        line_count = rng.randint(1, 4)
        order_total = 0.0

        selected_listings = []

        for _ in range(line_count):
            eligible_sellers = [
                s for s in sellers
                if s["seller_status"] == "ACTIVE"
                and listings_by_seller[s["seller_id"]]
            ]

            seller = rng.choice(eligible_sellers)
            listing = rng.choice(listings_by_seller[seller["seller_id"]])

            selected_listings.append((seller, listing))

        for seller, listing in selected_listings:
            order_line_counter += 1
            line_id = f"OL-{order_line_counter:09d}"

            quantity = rng.randint(1, 3)
            unit_price = listing["price"]
            line_total = round(quantity * unit_price, 2)
            order_total += line_total

            order_lines.append({
                "order_line_id": line_id,
                "order_id": f"ORD-{YEAR}-{i:06d}",
                "listing_id": listing["listing_id"],
                "seller_id": seller["seller_id"],
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": line_total
            })

            # Shipment and delivery dates.
            ship_delay = rng.randint(1, 8)
            ship_date = order_date + timedelta(days=ship_delay)
            delivery_date = ship_date + timedelta(days=rng.randint(1, 6))

            fulfillment_status = (
                "DELIVERED" if delivery_date <= AS_OF else "IN_TRANSIT"
            )

            if ship_delay > 3:
                sla_status = "LATE"
            else:
                sla_status = "ON_TIME"

            fulfillment = {
                "fulfillment_id": f"FUL-{line_id}",
                "order_line_id": line_id,
                "seller_id": seller["seller_id"],
                "shipment_date": iso(ship_date),
                "delivery_date": (
                    iso(delivery_date)
                    if fulfillment_status == "DELIVERED" else None
                ),
                "fulfillment_status": fulfillment_status,
                "sla_status": sla_status,
                "tracking_number": f"TRK-{line_id}"
            }

            fulfillments.append(fulfillment)

            events.append({
                "event_id": f"EVT-{len(events) + 1:09d}",
                "entity_type": "Fulfillment",
                "entity_id": fulfillment["fulfillment_id"],
                "event_type": "SHIPPED",
                "event_date": iso(ship_date),
                "description": "Order line shipped"
            })

            if fulfillment_status == "DELIVERED":
                events.append({
                    "event_id": f"EVT-{len(events) + 1:09d}",
                    "entity_type": "Fulfillment",
                    "entity_id": fulfillment["fulfillment_id"],
                    "event_type": "DELIVERED",
                    "event_date": iso(delivery_date),
                    "description": "Order line delivered"
                })

                if rng.random() < 0.30:
                    reviews.append({
                        "review_id": f"REV-{len(reviews) + 1:09d}",
                        "order_line_id": line_id,
                        "seller_id": seller["seller_id"],
                        "rating": rng.randint(1, 5),
                        "review_date": iso(
                            delivery_date + timedelta(days=rng.randint(1, 5))
                        ),
                        "review_text": "Synthetic customer review"
                    })

        # Store order total after all lines have been created.
        orders[-1]["order_total"] = round(order_total, 2)

    tables["order"] = orders
    tables["order_line"] = order_lines
    tables["fulfillment"] = fulfillments
    tables["customer_review"] = reviews

    # --------------------------------------------------------
    # 5. DISPUTES
    # --------------------------------------------------------

    disputes = []
    line_by_id = {x["order_line_id"]: x for x in order_lines}

    dispute_lines = rng.sample(
        order_lines,
        min(dispute_count, len(order_lines))
    )

    for i, line in enumerate(dispute_lines, 1):
        status = rng.choice(["OPEN", "WON", "LOST"])
        dispute_amount = round(
            line["line_total"] * rng.uniform(0.2, 1.0), 2
        )

        dispute = {
            "dispute_id": f"DSP-{YEAR}-{i:06d}",
            "order_line_id": line["order_line_id"],
            "seller_id": line["seller_id"],
            "dispute_amount": dispute_amount,
            "dispute_status": status,
            "reason": rng.choice([
                "ITEM_NOT_RECEIVED",
                "ITEM_NOT_AS_DESCRIBED",
                "DUPLICATE_CHARGE",
                "REFUND_REQUEST"
            ]),
            "created_date": "2026-10-01",
            "resolved_date": (
                "2026-10-20" if status != "OPEN" else None
            )
        }

        disputes.append(dispute)

        events.append({
            "event_id": f"EVT-{len(events) + 1:09d}",
            "entity_type": "Dispute",
            "entity_id": dispute["dispute_id"],
            "event_type": "DISPUTE_" + status,
            "event_date": dispute["created_date"],
            "description": "Dispute status recorded"
        })

    tables["dispute"] = disputes

    # --------------------------------------------------------
    # 6. PAYOUTS AND PAYOUT LINES
    # --------------------------------------------------------

    disputes_by_line = defaultdict(list)

    for dispute in disputes:
        disputes_by_line[dispute["order_line_id"]].append(dispute)

    fulfillment_by_line = {
        f["order_line_id"]: f for f in fulfillments
    }

    payouts = []
    payout_lines = []
    payout_counter = 0

    for seller in sellers:
        sid = seller["seller_id"]

        if seller["seller_status"] != "ACTIVE":
            continue

        seller_lines = []

        for line in order_lines:
            if line["seller_id"] != sid:
                continue

            fulfillment = fulfillment_by_line[line["order_line_id"]]

            if fulfillment["fulfillment_status"] != "DELIVERED":
                continue

            delivery_date = date.fromisoformat(
                fulfillment["delivery_date"]
            )

            if delivery_date + timedelta(days=HOLD_DAYS) > AS_OF:
                continue

            listing = next(
                x for x in listings
                if x["listing_id"] == line["listing_id"]
            )

            rule = commission_by_category[listing["category"]]

            gross = line["line_total"]
            commission = round(
                gross * rule["commission_rate_pct"] / 100, 2
            )
            reserve = round(
                gross * rule["reserve_rate_pct"] / 100, 2
            )

            dispute_deduction = 0.0
            dispute_hold = 0.0

            for dispute in disputes_by_line[line["order_line_id"]]:
                if dispute["dispute_status"] == "LOST":
                    dispute_deduction += dispute["dispute_amount"]
                elif dispute["dispute_status"] == "OPEN":
                    dispute_hold += dispute["dispute_amount"]

            net = round(
                gross - commission - reserve
                - dispute_deduction - dispute_hold, 2
            )

            seller_lines.append({
                "payout_line_id": f"PL-{len(payout_lines) + len(seller_lines) + 1:09d}",
                "order_line_id": line["order_line_id"],
                "seller_id": sid,
                "gross_amount": gross,
                "commission_amount": commission,
                "reserve_amount": reserve,
                "dispute_deduction": round(dispute_deduction, 2),
                "dispute_hold": round(dispute_hold, 2),
                "net_amount": max(0.0, net),
                "eligibility_status": "ELIGIBLE"
            })

        if seller_lines:
            payout_counter += 1
            payout_id = f"PAYOUT-{YEAR}-{payout_counter:06d}"

            for payout_line in seller_lines:
                payout_line["payout_id"] = payout_id
                payout_lines.append(payout_line)

            payout_total = round(
                sum(x["net_amount"] for x in seller_lines), 2
            )

            payouts.append({
                "payout_id": payout_id,
                "seller_id": sid,
                "payout_date": iso(AS_OF),
                "payout_status": "READY",
                "total_amount": payout_total,
                "currency": "INR"
            })

    tables["payout"] = payouts
    tables["payout_line"] = payout_lines
    tables["event_history"] = events

    # --------------------------------------------------------
    # 7. SELLER METRICS
    # --------------------------------------------------------

    seller_metrics = []

    for seller in sellers:
        sid = seller["seller_id"]

        seller_fulfillments = [
            f for f in fulfillments if f["seller_id"] == sid
        ]

        delivered = [
            f for f in seller_fulfillments
            if f["fulfillment_status"] == "DELIVERED"
        ]

        on_time = [
            f for f in delivered if f["sla_status"] == "ON_TIME"
        ]

        seller_metrics.append({
            "seller_id": sid,
            "total_fulfillments": len(seller_fulfillments),
            "delivered_count": len(delivered),
            "late_count": sum(
                1 for f in seller_fulfillments
                if f["sla_status"] == "LATE"
            ),
            "on_time_rate_pct": round(
                100 * len(on_time) / len(delivered), 2
            ) if delivered else 0.0,
            "dispute_count": sum(
                1 for d in disputes if d["seller_id"] == sid
            ),
            "payout_total": round(
                sum(p["total_amount"] for p in payouts if p["seller_id"] == sid),
                2
            )
        })

    tables["seller_metrics"] = seller_metrics

    # --------------------------------------------------------
    # 8. LABELLED EXCEPTION CASES
    # Baseline records remain valid. These are separate test cases.
    # --------------------------------------------------------

    exception_cases = [
        {
            "case_id": "EX-001",
            "issue_type": "PAYOUT_BEFORE_DELIVERY_OR_HOLD_RELEASE",
            "ground_truth": "REJECT_PAYOUT",
            "expected_decision": "Do not pay before delivery and 7-day hold release",
            "affected_entity": "Fulfillment/PayoutLine"
        },
        {
            "case_id": "EX-002",
            "issue_type": "COMMISSION_APPLIED_TWICE",
            "ground_truth": "FLAG_DUPLICATE_COMMISSION",
            "expected_decision": "Apply commission only once per order line",
            "affected_entity": "PayoutLine"
        },
        {
            "case_id": "EX-003",
            "issue_type": "SUSPENDED_SELLER_CONTINUES_LISTING",
            "ground_truth": "BLOCK_LISTING",
            "expected_decision": "Suspended sellers must not publish active listings",
            "affected_entity": "Seller/ProductListing"
        },
        {
            "case_id": "EX-004",
            "issue_type": "DISPUTE_NOT_DEDUCTED",
            "ground_truth": "FLAG_MISSING_DEDUCTION",
            "expected_decision": "Deduct resolved lost disputes and hold open disputes",
            "affected_entity": "Dispute/PayoutLine"
        },
        {
            "case_id": "EX-005",
            "issue_type": "PAYOUT_TOTAL_NOT_EQUAL_TO_LINES",
            "ground_truth": "FLAG_RECONCILIATION_MISMATCH",
            "expected_decision": "Payout total must equal the sum of payout lines",
            "affected_entity": "Payout/PayoutLine"
        }
    ]

    tables["exception_cases"] = exception_cases

    ground_truth = [
        {
            "case_id": x["case_id"],
            "issue_type": x["issue_type"],
            "ground_truth": x["ground_truth"],
            "expected_decision": x["expected_decision"]
        }
        for x in exception_cases
    ]

    # --------------------------------------------------------
    # 9. VALIDATION
    # --------------------------------------------------------

    errors = []

    def check_unique(rows, key, table_name):
        values = [r[key] for r in rows]
        if len(values) != len(set(values)):
            errors.append(f"{table_name}: duplicate {key}")

    check_unique(sellers, "seller_id", "seller")
    check_unique(listings, "listing_id", "product_listing")
    check_unique(orders, "order_id", "order")
    check_unique(order_lines, "order_line_id", "order_line")
    check_unique(fulfillments, "fulfillment_id", "fulfillment")
    check_unique(disputes, "dispute_id", "dispute")
    check_unique(payouts, "payout_id", "payout")
    check_unique(payout_lines, "payout_line_id", "payout_line")

    seller_ids = set(seller_by_id)
    listing_ids = {x["listing_id"] for x in listings}
    order_ids = {x["order_id"] for x in orders}
    line_ids = {x["order_line_id"] for x in order_lines}

    for x in listings:
        if x["seller_id"] not in seller_ids:
            errors.append("Invalid seller FK in product_listing")

    for x in order_lines:
        if x["listing_id"] not in listing_ids:
            errors.append("Invalid listing FK in order_line")
        if x["seller_id"] not in seller_ids:
            errors.append("Invalid seller FK in order_line")
        if x["order_id"] not in order_ids:
            errors.append("Invalid order FK in order_line")
        if round(x["quantity"] * x["unit_price"], 2) != x["line_total"]:
            errors.append("Order line arithmetic mismatch")

    for x in fulfillments:
        if x["order_line_id"] not in line_ids:
            errors.append("Invalid order_line FK in fulfillment")

    for x in disputes:
        if x["order_line_id"] not in line_ids:
            errors.append("Invalid order_line FK in dispute")

    payout_line_totals = defaultdict(float)

    for x in payout_lines:
        payout_line_totals[x["payout_id"]] += x["net_amount"]

    for payout in payouts:
        if round(payout_line_totals[payout["payout_id"]], 2) != payout["total_amount"]:
            errors.append("Payout reconciliation mismatch")

    for f in fulfillments:
        if f["delivery_date"] and f["shipment_date"] > f["delivery_date"]:
            errors.append("Delivery date before shipment date")

    # --------------------------------------------------------
    # 10. EXPORT CSV AND JSON
    # --------------------------------------------------------

    for table_name, rows in tables.items():
        write_csv(raw_dir / f"{table_name}.csv", rows)
        write_json(processed_dir / f"{table_name}.json", rows)

    write_csv(truth_dir / "ground_truth.csv", ground_truth)
    write_json(truth_dir / "ground_truth.json", ground_truth)

    # --------------------------------------------------------
    # 11. SQLITE DATABASE AND SQL EXPORT
    # --------------------------------------------------------

    db_path = sql_dir / "seller_operations.db"

    if db_path.exists():
        db_path.unlink()

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    for table_name, rows in tables.items():
        if not rows:
            continue

        columns = list(rows[0].keys())

        sql_columns = ", ".join(
            '"' + c + '"' + " TEXT"
            for c in columns
        )

        cursor.execute(
            f'CREATE TABLE "{table_name}" ({sql_columns})'
        )

        placeholders = ", ".join(["?"] * len(columns))

        insert_sql = (
            f'INSERT INTO "{table_name}" '
            f'({", ".join(chr(34) + c + chr(34) for c in columns)}) '
            f'VALUES ({placeholders})'
        )

        values = [
            tuple(
                json.dumps(row[c]) if isinstance(row[c], (dict, list))
                else str(row[c]) if row[c] is not None
                else None
                for c in columns
            )
            for row in rows
        ]

        cursor.executemany(insert_sql, values)

    connection.commit()

    sql_dump = "\n".join(connection.iterdump())
    (sql_dir / "seller_operations.sql").write_text(
        sql_dump, encoding="utf-8"
    )

    connection.close()

    # --------------------------------------------------------
    # 12. VALIDATION SUMMARY
    # --------------------------------------------------------

    row_counts = {
        name: len(rows) for name, rows in tables.items()
    }

    validation_summary = {
        "validation": "PASS" if not errors else "FAIL",
        "errors": errors,
        "seed": SEED,
        "scale": scale,
        "as_of_date": iso(AS_OF),
        "target_volume": {
            "sellers": seller_count,
            "listings": listing_count,
            "orders": order_count,
            "disputes": dispute_count
        },
        "row_counts": row_counts
    }

    (out / "validation_summary.json").write_text(
        json.dumps(validation_summary, indent=2),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # 13. README
    # --------------------------------------------------------

    readme = f"""# Seller Operations Payout Monitoring

## Overview
Synthetic seller operations and payout monitoring dataset.

## Data provenance
All records are synthetic. No customer personal information or
external dataset is used.

## Reproducibility
Fixed random seed: {SEED}

## Generator commands
Starter dataset:
python src/generate_data.py --scale 0.01

Full dataset:
python src/generate_data.py --scale 1.0

## Business rules
- Sellers with non-active status cannot publish active listings.
- Orders may contain lines from multiple sellers.
- Each order line has its own fulfillment record.
- Late shipment is identified when shipment delay exceeds 3 days.
- Payout eligibility requires delivery and a 7-day hold period.
- Commission and reserve are calculated from the applicable category rule.
- Lost disputes are deducted; open disputes are held.
- Payout totals must reconcile with payout lines.

## Output folders
- data/raw: CSV files
- data/processed: JSON files
- data/ground_truth: labelled exception cases
- data/sql: SQL dump and SQLite database

## Validation
See data/validation_summary.json.
"""

    (out / "README_generated.md").write_text(
        readme, encoding="utf-8"
    )

    # --------------------------------------------------------
    # 14. SOURCE MANIFEST AND CHECKSUMS
    # --------------------------------------------------------

    manifest_files = {}

    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "source_manifest.json":
            manifest_files[str(path.relative_to(out))] = sha256(path)

    manifest = {
        "dataset": "Seller Operations Payout Monitoring",
        "data_provenance": "Fully synthetic; no external dataset used",
        "seed": SEED,
        "scale": scale,
        "as_of_date": iso(AS_OF),
        "files": manifest_files
    }

    (out / "source_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8"
    )

    print("\n========== GENERATION COMPLETE ==========")
    print("Validation:", validation_summary["validation"])
    print("Seed:", SEED)
    print("Scale:", scale)
    print("\nRow counts:")

    for name, count in row_counts.items():
        print(f"{name}: {count:,}")

    if errors:
        print("\nVALIDATION ERRORS:")
        for error in errors:
            print("-", error)

    print("\nOutput folder:", out)

    if errors:
        raise SystemExit("Validation failed. Review validation_summary.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Seller Operations Payout Monitoring data"
    )

    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Use 0.01 for starter data or 1.0 for full target volume"
    )

    args = parser.parse_args()

    if args.scale <= 0 or args.scale > 1:
        raise ValueError("Scale must be greater than 0 and at most 1")

    generate(args.scale)
