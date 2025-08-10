import requests
from bs4 import BeautifulSoup
import pandas as pd

# Load CUSIP-to-ticker mapping at module load
try:
    cusip_map_df = pd.read_csv("cusip_ticker_map.csv")
    # Try to handle different possible column names
    cusip_col = [col for col in cusip_map_df.columns if col.lower().startswith("cusip")][0]
    ticker_col = [col for col in cusip_map_df.columns if col.lower().startswith("symb") or col.lower() == "ticker"][0]
    cusip_to_ticker = dict(zip(cusip_map_df[cusip_col].astype(str).str.strip(), cusip_map_df[ticker_col].astype(str).str.strip()))
except Exception as e:
    print(f"Could not load CUSIP-to-ticker mapping: {e}")
    cusip_to_ticker = {}


SEC_HEADERS = {
    "User-Agent": "Mark Matthews mjmatt90gmail.com"
}

def get_cik_for_fund(fund_name):
    """
    Returns a list of (fund_name, cik) tuples matching the search.
    """
    url = f"https://efts.sec.gov/LATEST/search-index"
    resp = requests.post(url, headers=SEC_HEADERS, json={"keys": fund_name, "category": "name"})
    results = resp.json().get("hits", {}).get("hits", [])
    return [(r["_source"]["entityName"], r["_source"]["cik"]) for r in results]

def get_latest_13f_cik(cik):
    """
    Returns the accession number and filing URL for the latest 13F-HR for a CIK.
    """
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    resp = requests.get(url, headers=SEC_HEADERS)
    data = resp.json()
    filings = data.get("filings", {}).get("recent", {})
    for i, form in enumerate(filings.get("form", [])):
        if form == "13F-HR":
            accession = filings["accessionNumber"][i].replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{str(cik).lstrip('0')}/{accession}/primary_doc.xml"
            return accession, filing_url
    return None, None

def parse_13f_holdings(xml_url):
    """
    Parses the 13F XML and returns a list of holdings dicts (cusip, name, shares, value, ticker).
    """
    resp = requests.get(xml_url, headers=SEC_HEADERS)
    soup = BeautifulSoup(resp.content, "xml")
    holdings = []
    for info in soup.find_all("infoTable"):
        cusip = info.find_text("cusip")
        ticker = cusip_to_ticker.get(str(cusip).strip(), "")
        print(f"DEBUG: edgar_whale 55 CUSIP {cusip} maps to ticker {ticker}")
        holding = {
            "nameOfIssuer": info.find_text("nameOfIssuer"),
            "cusip": cusip,
            "ticker": ticker,
            "value": info.find_text("value"),
            "sshPrnamt": info.find_text("sshPrnamt"),
            "sshPrnamtType": info.find_text("sshPrnamtType"),
            "putCall": info.find_text("putCall") if info.find("putCall") else "",
        }
        holdings.append(holding)
    return holdings

def get_whale_13f_holdings(fund_cik_or_name):
    """
    Main function: Given a CIK or fund name, returns latest 13F holdings as a list of dicts.
    """
    cik = fund_cik_or_name
    if not str(cik).isdigit():
        # Try to look up CIK by name
        matches = get_cik_for_fund(cik)
        if not matches:
            print(f"No CIK found for {cik}")
            return []
        cik = matches[0][1]
    accession, xml_url = get_latest_13f_cik(cik)
    if not xml_url:
        print(f"No 13F-HR found for CIK {cik}")
        return []
    return parse_13f_holdings(xml_url)

# Example usage:
if __name__ == "__main__":
    # Example: "Berkshire Hathaway" or CIK "0001067983"
    holdings = get_whale_13f_holdings("Berkshire Hathaway")
    print(f"Found {len(holdings)} holdings in latest 13F filing.")
    for h in holdings[:10]:
        print(h)