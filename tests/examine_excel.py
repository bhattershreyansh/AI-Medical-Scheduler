#!/usr/bin/env python3
"""
Script to examine the Excel file content and identify the data mapping issue
"""

import pandas as pd
import os

def examine_excel_files():
    """Examine the Excel files to understand the data structure"""
    
    print("🔍 Examining Excel Files...\n")
    
    # Check appointments.xlsx
    appointments_file = "data/appointments.xlsx"
    if os.path.exists(appointments_file):
        print(f"📊 Examining {appointments_file}")
        try:
            df = pd.read_excel(appointments_file)
            print(f"Rows: {len(df)}")
            print(f"Columns: {list(df.columns)}")
            print("\nFirst row data:")
            if len(df) > 0:
                for col in df.columns:
                    value = df.iloc[0][col]
                    print(f"  {col}: {value} (type: {type(value)})")
            
            print("\nLast row data:")
            if len(df) > 1:
                for col in df.columns:
                    value = df.iloc[-1][col]
                    print(f"  {col}: {value} (type: {type(value)})")
                    
        except Exception as e:
            print(f"Error reading {appointments_file}: {e}")
    else:
        print(f"❌ {appointments_file} does not exist")
    
    # Check admin_review_report.xlsx
    admin_file = "data/admin_review_report.xlsx"
    if os.path.exists(admin_file):
        print(f"\n📊 Examining {admin_file}")
        try:
            df = pd.read_excel(admin_file)
            print(f"Rows: {len(df)}")
            print(f"Columns: {list(df.columns)}")
            print("\nSample data:")
            print(df.head())
        except Exception as e:
            print(f"Error reading {admin_file}: {e}")
    else:
        print(f"❌ {admin_file} does not exist")

if __name__ == "__main__":
    examine_excel_files()