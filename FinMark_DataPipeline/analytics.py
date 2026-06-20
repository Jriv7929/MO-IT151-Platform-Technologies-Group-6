def generate_kpis(event_logs, marketing_summary, trend_report):

    total_events = len(event_logs)
    total_users = event_logs["user_id"].nunique()
    total_sales = marketing_summary["total_sales"].sum()
    avg_active_users = marketing_summary["users_active"].mean()
    avg_sales_growth = trend_report["sales_growth_rate"].mean()

    print("\nFINMARK KPI SUMMARY")
    print("-------------------")
    print("Total Events:", total_events)
    print("Unique Users:", total_users)
    print("Total Sales:", round(total_sales, 2))
    print("Average Active Users:", round(avg_active_users, 2))
    print("Average Sales Growth Rate:", round(avg_sales_growth, 2))

    return {
        "total_events": total_events,
        "unique_users": total_users,
        "total_sales": total_sales,
        "avg_active_users": avg_active_users,
        "avg_sales_growth": avg_sales_growth
    }