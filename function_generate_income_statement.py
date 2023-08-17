import pandas as pd
from collections import defaultdict


def generate_income_statement(ledger, fiscal_year=('1900-01-01', '9999-12-31')):
    income_statement = defaultdict(lambda: defaultdict(int))
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
                if accounting_class == 'Revenue':
                    income_statement[accounting_class][subclass] += credit - debit
                    income_statement[accounting_class]['Total Revenue'] += credit - debit
                elif accounting_class == 'Expenses':
                    income_statement[accounting_class][subclass] += debit - credit
                    income_statement[accounting_class]['Total Expenses'] += debit - credit

    income_statement['Net Income']['Net Income'] = income_statement['Revenue']['Total Revenue'] - income_statement['Expenses']['Total Expenses']

    df = pd.DataFrame.from_dict(income_statement, orient='columns')

    # Generate the desired_order dynamically
    revenue_keys = list(income_statement['Revenue'].keys())
    expenses_keys = list(income_statement['Expenses'].keys())
    revenue_keys.remove('Total Revenue')  # Remove the 'Total Revenue' key
    expenses_keys.remove('Total Expenses')  # Remove the 'Total Expenses' key
    desired_order = revenue_keys + expenses_keys + ['Total Revenue', 'Total Expenses', 'Net Income']
    
    df = df.reindex(desired_order)

    return df