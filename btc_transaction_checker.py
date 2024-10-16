import requests
import json
from datetime import datetime

def get_wallet_info(address):
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full?limit=50"
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None

def parse_timestamp(timestamp_str):
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        return datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')

def safe_get(dct, *keys, default=None):
    for key in keys:
        try:
            dct = dct[key]
        except (KeyError, TypeError):
            return default
    return dct if dct is not None else default

def print_wallet_info(wallet_data):
    if wallet_data:
        print(f"Address: {wallet_data['address']}")
        print(f"Final Balance: {wallet_data['final_balance'] / 1e8:.8f} BTC")
        print(f"Total Received: {wallet_data['total_received'] / 1e8:.8f} BTC")
        print(f"Total Sent: {wallet_data['total_sent'] / 1e8:.8f} BTC")
        print(f"Number of Transactions: {wallet_data['n_tx']}")
        print(f"Unconfirmed Balance: {wallet_data['unconfirmed_balance'] / 1e8:.8f} BTC")
        print(f"Unconfirmed Transactions: {wallet_data['unconfirmed_n_tx']}")
        
        if 'txs' in wallet_data:
            print("\nRecent Transactions:")
            for tx in wallet_data['txs'][:5]:  # Show last 5 transactions
                # Parse the date string
                received = safe_get(tx, 'received')
                date = parse_timestamp(received).strftime('%Y-%m-%d %H:%M:%S') if received else 'Unknown Date'
                
                # Check if this address is in inputs (sending) or outputs (receiving)
                is_sending = any(safe_get(inp, 'addresses', 0) == wallet_data['address'] for inp in tx.get('inputs', []))
                
                if is_sending:
                    amount = sum(safe_get(out, 'value', default=0) for out in tx.get('outputs', [])) / 1e8
                    recipients = [safe_get(out, 'addresses', 0) for out in tx.get('outputs', []) 
                                  if safe_get(out, 'addresses', 0) and safe_get(out, 'addresses', 0) != wallet_data['address']]
                    print(f"Sent: {amount:.8f} BTC on {date}")
                    print(f"  To: {', '.join(recipients[:3])}{'...' if len(recipients) > 3 else ''}")
                else:
                    amount = sum(safe_get(out, 'value', default=0) for out in tx.get('outputs', []) 
                                 if safe_get(out, 'addresses', 0) == wallet_data['address']) / 1e8
                    senders = [safe_get(inp, 'addresses', 0) for inp in tx.get('inputs', []) if safe_get(inp, 'addresses')]
                    print(f"Received: {amount:.8f} BTC on {date}")
                    print(f"  From: {', '.join(senders[:3])}{'...' if len(senders) > 3 else ''}")
                print()  # Add a blank line between transactions for readability
    else:
        print("Failed to retrieve wallet information.")

def main():
    address = input("Enter a Bitcoin wallet address: ")
    wallet_data = get_wallet_info(address)
    print_wallet_info(wallet_data)

if __name__ == "__main__":
    main()
