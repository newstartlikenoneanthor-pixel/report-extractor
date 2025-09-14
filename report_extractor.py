import requests
import argparse
import csv
import sys
import time
import itertools
from pyfiglet import Figlet

# -------------------------------
# Banner with animation
# -------------------------------
def print_banner():
    fig = Figlet(font="standard")  # safe, readable font
    banner = fig.renderText("Report Extractor")

    print("\033[96m")  # cyan color
    for line in banner.splitlines():
        print(line)
        time.sleep(0.02)  # smooth animation
    print("\033[0m")  # reset color
    print("   by x.com/_bronx_101\n")
    time.sleep(0.3)

# -------------------------------
# Loading animation
# -------------------------------
def loading(msg, duration=3):
    spinner = itertools.cycle(["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"])
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f"\r{msg} {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(msg) + 2) + "\r")

# -------------------------------
# Fancy print for reports (faster animation)
# -------------------------------
def fancy_print(title, severity, url):
    colors = {
        "critical": "\033[91m",     # bright red
        "high": "\033[38;5;208m",   # orange
        "medium": "\033[38;5;226m", # bright yellow (sponge bob)
        "low": "\033[92m",          # green
        None: "\033[94m",           # blue if no rating
        "": "\033[94m"              # also empty string = no rating
    }

    sev_key = severity.lower() if severity else None
    color = colors.get(sev_key, "\033[97m")  # fallback white

    print(f"{color}[#] Title: {title}\033[0m")
    time.sleep(0.02)  # faster
    print(f"{color}    Severity: {severity if severity else 'No rating'}\033[0m")
    time.sleep(0.02)  # faster
    print(f"{color}    URL: {url}\033[0m\n")
    time.sleep(0.05)  # faster


# -------------------------------
# Banner + fake loading
# -------------------------------
print_banner()
loading("Connecting to HackerOne API")
print("[+] Connected!")

# -------------------------------
# API setup
# -------------------------------
url = "https://hackerone.com/graphql"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "X-Product-Area": "hacktivity",
    "X-Product-Feature": "overview",
}

cookies = {}

# -------------------------------
# Parse CLI arguments
# -------------------------------
parser = argparse.ArgumentParser(description="Fetch resolved HackerOne reports by bug type")
parser.add_argument("-v", "--vulnerability", nargs="+", required=True, help="Enter the vulnerability name")
parser.add_argument("-o", "--output", help="Output CSV file name (default: bugname.csv)")
parser.add_argument("-n", "--number", type=int, default=100, help="Number of reports to fetch (default: 100, max 3000)")
args = parser.parse_args()

# -------------------------------
# Validate arguments
# -------------------------------
bug_type = " ".join(args.vulnerability)
output_file = args.output if args.output else f"{bug_type.replace(' ', '_')}.csv"
num_reports = args.number

if num_reports <= 0:
    print("[-] Error: Number of reports must be greater than 0.")
    sys.exit(1)
if num_reports > 3000:
    print("[-] Error: HackerOne API max is 3000 reports. Please choose 3000 or less.")
    sys.exit(1)

# -------------------------------
# Fetch reports with pagination
# -------------------------------
def fetch_reports(bug_type, num_reports):
    all_reports = []
    page_size = 100  # enforced by H1
    for offset in range(0, num_reports, page_size):
        size = min(page_size, num_reports - offset)
        payload = {
            "operationName": "HacktivitySearchQuery",
            "variables": {
                "queryString": f'cwe:("{bug_type}") AND substate:("Resolved") AND disclosed:true',
                "size": size,
                "from": offset,
                "sort": {
                    "field": "latest_disclosable_activity_at",
                    "direction": "DESC"
                },
                "product_area": "hacktivity",
                "product_feature": "overview"
            },
            "query": """query HacktivitySearchQuery($queryString: String!, $from: Int, $size: Int, $sort: SortInput!) {
              me { id __typename }
              search(
                index: CompleteHacktivityReportIndex
                query_string: $queryString
                from: $from
                size: $size
                sort: $sort
              ) {
                __typename
                total_count
                nodes {
                  __typename
                  ... on HacktivityDocument {
                    id
                    _id
                    severity_rating
                    report {
                      id
                      _id
                      title
                      url
                      disclosed_at
                    }
                  }
                }
              }
            }"""
        }

        response = requests.post(url, headers=headers, cookies=cookies, json=payload)
        res = response.json()

        nodes = res["data"]["search"]["nodes"]
        all_reports.extend(nodes)

        # stop early if fewer results are returned
        if len(nodes) < size:
            break

    return all_reports

# -------------------------------
# Save + Print
# -------------------------------
reports = fetch_reports(bug_type, num_reports)

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Severity", "URL"])  # header

    for node in reports:
        title = node["report"]["title"]
        severity = node["severity_rating"]
        url = node["report"]["url"]

        writer.writerow([title, severity, url])

        # if user didn't specify -o, also print them nicely
        if not args.output:
            fancy_print(title, severity, url)

print(f"[+] Saved {len(reports)} reports about '{bug_type}' to {output_file}")
