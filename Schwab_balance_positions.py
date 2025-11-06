# === Load tokens and refresh if needed ===
def load_tokens():
    with open(TOKEN_FILE, 'r') as f:
        tokens = json.load(f)
    return tokens

def refresh_tokens(tokens):
    now = datetime.utcnow()
    expires_at = datetime.strptime(tokens['expires_at'], "%Y-%m-%dT%H:%M:%SZ")
    if (expires_at - now).total_seconds() < 300:  # 5-minute buffer
        print("🔄 Refreshing access token...")
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token'],
            'client_id': APP_KEY,
            'client_secret': APP_SECRET
        }
        response = requests.post(TOKEN_URL, data=payload)
        response.raise_for_status()
        new_tokens = response.json()
        new_tokens['expires_at'] = (now.replace(microsecond=0) + 
                                    timedelta(seconds=new_tokens['expires_in'])).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(TOKEN_FILE, 'w') as f:
            json.dump(new_tokens, f, indent=2)
        return new_tokens
    return tokens

# === Get account data ===
def get_account_data(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    url = "https://api.schwabapi.com/trader/v1/accounts"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# === Extract and print balances and positions ===
def display_balances_and_positions(account_data):
    for acct in account_data.get('accounts', []):
        acct_id = acct.get('accountId')
        acct_type = acct.get('accountType')
        sec_acct = acct.get('securitiesAccount', {})
        print(f"\n📘 Account ID: {acct_id} | Type: {acct_type}")

        # Balances
        if acct_id == "91562183":  # IRA
            bal = sec_acct.get('initialBalances', {})
            print("💰 Initial Balance (IRA):", bal.get('equity'))
        elif acct_id == "74501314":  # Individual
            bal = sec_acct.get('currentBalances', {})
            print("💰 Current Balance (Individual):", bal.get('equity'))
        else:
            print("⚠️ Unknown account type or ID")

        # Positions
        positions = sec_acct.get('positions', [])
        print("📊 Positions:")
        for pos in positions:
            instr = pos.get('instrument', {})
            symbol = instr.get('symbol')
            qty = pos.get('quantity')
            mv = pos.get('marketValue')
            print(f"  - {symbol}: {qty} shares, Market Value ${mv:,.2f}")

# === Main Execution ===
try:
    tokens = load_tokens()
    tokens = refresh_tokens(tokens)
    account_data = get_account_data(tokens['access_token'])
    display_balances_and_positions(account_data)
except Exception as e:
    print("❌ Error occurred:")
    traceback.print_exc()