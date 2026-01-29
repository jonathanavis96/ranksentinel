#!/usr/bin/env python3
"""Test script to generate and display a sample weekly report.

Usage:
    PYTHONPATH=src python3 scripts/test_weekly_report.py [--save-html OUTPUT_FILE]
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ranksentinel.config import Settings
from ranksentinel.db import connect, fetch_all, fetch_one, init_db
from ranksentinel.reporting.report_composer import compose_weekly_report


def main():
    parser = argparse.ArgumentParser(description="Generate sample weekly report")
    parser.add_argument("--save-html", help="Save HTML report to file")
    parser.add_argument("--customer-id", type=int, default=1, help="Customer ID to generate report for")
    args = parser.parse_args()
    
    # Connect to database
    settings = Settings()
    conn = connect(settings)
    init_db(conn)
    
    try:
        # Get customer name
        customer = fetch_one(conn, "SELECT name FROM customers WHERE id=?", (args.customer_id,))
        if not customer:
            print(f"Error: Customer {args.customer_id} not found")
            return 1
        
        customer_name = customer["name"]
        
        # Fetch weekly findings for this customer
        findings = fetch_all(
            conn,
            "SELECT id, customer_id, severity, category, title, details_md, url, created_at "
            "FROM findings "
            "WHERE customer_id=? AND run_type='weekly' "
            "ORDER BY created_at DESC",
            (args.customer_id,)
        )
        
        if not findings:
            print(f"No weekly findings found for customer {args.customer_id} ({customer_name})")
            print("\nTo test with sample data, insert some findings into the database.")
            return 0
        
        # Compose the report
        report = compose_weekly_report(customer_name, findings)
        
        print("=" * 80)
        print(f"Weekly Report for {customer_name}")
        print("=" * 80)
        print(f"Critical: {report.critical_count}")
        print(f"Warnings: {report.warning_count}")
        print(f"Info: {report.info_count}")
        print(f"Total: {report.total_count}")
        print("=" * 80)
        print()
        
        # Print text version
        print(report.to_text())
        print()
        
        # Save HTML if requested
        if args.save_html:
            html_content = report.to_html()
            output_path = Path(args.save_html)
            output_path.write_text(html_content)
            print(f"\n✓ HTML report saved to: {output_path}")
            print(f"  Open with: open {output_path}")
        
        return 0
        
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
