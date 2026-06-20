import os
import matplotlib.pyplot as plt

def create_dashboard(marketing_summary):

    os.makedirs("dashboard", exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(
        marketing_summary["date"],
        marketing_summary["total_sales"],
        marker="o"
    )

    plt.title("FinMark Sales Trend")
    plt.xlabel("Date")
    plt.ylabel("Total Sales")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig("dashboard/finmark_sales_trend.png")
    plt.show()

    print("Dashboard generated successfully.")