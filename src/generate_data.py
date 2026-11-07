#!/usr/bin/env python3
"""Deterministic synthetic Seller Operations / Payout Monitoring data generator."""
from __future__ import annotations
import argparse, csv, hashlib, json, random, sqlite3
from collections import defaultdict, Counter
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

SEED = 20261022
AS_OF = date(2026, 11, 7)
CATEGORIES = ["Electronics", "Home", "Fashion", "Books", "Beauty"]
STATUSES = ["ACTIVE", "SUSPENDED", "UNDER_REVIEW"]
D = Decimal

def money(x): return str(D(str(x)).quantize(D("0.01"), rounding=ROUND_HALF_UP))
def iso(d): return d.isoformat()
def make_id(prefix, n, width=6): return f"{prefix}{n:0{width}d}"
def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8"); return
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def generate(scale: float, out: Path):
    rng=random.Random(SEED)
    n_sellers=max(1, round(2000*scale)); n_listings=max(1, round(20000*scale))
    n_orders=max(1, round(100000*scale)); n_disputes=max(1, round(10000*scale))
    # 1. Parent/master records
    sellers=[]
    for i in range(1,n_sellers+1):
        status="SUSPENDED" if i%37==0 else ("UNDER_REVIEW" if i%29==0 else "ACTIVE")
        sellers.append({"seller_id":make_id("SELL-",i),"seller_name":f"Seller {i:06d}","seller_status":status,
                        "country":"IN","created_date":iso(date(2024,1,1)+timedelta(days=rng.randrange(900))),
                        "service_level_target_pct":"95.00"})
    seller_status_by_id={s["seller_id"]:s["seller_status"] for s in sellers}
    active_ids=[s["seller_id"] for s in sellers if s["seller_status"]=="ACTIVE"]
    all_ids=[s["seller_id"] for s in sellers]
    listing_counts=Counter(); listings=[]
    for i in range(1,n_listings+1):
        sid=all_ids[(i-1)%len(all_ids)]; listing_counts[sid]+=1
        cat=CATEGORIES[(i-1)%len(CATEGORIES)]
        listings.append({"listing_id":f"LIST-{sid}-{listing_counts[sid]:06d}","seller_id":sid,
                         "product_name":f"{cat} Product {i:06d}","category":cat,
                         "unit_price":money(rng.uniform(100,50000)),"listing_status":"ACTIVE" if next(s for s in sellers if s['seller_id']==sid)['seller_status']=="ACTIVE" else "INACTIVE",
                         "created_date":iso(date(2025,1,1)+timedelta(days=rng.randrange(600)))})
    listing_category_by_id={x["listing_id"]:x["category"] for x in listings}
    active_listings=[x for x in listings if x["listing_status"]=="ACTIVE"]
    listings_by_seller=defaultdict(list)
    for x in active_listings: listings_by_seller[x["seller_id"]].append(x)
    if not active_listings: raise ValueError("No active listings; increase scale.")
    # Effective-dated commission rules
    rules=[]
    for cat in CATEGORIES:
        rules.append({"commission_rule_id":f"CR-{cat.upper()}","category":cat,"commission_rate_pct":str({"Electronics":10,"Home":12,"Fashion":15,"Books":8,"Beauty":13}[cat]),
                      "reserve_rate_pct":"5.00","effective_from":"2025-01-01","effective_to":"2027-12-31","is_active":"true"})
    rule_by_cat={r["category"]:r for r in rules}
    # 2. Transaction records and event history
    orders=[]; order_lines=[]; fulfillments=[]; events=[]; reviews=[]
    lines_by_order=defaultdict(list); line_lookup={}; order_date={}
    start=date(2026,1,1)
    for oi in range(1,n_orders+1):
        oid=make_id("ORD-2026-",oi)
        od=start+timedelta(days=rng.randrange(300)); order_date[oid]=od
        # 1-3 distinct sellers where possible
        seller_pool=active_ids or all_ids
        chosen=rng.sample(seller_pool, k=min(rng.randint(1,3),len(seller_pool)))
        order_total=D("0.00"); order_lines_for_order=[]; order_fulfillment_states=[]
        for j,sid in enumerate(chosen,1):
            pool=listings_by_seller.get(sid)
            if not pool: continue
            listing=rng.choice(pool); qty=rng.randint(1,3); unit=D(listing["unit_price"])
            amount=(unit*qty).quantize(D("0.01")); order_total+=amount
            lid=f"OL-{oi:06d}-{j:02d}"
            line={"order_line_id":lid,"order_id":oid,"listing_id":listing["listing_id"],"seller_id":sid,
                  "quantity":qty,"unit_price":money(unit),"line_total":money(amount)}
            order_lines.append(line); order_lines_for_order.append(line); lines_by_order[oid].append(line); line_lookup[lid]=line
            # delivery timeline, with explicit late shipment and return paths
            ship_delay=rng.randint(1,8); delivery_delay=rng.randint(1,6)
            shipped=od+timedelta(days=ship_delay); delivered=shipped+timedelta(days=delivery_delay)
            returned=(rng.random()<0.025 and delivered<=AS_OF)
            status="CREATED" if shipped>AS_OF else "SHIPPED"
            delivered_value=iso(delivered) if delivered<=AS_OF else ""
            if delivered<=AS_OF: status="RETURNED" if returned else "DELIVERED"
            fid=f"FUL-{lid}"
            order_fulfillment_states.append(status)
            fulfillments.append({"fulfillment_id":fid,"order_line_id":lid,"seller_id":sid,"fulfillment_status":status,
                                 "created_date":iso(od),"shipped_date":iso(shipped) if shipped<=AS_OF else "",
                                 "delivered_date":delivered_value,"is_late":"true" if ship_delay>3 else "false",
                                 "is_returned":"true" if returned else "false"})
            events.append({"event_id":f"EV-{len(events)+1:09d}","entity_type":"Fulfillment","entity_id":fid,"event_type":"CREATED","event_date":iso(od),"from_state":"","to_state":"CREATED"})
            if shipped<=AS_OF: events.append({"event_id":f"EV-{len(events)+1:09d}","entity_type":"Fulfillment","entity_id":fid,"event_type":"SHIPPED","event_date":iso(shipped),"from_state":"CREATED","to_state":"SHIPPED"})
            if delivered<=AS_OF: events.append({"event_id":f"EV-{len(events)+1:09d}","entity_type":"Fulfillment","entity_id":fid,"event_type":"DELIVERED","event_date":iso(delivered),"from_state":"SHIPPED","to_state":"DELIVERED"})
            if returned: events.append({"event_id":f"EV-{len(events)+1:09d}","entity_type":"Fulfillment","entity_id":fid,"event_type":"RETURNED","event_date":iso(delivered+timedelta(days=2)),"from_state":"DELIVERED","to_state":"RETURNED"})
            if delivered<=AS_OF and not returned and rng.random()<0.30:
                reviews.append({"review_id":f"REV-{len(reviews)+1:08d}","order_line_id":lid,"seller_id":sid,
                                "rating":rng.randint(1,5),"review_date":iso(delivered+timedelta(days=rng.randint(1,10))),"review_text":"Synthetic customer review"})
        orders.append({"order_id":oid,"customer_id":f"CUST-{rng.randint(1,max(10,n_orders)):06d}","order_date":iso(od),
                       "order_status":"CANCELLED" if not order_lines_for_order else ("FULFILLED" if all(st in ("DELIVERED", "RETURNED") for st in order_fulfillment_states) else "IN_PROGRESS"),
                       "order_total":money(order_total),"currency":"INR"})
    # Disputes attached to valid order lines; no independent random foreign keys
    disputes=[]
    delivered_line_ids=[f["order_line_id"] for f in fulfillments if f["delivered_date"]]
    for i in range(1,n_disputes+1):
        if not delivered_line_ids: break
        lid=delivered_line_ids[(i-1)%len(delivered_line_ids)]; line=line_lookup[lid]
        delivered_on=date.fromisoformat(next(f["delivered_date"] for f in fulfillments if f["order_line_id"]==lid))
        created=delivered_on+timedelta(days=rng.randint(1,45))
        dispute_status=rng.choice(["OPEN","WON","LOST"])
        disputes.append({"dispute_id":make_id("DSP-2026-",i),"order_line_id":lid,"seller_id":line["seller_id"],
                         "dispute_type":rng.choice(["CHARGEBACK","ITEM_NOT_RECEIVED","NOT_AS_DESCRIBED"]),
                         "dispute_status":dispute_status,"dispute_amount":line["line_total"],
                         "created_date":iso(created),"resolved_date":iso(created+timedelta(days=14)) if dispute_status!="OPEN" else ""})
    disputed_lines={d["order_line_id"] for d in disputes if d["dispute_status"] in ("OPEN","LOST")}
    # 3. Payouts: only delivered, past hold, not returned, not held by open/lost dispute
    payout_by_seller=defaultdict(list); fulfillment_by_line={f["order_line_id"]:f for f in fulfillments}
    for line in order_lines:
        f=fulfillment_by_line[line["order_line_id"]]
        if f["fulfillment_status"]!="DELIVERED" or not f["delivered_date"] or line["order_line_id"] in disputed_lines: continue
        delivered=date.fromisoformat(f["delivered_date"])
        if delivered+timedelta(days=7)>AS_OF: continue
        rule=rule_by_cat[listing_category_by_id[line["listing_id"]]]
        gross=D(line["line_total"]); commission=(gross*D(rule["commission_rate_pct"])/D(100)).quantize(D("0.01"))
        reserve=(gross*D(rule["reserve_rate_pct"])/D(100)).quantize(D("0.01"))
        net=gross-commission-reserve
        payout_by_seller[line["seller_id"]].append({"order_line_id":line["order_line_id"],"gross_amount":money(gross),"commission_amount":money(commission),"reserve_amount":money(reserve),"refund_amount":"0.00","net_amount":money(net)})
    payouts=[]; payout_lines=[]
    for idx,(sid,items) in enumerate(sorted(payout_by_seller.items()),1):
        pid=make_id("PAYOUT-",idx)
        total=sum((D(x["net_amount"]) for x in items),D("0.00"))
        payouts.append({"payout_id":pid,"seller_id":sid,"payout_date":iso(AS_OF),"payout_status":"ELIGIBLE","payout_total":money(total),"currency":"INR"})
        for j,x in enumerate(items,1):
            payout_lines.append({"payout_line_id":f"{pid}-LINE-{j:06d}","payout_id":pid,"order_line_id":x["order_line_id"],**x})
    # Derived seller service metrics (computed from fulfillment and review source rows)
    seller_metrics=[]
    review_scores=defaultdict(list)
    for review in reviews: review_scores[review["seller_id"]].append(int(review["rating"]))
    for seller in sellers:
        sid=seller["seller_id"]
        sf=[f for f in fulfillments if f["seller_id"]==sid and f["delivered_date"]]
        delivered_count=len(sf); late_count=sum(1 for f in sf if f["is_late"]=="true")
        avg_rating=(sum(review_scores[sid])/len(review_scores[sid])) if review_scores[sid] else 0
        seller_metrics.append({"seller_id":sid,"delivered_fulfillment_count":delivered_count,"late_fulfillment_count":late_count,
            "on_time_rate_pct":money((delivered_count-late_count)*100/delivered_count) if delivered_count else "0.00",
            "average_review_rating":money(avg_rating),"seller_status":seller["seller_status"],
            "meets_service_target":"true" if delivered_count and (delivered_count-late_count)*100/delivered_count>=95 else "false"})
    # 4. Deliberate exception cases kept OUTSIDE baseline input tables
    exception_cases=[
      {"case_id":"EX-001","issue_type":"PAYOUT_BEFORE_DELIVERY_OR_HOLD_RELEASE","ground_truth":"REJECT_PAYOUT","expected_decision":"Do not pay until delivered and 7-day hold has elapsed","affected_entity":"Fulfillment/PayoutLine","affected_record_id":"SYNTHETIC_FIXTURE"},
      {"case_id":"EX-002","issue_type":"COMMISSION_APPLIED_TWICE","ground_truth":"FLAG_DUPLICATE_COMMISSION","expected_decision":"Apply one effective commission rule once per order line","affected_entity":"PayoutLine","affected_record_id":"SYNTHETIC_FIXTURE"},
      {"case_id":"EX-003","issue_type":"SUSPENDED_SELLER_CONTINUES_LISTING","ground_truth":"SUSPEND_LISTING","expected_decision":"Suspended seller must not have an active listing","affected_entity":"Seller/ProductListing","affected_record_id":next((s['seller_id'] for s in sellers if s['seller_status']=='SUSPENDED'),"NONE")},
      {"case_id":"EX-004","issue_type":"DISPUTE_NOT_DEDUCTED","ground_truth":"HOLD_OR_DEDUCT_DISPUTE","expected_decision":"Open/lost disputes must be held or deducted according to policy","affected_entity":"Dispute/PayoutLine","affected_record_id":"SYNTHETIC_FIXTURE"},
      {"case_id":"EX-005","issue_type":"PAYOUT_TOTAL_NOT_EQUAL_TO_LINES","ground_truth":"RECONCILE_PAYOUT","expected_decision":"Payout header must equal sum of its payout lines","affected_entity":"Payout","affected_record_id":"SYNTHETIC_FIXTURE"},
    ]
    # 5. Validation of generated baseline
    errors=[]
    def unique(rows,key,label):
        vals=[r[key] for r in rows]
        if len(vals)!=len(set(vals)): errors.append(f"{label}: duplicate {key}")
    for rows,key,label in [(sellers,'seller_id','Seller'),(listings,'listing_id','ProductListing'),(orders,'order_id','Order'),(order_lines,'order_line_id','OrderLine'),(fulfillments,'fulfillment_id','Fulfillment'),(disputes,'dispute_id','Dispute'),(payouts,'payout_id','Payout'),(payout_lines,'payout_line_id','PayoutLine')]: unique(rows,key,label)
    seller_set=set(all_ids); listing_set={x['listing_id'] for x in listings}; order_set={x['order_id'] for x in orders}; line_set={x['order_line_id'] for x in order_lines}
    for x in listings:
        if x['seller_id'] not in seller_set: errors.append('Listing seller FK')
        if x['category'] not in CATEGORIES: errors.append('Listing category enum')
    for x in order_lines:
        if x['order_id'] not in order_set or x['listing_id'] not in listing_set or x['seller_id'] not in seller_set: errors.append('OrderLine FK')
        if D(x['line_total']) != D(x['unit_price'])*x['quantity']: errors.append('OrderLine arithmetic')
    for x in fulfillments:
        if x['order_line_id'] not in line_set: errors.append('Fulfillment FK')
        if x['delivered_date'] and x['shipped_date'] and x['delivered_date'] < x['shipped_date']: errors.append('Fulfillment date order')
    for x in disputes:
        if x['order_line_id'] not in line_set or x['seller_id'] not in seller_set: errors.append('Dispute FK')
    payout_totals={p['payout_id']:D(p['payout_total']) for p in payouts}; sums=defaultdict(lambda:D('0.00'))
    for x in payout_lines: sums[x['payout_id']]+=D(x['net_amount'])
    for pid,total in payout_totals.items():
        if total!=sums[pid]: errors.append(f'Payout reconciliation {pid}')
    for x in payout_lines:
        if x['order_line_id'] not in line_set: errors.append('PayoutLine FK')
    if errors: raise RuntimeError('VALIDATION FAILED: '+'; '.join(errors[:20]))
    # 6. Write CSV + JSON
    tables={"seller":sellers,"product_listing":listings,"order":orders,"order_line":order_lines,"fulfillment":fulfillments,
            "customer_review":reviews,"dispute":disputes,"commission_rule":rules,"payout":payouts,"payout_line":payout_lines,
            "event_history":events,"seller_metrics":seller_metrics,"exception_cases":exception_cases}
    for folder in ("raw", "processed", "ground_truth", "sql"): (out/folder).mkdir(parents=True, exist_ok=True)
    for name,rows in tables.items():
        write_rows(out/'raw'/f'{name}.csv',rows)
        (out/'processed'/f'{name}.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    (out/'ground_truth'/'ground_truth.json').write_text(json.dumps(exception_cases,indent=2),encoding='utf-8')
    write_rows(out/'ground_truth'/'ground_truth.csv',exception_cases)
    # SQLite database and SQL dump (all columns stored as TEXT for portable seed export)
    db=out/'sql'/'seller_operations.db'; db.parent.mkdir(parents=True,exist_ok=True)
    if db.exists(): db.unlink()
    con=sqlite3.connect(db)
    for name,rows in tables.items():
        if not rows: continue
        cols=list(rows[0].keys()); colsql=", ".join('"'+c+'" TEXT' for c in cols)
        con.execute(f'CREATE TABLE "{name}" ({colsql})')
        marks=','.join('?' for _ in cols)
        con.executemany(f'INSERT INTO "{name}" VALUES ({marks})',[[str(r.get(c,'')) for c in cols] for r in rows])
    con.commit()
    with (out/'sql'/'seller_operations.sql').open('w',encoding='utf-8') as f:
        for line in con.iterdump(): f.write(line+'\n')
    con.close()
    # README + reproducible manifest (checksums exclude manifest itself)
    readme=("# Seller Operations Payout Monitoring\n\nSynthetic data only; no personal or external data used.\n\n"
            f"Seed: {SEED}\nScale: {scale}\nAs-of date: {AS_OF}\n\n"
            "Run from repository root: `python src/generate_data.py --scale 0.01` (starter) or `python src/generate_data.py` (full).\n\n"
            "Policy assumptions: 7-day post-delivery hold; category commission rates are in commission_rule; 5% reserve; open/lost disputes and returned orders are excluded from eligible payouts. These are synthetic demonstration rules, not universal marketplace policy.\n")
    (out/'README_generated.md').write_text(readme,encoding='utf-8')
    files=sorted(p for p in out.rglob('*') if p.is_file() and p.name!='source_manifest.json')
    manifest={"seed":SEED,"scale":scale,"as_of_date":iso(AS_OF),"provenance":"Synthetic generated data; no external source",
              "row_counts":{k:len(v) for k,v in tables.items()},"validation_status":"PASS","checksums_sha256":{str(p.relative_to(out)):sha256(p) for p in files}}
    (out/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    summary={"validation":"PASS","seed":SEED,"scale":scale,"row_counts":manifest['row_counts'],"output_directory":str(out)}
    (out/'validation_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('VALIDATION: PASS')
    for k,v in manifest['row_counts'].items(): print(f'{k}: {v:,}')
    print(f'Output: {out.resolve()}')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--scale',type=float,default=1.0,help='0 < scale <= 1; default 1.0 creates target volume')
    ap.add_argument('--output',default='data',help='output directory (default: data)')
    args=ap.parse_args()
    if not (0 < args.scale <= 1): ap.error('--scale must be greater than 0 and at most 1')
    generate(args.scale,Path(args.output))
if __name__=='__main__': main()

