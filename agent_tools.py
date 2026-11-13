# agent_tools.py - functions the AI agent can call; each one reads the processed CSVs
import pandas as pd
from pathlib import Path

# Folder holding the processed data files
DATA = Path(__file__).parent / "data" / "processed"

# Load the data once when the file is imported
segments = pd.read_csv(DATA / "client_segments.csv")
summary = pd.read_csv(DATA / "segment_summary.csv")

# Load the property listings (add next to the other read_csv lines)
props = pd.read_csv(DATA / "props_clean.csv")

from typing import Optional   # add this once at the top of agent_tools.py

def get_segment_summary():
    """Return size, revenue share and profile of every segment."""
    return summary.to_dict(orient="records")


def lookup_client(client_ref: str) -> dict:
    """Return the segment and purchase stats for one client."""
    row = segments[segments["client_ref"] == client_ref]
    if row.empty:
        return {"error": f"client_ref {client_ref} not found"}
    return row.iloc[0].to_dict()

def compare_segments(a: str, b: str) -> dict:
    """Return the summary rows of two segments side by side."""
    # Find the summary row for each segment name
    row_a = summary[summary["segment"] == a]
    row_b = summary[summary["segment"] == b]
    # Return an error if either name is not found
    if row_a.empty or row_b.empty:
        return {"error": f"segment not found: '{a}' or '{b}'"}
    # Return both rows as dicts, keyed by segment name
    return {a: row_a.iloc[0].to_dict(), b: row_b.iloc[0].to_dict()}

def top_clients(segment: str, n: int = 5) -> list:
    """Return the n biggest-spending clients in a segment."""
    # Keep only clients of the requested segment
    seg = segments[segments["segment"] == segment].copy()
    if seg.empty:
        return {"error": f"segment not found: '{segment}'"}
    # Total spend = purchases x average price
    seg["total_spend"] = seg["n_purchase"] * seg["avg_price"]
    top = seg.sort_values("total_spend", ascending=False).head(n)
    return top[["client_ref", "n_purchase", "total_spend"]].to_dict(orient="records")

def property_stats(status: str = "Sold", tower_number: Optional[int] = None, unit_category: Optional[str] = None) -> dict:
    """Return count, average price and average price per sqft for listings."""
    # Filter by listing status, then by tower and unit type if given
    df = props[props["listing_status"] == status]
    if tower_number is not None:
        df = df[df["tower_number"] == tower_number]
    if unit_category is not None:
        df = df[df["unit_category"] == unit_category]
    if df.empty:
        return {"error": "no listings match these filters"}
    return {
        "listings": len(df),
        "avg_price": float(round(df["sale_price"].mean(), 2)),
        "avg_price_per_sqft": float(round((df["sale_price"] / df["floor_area_sqft"]).mean(), 2)),
    }
# Quick test, runs only when you execute this file directly
if __name__ == "__main__":
    print(get_segment_summary())
    print(lookup_client(segments["client_ref"].iloc[0]))
    print(compare_segments("Budget Buyers", "Portfolio Investors"))
    print(compare_segments("Budget Buyers", "Nonsense"))
    print(top_clients("Portfolio Investors", 3))
    print(property_stats())
    print(property_stats(unit_category="Office"))