import requests
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import os
import sys

from etrade_auth import get_etrade_session  # Your existing auth function

def fetch_accounts_with_auto_auth():
    session, base_url = get_etrade_session()
    url = f"{base_url}/v1/accounts/list.json"
    response = session.get(url)
    if response.status_code == 401:
        print("❌ 401 Unauthorized: Deleting auth_data.json and re-authenticating.")
        try:
            os.remove("auth_data.json")
        except Exception as e:
            print(f"Could not delete auth_data.json: {e}")
        # Re-authenticate
        session, base_url = get_etrade_session()
        response = session.get(url)
    print("DEBUG: Raw accounts response:", response.text)
    # --- FIX: Use the correct key for your API response ---
    accounts = response.json().get("AccountListResponse", {}).get("Accounts", {}).get("Account", [])
    if not accounts:
        print("No accounts returned by E*TRADE API.")
    return {acct.get("accountDesc", acct["accountIdKey"]): acct["accountIdKey"] for acct in accounts}, session, base_url

def fetch_account_balance(session, base_url, account_id):
    url = f"{base_url}/v1/accounts/{account_id}/balance.json"
    print(f"DEBUG: Fetching balance from URL: {url}")
    response = session.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch balance. Status code: {response.status_code}")
        print("Raw response text:", response.text)
        return {}
    try:
        return response.json().get("BalanceResponse", {})
    except Exception as e:
        print(f"Error decoding JSON for balance: {e}")
        print("Raw response text:", response.text)
        return {}

def fetch_account_positions(session, base_url, account_id):
    url = f"{base_url}/v1/accounts/{account_id}/portfolio.json"
    print(f"DEBUG: Fetching positions from URL: {url}")
    response = session.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch positions. Status code: {response.status_code}")
        print("Raw response text:", response.text)
        return []
    try:
        return response.json().get("PortfolioResponse", {}).get("AccountPortfolio", [{}])[0].get("Position", [])
    except Exception as e:
        print(f"Error decoding JSON for positions: {e}")
        print("Raw response text:", response.text)
        return []

def select_account_gui(account_options):
    selected = {"account": None}

    def on_account_select():
        try:
            idx = account_listbox.curselection()[0]
            selected["account"] = list(account_options.values())[idx]
            for i in range(account_listbox.size()):
                account_listbox.itemconfig(i, bg="#222244", fg="white")
            account_listbox.itemconfig(idx, bg="#4CAF50", fg="white")
        except IndexError:
            pass

    def submit():
        if selected["account"] is None:
            messagebox.showerror("Error", "Please select an account.")
            return
        root.destroy()

    root = tk.Tk()
    root.title("Select E*TRADE Account")
    root.geometry("400x300")
    root.configure(bg="#222244")

    tk.Label(root, text="Select E*TRADE Account:", font=("Arial", 14, "bold"), bg="#222244", fg="white").pack(pady=10)
    account_listbox = tk.Listbox(root, font=("Arial", 12), bg="#222244", fg="white", selectbackground="#4CAF50", selectforeground="white", height=6)
    for desc in account_options.keys():
        account_listbox.insert(tk.END, desc)
    account_listbox.pack(pady=10, fill="x", padx=40)
    account_listbox.bind("<<ListboxSelect>>", lambda e: on_account_select())

    tk.Button(root, text="Submit", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=submit).pack(pady=20)

    root.mainloop()
    return selected["account"]

if __name__ == "__main__":
    account_options, session, base_url = fetch_accounts_with_auto_auth()
    if not account_options:
        print("No accounts found. Please check your E*TRADE API credentials and try again.")
        exit()
    account_id = select_account_gui(account_options)
    if not account_id:
        print("No account selected. Exiting.")
        exit()

    # Get the selected account description for filename
    account_desc = None
    for desc, aid in account_options.items():
        if aid == account_id:
            account_desc = desc.replace(" ", "_").replace("/", "_")
            break
    if not account_desc:
        account_desc = account_id  # fallback

    # Fetch and save data for the selected account
    balance = fetch_account_balance(session, base_url, account_id)
    positions = fetch_account_positions(session, base_url, account_id)

    # Build filename based on account description
    excel_filename = f"Etrade_{account_desc}_data.xlsx"

    # Save to Excel
    with pd.ExcelWriter(excel_filename) as writer:
        pd.DataFrame([{"account_id": account_id, **balance}]).to_excel(writer, sheet_name="Balance", index=False)
        pd.DataFrame(positions).to_excel(writer, sheet_name="Positions", index=False)

    print(f"✅ E*TRADE account data for {account_id} saved to {excel_filename}")
    sys.exit(0)
