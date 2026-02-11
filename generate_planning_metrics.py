import pandas as pd
import numpy as np

def planning_metrics(df):

    # Inventory Risk
    df["inventory_risk"] = (df["warehouse_inventory_level"] < df["order_quantity"]).map({True: "At Risk", False: "OK"})

    # Supplier Risk
    conditions = [
        df["supplier_reliability_score"] < 0.5,
        (df["supplier_reliability_score"] >= 0.5) & (df["supplier_reliability_score"] < 0.75),
        df["supplier_reliability_score"] >= 0.75
    ]

    choices = ["High Risk", "Medium Risk", "Low Risk"]

    df["supplier_risk"] = np.select(conditions, choices, default="Unknown")

    # Delay flag
    df["delay_flag"] = df["delayed"].map({1: "Delayed", 0: "On Time"})

    # Processing risk
    df["processing_risk"] = np.where(df["processing_time_hours"] > 48,"High","Normal")

    # Distance risk
    df["distance_risk"] = np.where(df["shipping_distance_km"] > 1000,"High","Normal")

    return df

def build_summary_tables(df):
    kpis = pd.DataFrame([{
        "total_orders": len(df),
        "delay_rate_pct": round(df["delayed"].mean() * 100, 2),
        "inventory_risk_pct": round((df["inventory_risk"] == "At Risk").mean() * 100, 2),
        "processing_risk_pct": round((df["processing_risk"] == "High").mean() * 100, 2),
        "distance_risk_pct": round((df["distance_risk"] == "High").mean() * 100, 2),
        "avg_processing_hours": round(df["processing_time_hours"].mean(), 2),
        "avg_shipping_distance_km": round(df["shipping_distance_km"].mean(), 2),
    }])


    # Breakdown tables
    by_priority = (
    (df.groupby("order_priority")["delayed"].mean() * 100).round(2).reset_index().rename(columns={"delayed": "delay_rate_pct"})
    )

    by_supplier_risk = (
    (df.groupby("supplier_risk") ["delayed"].mean() * 100).round(2).reset_index().rename(columns={"delayed": "delay_rate_pct"})
    )

    by_shipping_method = (
    (df.groupby("shipping_method")["delayed"].mean() * 100).round(2).reset_index().rename(columns={"delayed": "delay_rate_pct"})
    )

    return kpis, by_priority, by_supplier_risk, by_shipping_method

def main():
    df = pd.read_csv("supply_chain_order_fulfillment_delay_risk.csv")
    df = planning_metrics(df)

    kpis, by_priority, by_supplier_risk, by_shipping_method = build_summary_tables(df)

    # Export outputs 
    df.to_csv("fact_orders.csv", index=False)
    kpis.to_csv("kpi_summary.csv", index=False)
    by_priority.to_csv("delay_by_priority.csv", index=False)
    by_supplier_risk.to_csv("delay_by_supplier_risk.csv", index=False)
    by_shipping_method.to_csv("delay_by_shipping_method.csv", index=False)

    print("\nExported files:")
    print(" - fact_orders.csv")
    print(" - kpi_summary.csv")
    print(" - delay_by_priority.csv")
    print(" - delay_by_supplier_risk.csv")
    print(" - delay_by_shipping_method.csv")

if __name__ == "__main__":
    main()