import pandas as pd
from collections import defaultdict




# It imports the necessary libraries, including defaultdict and pd (Pandas).
def generate_balance_sheet(ledger, fiscal_year=('1900-01-01', '9999-12-31')):
    # It initializes a balance_sheet defaultdict to store the balance sheet data, where each entry corresponds to an 
    # accounting class (Assets, Liabilities, Equity) and its subclasses, with initial values set to 0.
    balance_sheet = defaultdict(lambda: defaultdict(int))
    totals = defaultdict(int)
    start_time = pd.to_datetime(fiscal_year[0])
    end_time = pd.to_datetime(fiscal_year[1])

    for block in ledger.chain:
        for transaction in block.transactions:
            transaction_date = pd.to_datetime(transaction['accounting_date'], unit='s') if 'accounting_date' in transaction else pd.to_datetime(block.timestamp, unit='s')
            if start_time <= transaction_date <= end_time:
                accounting_class = transaction['accounting_class']
                subclass = transaction['subclass']
                debit = transaction['debit']
                credit = transaction['credit']
                if accounting_class in ['Assets', 'Liabilities', 'Equity']:
                    balance_sheet[accounting_class][subclass] += debit - credit
                    totals[accounting_class] += debit - credit

    # After processing all transactions, it calculates the total Equity value as the difference between Assets and 
    # Liabilities.
    totals['Equity'] = totals['Assets'] - totals['Liabilities']

    # It constructs a Pandas DataFrame from the balance_sheet defaultdict, using the accounting classes as columns and 
    # subclasses as index.
    df = pd.DataFrame.from_dict(balance_sheet, orient='columns')
    # It creates a separate DataFrame for the totals and transposes it to have the accounting classes as rows and a 
    # single 'Total' row.
    totals_row = pd.DataFrame(totals, index=['Total']).transpose()
    # It concatenates the two DataFrames (balance sheet and totals) along the columns axis.
    df = pd.concat([df, totals_row], axis=1)
    # It returns the final DataFrame representing the generated balance sheet.
    return df
