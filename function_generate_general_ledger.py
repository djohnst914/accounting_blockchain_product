# import pandas as pd
# import datetime



# def generate_general_ledger(ledger, fiscal_year=(None, None)):
#     data = []
#     start_time = fiscal_year[0].to_pydatetime() if fiscal_year[0] else None
#     end_time = fiscal_year[1].to_pydatetime() if fiscal_year[1] else None

#     for i, block in enumerate(ledger.chain):
#         for transaction in block.transactions:
#             timestamp = float(transaction.get('timestamp', 0))  # convert timestamp to float

#             if 'accounting_date' in transaction:
#                 timestamp_in_seconds = float(transaction['accounting_date'])
#                 accounting_date = datetime.fromtimestamp(timestamp_in_seconds)
#             else:
#                 timestamp_in_seconds = timestamp  # Assuming `timestamp` is already in seconds.
#                 accounting_date = datetime.fromtimestamp(timestamp_in_seconds)

#             if start_time and end_time:
#                 if start_time <= accounting_date <= end_time:
#                     data.append({
#                         "Block": i + 1,
#                         "Timestamp": pd.Timestamp.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
#                         "Accounting Date": pd.Timestamp.fromtimestamp(accounting_date.timestamp()).strftime('%Y-%m-%d'),
#                         "Accounting Class": transaction['accounting_class'],
#                         "Subclass": transaction['subclass'].capitalize(),
#                         "Debit": transaction['debit'],
#                         "Credit": transaction['credit'],
#                         "Transaction Detail": transaction.get('transaction_detail', 'N/A'),
#                         "Sender": transaction['sender'],
#                         "Signature": transaction['signature'],
#                     })
#             else:
#                 data.append({
#                     "Block": i + 1,
#                     "Timestamp": pd.Timestamp.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
#                     "Accounting Date": pd.Timestamp.fromtimestamp(accounting_date.timestamp()).strftime('%Y-%m-%d'),
#                     "Accounting Class": transaction['accounting_class'],
#                     "Subclass": transaction['subclass'].capitalize(),
#                     "Debit": transaction['debit'],
#                     "Credit": transaction['credit'],
#                     "Transaction Detail": transaction.get('transaction_detail', 'N/A'),
#                     "Sender": transaction['sender'],
#                     "Signature": transaction['signature'],
#                 })

#     df = pd.DataFrame(data)
#     return df



import pandas as pd
from datetime import datetime

def convert_timestamp(timestamp):
    return pd.Timestamp.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def generate_general_ledger(ledger, fiscal_year=(None, None)):
    data = []
    start_time = fiscal_year[0].to_pydatetime() if fiscal_year[0] else None
    end_time = fiscal_year[1].to_pydatetime() if fiscal_year[1] else None

    for i, block in enumerate(ledger.chain):
        for transaction in block.transactions:
            timestamp = float(transaction.get('timestamp', 0))
            accounting_date = datetime.fromtimestamp(float(transaction.get('accounting_date', timestamp)))

            if start_time and end_time and start_time <= accounting_date <= end_time:
                data.append({
                    "Block": i + 1,
                    "Timestamp": convert_timestamp(timestamp),
                    "Accounting Date": accounting_date.strftime('%Y-%m-%d'),
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
