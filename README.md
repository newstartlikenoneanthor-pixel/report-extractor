# report-extractor
CLI tool that fetches resolved &amp; disclosed HackerOne reports by vulnerability and exports them to CSV.
# Report Extractor

A small CLI tool that fetches **resolved & disclosed** HackerOne reports by vulnerability (CWE/keyword) and exports them to a CSV file.  
Includes a lightweight ASCII banner, spinner, and colorized terminal output.

## Features
- Query HackerOne via GraphQL (search by vulnerability/CWE)
- Pagination support (fetch up to 3000 reports per run)
- Export results to CSV (Title | Severity | URL)
- Animated banner + spinner and colorized report printing (can be omitted if you edit the script)
- Minimal dependencies

## Requirements
- Python 3.7+
- Packages: `requests`, `pyfiglet`

Install dependencies:
```bash
pip install requests pyfiglet
