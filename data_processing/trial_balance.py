from collections import defaultdict
from datetime import datetime
import pandas as pd
from pandas import Timestamp



def generate_trial_balance(ledger, fiscal_year=(1, 1), filename=None):
    trial_balance = defaultdict(lambda: defaultdict(int))
    beginning_balances = defaultdict(lambda: defaultdict(int))
    ending_balances = defaultdict(lambda: defaultdict(int))
    balances = defaultdict(lambda: defaultdict(int))

    start_time = pd.to_datetime(fiscal_year[0])
    end_time = pd.to_datetime(fiscal_year[1])

    for block in ledger.chain:
        for transaction in block.transactions:
            transaction_date = pd.to_datetime(transaction['accounting_date'], unit='s') if 'accounting_date' in transaction else pd.to_datetime(block.timestamp, unit='s')
            if transaction_date <= start_time:
                accounting_class = transaction['accounting_class']
                subclass = transaction['subclass']
                debit = transaction['debit']
                credit = transaction['credit']

                balances[accounting_class][subclass] += debit - credit
                beginning_balances[accounting_class][subclass] = balances[accounting_class][subclass]

            if start_time <= transaction_date <= end_time:
                accounting_class = transaction['accounting_class']
                subclass = transaction['subclass']
                debit = transaction['debit']
                credit = transaction['credit']

                balances[accounting_class][subclass] += debit - credit
                ending_balances[accounting_class][subclass] = balances[accounting_class][subclass]

    for ac_class in balances.keys():
        for subclass in balances[ac_class].keys():
            trial_balance[ac_class][subclass] = {
                "Beginning Balance": beginning_balances[ac_class][subclass],
                "Ending Balance": ending_balances[ac_class][subclass]
            }

    df = pd.DataFrame.from_dict({(i, j): trial_balance[i][j] for i in trial_balance.keys() for j in trial_balance[i].keys()}, orient='index')

    if filename:
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Trial Balance')

    return df