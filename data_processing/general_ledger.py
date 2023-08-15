from datetime import datetime
import pandas as pd


#generate_key()  # Generate a new key when first running the application

def generate_general_ledger(ledger, fiscal_year=(None, None)):
    data = []
    start_time = fiscal_year[0].to_pydatetime() if fiscal_year[0] else None
    end_time = fiscal_year[1].to_pydatetime() if fiscal_year[1] else None

    for i, block in enumerate(ledger.chain):
        for transaction in block.transactions:
            timestamp = float(transaction.get('timestamp', 0))  # convert timestamp to float

            if 'accounting_date' in transaction:
                timestamp_in_seconds = float(transaction['accounting_date'])
                accounting_date = datetime.fromtimestamp(timestamp_in_seconds)
            else:
                timestamp_in_seconds = timestamp  # Assuming `timestamp` is already in seconds.
                accounting_date = datetime.fromtimestamp(timestamp_in_seconds)

            if start_time and end_time:
                if start_time <= accounting_date <= end_time:
                    data.append({
                        "Block": i + 1,
                        "Timestamp": pd.Timestamp.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                        "Accounting Date": pd.Timestamp.fromtimestamp(accounting_date.timestamp()).strftime('%Y-%m-%d'),
                        "Accounting Class": transaction['accounting_class'],
                        "Subclass": transaction['subclass'].capitalize(),
                        "Debit": transaction['debit'],
                        "Credit": transaction['credit'],
                        "Transaction Detail": transaction.get('transaction_detail', 'N/A'),
                        "Sender": transaction['sender'],
                        "Signature": transaction['signature'],
                    })
            else:
                data.append({
                    "Block": i + 1,
                    "Timestamp": pd.Timestamp.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    "Accounting Date": pd.Timestamp.fromtimestamp(accounting_date.timestamp()).strftime('%Y-%m-%d'),
                    "Accounting Class": transaction['accounting_class'],
                    "Subclass": transaction['subclass'].capitalize(),
                    "Debit": transaction['debit'],
                    "Credit": transaction['credit'],
                    "Transaction Detail": transaction.get('transaction_detail', 'N/A'),
                    "Sender": transaction['sender'],
                    "Signature": transaction['signature'],
                })

    df = pd.DataFrame(data)
    return df