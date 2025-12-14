# CFTC COT Weekly Report Automation

Automated weekly CFTC Commitment of Traders (COT) report for US Crude Oil WTI futures, delivered via email every Friday.

## Features

✅ **Fully Automated** - Runs every Friday at 4:00 PM ET via GitHub Actions  
✅ **CFTC Data Integration** - Downloads latest COT data directly from CFTC  
✅ **Email Delivery** - Formatted report sent to veluthap@gmail.com  
✅ **Secure** - Uses GitHub Secrets for email credentials  
✅ **Manual Trigger** - Test anytime with workflow_dispatch  
✅ **Error Handling** - Comprehensive logging and error reporting  

## What is COT?

The Commitment of Traders (COT) report is a weekly publication by the CFTC showing aggregate positions of different trader categories in futures markets. This script focuses on **US Crude Oil WTI futures** traded on the New York Mercantile Exchange.

### Trader Categories

- **Reportable**: All large traders (Dealer + Asset Mgr + Lev Money + Other Rept)
- **Non-Commercial**: Speculators (Asset Managers + Leveraged Money)
- **Commercial**: Hedgers (Dealers + Other Reportable)
- **Non-Reportable**: Small traders below reporting thresholds

## Setup Instructions

### 1. Fork or Clone Repository

```bash
git clone https://github.com/bloombodymind/cftc-cot-weekly-report.git
cd cftc-cot-weekly-report
```

### 2. Set up Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Search for "App passwords"
4. Generate password for "Mail" / "Other (Custom name)"
5. Copy the 16-character password (remove spaces)

### 3. Configure GitHub Secrets

1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add two secrets:

   **SENDER_EMAIL**
   ```
   your_email@gmail.com
   ```

   **SENDER_PASSWORD**
   ```
   your_16_character_app_password
   ```

### 4. Update Recipient Email (Optional)

If you want to change the recipient email, edit `cftc_cot_report.py`:

```python
recipient_email = "veluthap@gmail.com"  # Change this
```

### 5. Test the Workflow

1. Go to **Actions** tab
2. Click **Weekly CFTC COT Report**
3. Click **Run workflow** → **Run workflow**
4. Check your email for the report

## Schedule

The workflow runs automatically:
- **Every Friday at 4:00 PM ET (9:00 PM UTC)**
- After CFTC releases data (3:30 PM ET)
- Can be manually triggered anytime

## Report Format

The email contains a formatted text report with:

```
===============================================================================
CFTC COT REPORT - US CRUDE WTI FUTURE
Report Date: 2024-12-10
Source: New York Mercantile Exchange
Generated: 2024-12-14 16:00:00
===============================================================================

Category                        Position            Chg
---------------------------------------------------------------------------

▼ Reportable
  Long                          2,541,739           -18,634
  Short                         2,633,152           -10,602
  Net                             -91,413            -8,032

▼ Non-Commercial
  Long                            60                    +4
  Short                           47                    -6
  Net                             13                   +10
  
... (and more categories)
```

## Project Structure

```
cftc-cot-weekly-report/
├── .github/
│   └── workflows/
│       └── weekly-cot-report.yml    # GitHub Actions workflow
├── cftc_cot_report.py              # Main Python script
├── README.md                        # This file
├── LICENSE                          # MIT License
└── .gitignore                       # Python gitignore
```

## Technical Details

### Dependencies

- **pandas**: Data processing
- **requests**: HTTP requests to CFTC
- Python 3.11+

### Data Source

CFTC Disaggregated Futures Financial Traders report:  
https://www.cftc.gov/files/dea/history/fut_fin_txt_2024.zip

### Key Bug Fixes

✅ Fixed column name: `Report_Date` (not `Report_Date_as_MM_DD_YYYY`)  
✅ Added environment variable support for email credentials  
✅ Proper numeric conversion for all COT data fields  

## Troubleshooting

### Email not sending?

1. Check GitHub Actions log for errors
2. Verify Gmail App Password is correct (not regular password)
3. Ensure 2-Step Verification is enabled on Google Account
4. Check spam folder

### Workflow not running?

1. Check Actions tab is enabled in repository settings
2. Verify cron schedule in `weekly-cot-report.yml`
3. Manually trigger to test

### Data errors?

1. CFTC may not release data on US holidays
2. URL may need updating for 2025+ data:  
   `https://www.cftc.gov/files/dea/history/fut_fin_txt_2025.zip`

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see [LICENSE](LICENSE) file

## Author

**bloombodymind**  
GitHub: [@bloombodymind](https://github.com/bloombodymind)

## Acknowledgments

- CFTC for providing free COT data
- GitHub Actions for free automation
- Python community for excellent libraries

---

**⭐ Star this repo if you find it useful!**
