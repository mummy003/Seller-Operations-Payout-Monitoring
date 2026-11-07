import pandas as pd

def test_seller():
    df = pd.read_csv("data/raw/seller.csv")
    assert df["seller_id"].is_unique

def test_orders():
    df = pd.read_csv("data/raw/order.csv")
    assert df["order_id"].is_unique

def test_order_lines():
    df = pd.read_csv("data/raw/order_line.csv")
    assert df["order_line_id"].is_unique
    assert (df["line_total"] > 0).all()

def test_payout():
    df = pd.read_csv("data/raw/payout.csv")
    assert (df["total_amount"] >= 0).all()

def test_disputes():
    df = pd.read_csv("data/raw/dispute.csv")
    assert df["dispute_status"].isin(["OPEN", "WON", "LOST"]).all()
