#!/usr/bin/env python3
"""
CFTC Commitment of Traders (COT) Weekly Report Generator
Automatically downloads, processes, and emails weekly COT reports for US Crude Oil WTI

Author: bloombodymind
Repository: https://github.com/bloombodymind/cftc-cot-weekly-report
"""

import os
import requests
import pandas as pd
import zipfile
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def get_latest_cot_data():
    """
    Download and process the latest CFTC COT data
    Returns: DataFrame with latest data, report date
    """
    print("Downloading CFTC COT data...")
    url = "https://www.cftc.gov/files/dea/history/fut_fin_txt_2024.zip"
    response = requests.get(url)
    
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        csv_file = z.namelist()[0]
        with z.open(csv_file) as f:
            df = pd.read_csv(f)
    
    # Filter for Crude Oil WTI
    crude_oil = df[df['Market_and_Exchange_Names'].str.contains('CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE', na=False)].copy()
    
    # Get latest report date - FIXED: Use 'Report_Date' instead of 'Report_Date_as_MM_DD_YYYY'
    latest_date = crude_oil['Report_Date'].max()
    latest = crude_oil[crude_oil['Report_Date'] == latest_date].copy()
    
    # Convert to numeric
    numeric_cols = ['Pct_of_OI_Dealer_Long_All', 'Pct_of_OI_Dealer_Short_All', 
                    'Pct_of_OI_Asset_Mgr_Long_All', 'Pct_of_OI_Asset_Mgr_Short_All',
                    'Pct_of_OI_Lev_Money_Long_All', 'Pct_of_OI_Lev_Money_Short_All',
                    'Pct_of_OI_Other_Rept_Long_All', 'Pct_of_OI_Other_Rept_Short_All',
                    'Pct_of_OI_NonRept_Long_All', 'Pct_of_OI_NonRept_Short_All',
                    'Change_in_Dealer_Long_All', 'Change_in_Dealer_Short_All',
                    'Change_in_Asset_Mgr_Long_All', 'Change_in_Asset_Mgr_Short_All',
                    'Change_in_Lev_Money_Long_All', 'Change_in_Lev_Money_Short_All',
                    'Change_in_Other_Rept_Long_All', 'Change_in_Other_Rept_Short_All',
                    'Change_in_NonRept_Long_All', 'Change_in_NonRept_Short_All',
                    'Open_Interest_All']
    
    for col in numeric_cols:
        if col in latest.columns:
            latest[col] = pd.to_numeric(latest[col].astype(str).str.replace(',', ''), errors='coerce')
    
    return latest, latest_date


def generate_report(data, report_date):
    """
    Generate formatted COT report text
    Args:
        data: DataFrame with COT data
        report_date: Date of the report
    Returns: Formatted report string
    """
    # Calculate positions and changes
    oi = data['Open_Interest_All'].values[0]
    
    # Reportable (all categories combined)
    reportable_long = (data['Pct_of_OI_Dealer_Long_All'].values[0] + 
                       data['Pct_of_OI_Asset_Mgr_Long_All'].values[0] + 
                       data['Pct_of_OI_Lev_Money_Long_All'].values[0] + 
                       data['Pct_of_OI_Other_Rept_Long_All'].values[0]) * oi / 100
    
    reportable_short = (data['Pct_of_OI_Dealer_Short_All'].values[0] + 
                        data['Pct_of_OI_Asset_Mgr_Short_All'].values[0] + 
                        data['Pct_of_OI_Lev_Money_Short_All'].values[0] + 
                        data['Pct_of_OI_Other_Rept_Short_All'].values[0]) * oi / 100
    
    reportable_chg_long = (data['Change_in_Dealer_Long_All'].values[0] + 
                           data['Change_in_Asset_Mgr_Long_All'].values[0] + 
                           data['Change_in_Lev_Money_Long_All'].values[0] + 
                           data['Change_in_Other_Rept_Long_All'].values[0])
    
    reportable_chg_short = (data['Change_in_Dealer_Short_All'].values[0] + 
                            data['Change_in_Asset_Mgr_Short_All'].values[0] + 
                            data['Change_in_Lev_Money_Short_All'].values[0] + 
                            data['Change_in_Other_Rept_Short_All'].values[0])
    
    # Non-Commercial (Asset Mgr + Lev Money)
    nc_long = (data['Pct_of_OI_Asset_Mgr_Long_All'].values[0] + data['Pct_of_OI_Lev_Money_Long_All'].values[0]) * oi / 100
    nc_short = (data['Pct_of_OI_Asset_Mgr_Short_All'].values[0] + data['Pct_of_OI_Lev_Money_Short_All'].values[0]) * oi / 100
    nc_chg_long = data['Change_in_Asset_Mgr_Long_All'].values[0] + data['Change_in_Lev_Money_Long_All'].values[0]
    nc_chg_short = data['Change_in_Asset_Mgr_Short_All'].values[0] + data['Change_in_Lev_Money_Short_All'].values[0]
    
    # Commercial (Dealer + Other Rept)
    comm_long = (data['Pct_of_OI_Dealer_Long_All'].values[0] + data['Pct_of_OI_Other_Rept_Long_All'].values[0]) * oi / 100
    comm_short = (data['Pct_of_OI_Dealer_Short_All'].values[0] + data['Pct_of_OI_Other_Rept_Short_All'].values[0]) * oi / 100
    comm_chg_long = data['Change_in_Dealer_Long_All'].values[0] + data['Change_in_Other_Rept_Long_All'].values[0]
    comm_chg_short = data['Change_in_Dealer_Short_All'].values[0] + data['Change_in_Other_Rept_Short_All'].values[0]
    
    # Non-Reportable
    nr_long = data['Pct_of_OI_NonRept_Long_All'].values[0] * oi / 100
    nr_short = data['Pct_of_OI_NonRept_Short_All'].values[0] * oi / 100
    nr_chg_long = data['Change_in_NonRept_Long_All'].values[0]
    nr_chg_short = data['Change_in_NonRept_Short_All'].values[0]
    
    report = f"""
===============================================================================
CFTC COT REPORT - US CRUDE WTI FUTURE
Report Date: {report_date}
Source: New York Mercantile Exchange
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
===============================================================================

===============================================================================
FUTURES OPEN INTEREST
===============================================================================
Category                        Position            Chg
---------------------------------------------------------------------------

▼ Reportable
  Long                          {reportable_long:>15,.0f}     {reportable_chg_long:>12,.0f}
  Short                         {reportable_short:>15,.0f}     {reportable_chg_short:>12,.0f}
  Net                           {reportable_long - reportable_short:>15,.0f}     {reportable_chg_long - reportable_chg_short:>12,.0f}

▼ Non-Commercial
  Long                          {nc_long:>15,.0f}     {nc_chg_long:>12,.0f}
  Short                         {nc_short:>15,.0f}     {nc_chg_short:>12,.0f}
  Net                           {nc_long - nc_short:>15,.0f}     {nc_chg_long - nc_chg_short:>12,.0f}

▼ Commercial
  Long                          {comm_long:>15,.0f}     {comm_chg_long:>12,.0f}
  Short                         {comm_short:>15,.0f}     {comm_chg_short:>12,.0f}
  Net                           {comm_long - comm_short:>15,.0f}     {comm_chg_long - comm_chg_short:>12,.0f}

▼ Non-Reportable
  Long                          {nr_long:>15,.0f}     {nr_chg_long:>12,.0f}
  Short                         {nr_short:>15,.0f}     {nr_chg_short:>12,.0f}
  Net                           {nr_long - nr_short:>15,.0f}     {nr_chg_long - nr_chg_short:>12,.0f}

===============================================================================
✓ COT Report Generated Successfully!
===============================================================================
"""
    return report


def send_email(report_content, report_date):
    """
    Send email with COT report
    Args:
        report_content: Formatted report text
        report_date: Date of the report
    Returns: True if successful, False otherwise
    """
    # Email configuration - using environment variables for security
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    recipient_email = "veluthap@gmail.com"
    
    if not sender_email or not sender_password:
        print("ERROR: Email credentials not set in environment variables!")
        print("Set SENDER_EMAIL and SENDER_PASSWORD environment variables.")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Weekly CFTC COT Report - {report_date}"
    
    msg.attach(MIMEText(report_content, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print(f"✓ Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {str(e)}")
        return False


def main():
    """
    Main execution function
    """
    print("="*80)
    print("CFTC COT Weekly Report Generator")
    print("="*80)
    
    try:
        # Step 1: Get data
        print("\nStep 1: Fetching latest CFTC COT data...")
        data, report_date = get_latest_cot_data()
        print(f"✓ Data retrieved for {report_date}")
        
        # Step 2: Generate report
        print("\nStep 2: Generating report...")
        report = generate_report(data, report_date)
        print("✓ Report generated")
        print("\n" + report)
        
        # Step 3: Send email
        print("\nStep 3: Sending email...")
        success = send_email(report, report_date)
        
        if success:
            print("\n" + "="*80)
            print("✓ WEEKLY COT REPORT COMPLETED SUCCESSFULLY")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("✗ EMAIL SENDING FAILED")
            print("="*80)
            exit(1)
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
