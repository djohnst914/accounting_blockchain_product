import pandas as pd
import time


def load_transactions_from_excel(filename):

    # The function starts by reading the data from the Excel file specified by the filename parameter using 
    # pd.read_excel(filename), where pd refers to the Pandas library.   
    df = pd.read_excel(filename)

    # The 'timestamp' column is converted to a datetime format using pd.to_datetime and then formatted as a string in 
    # the 'YYYY-MM-DD HH:MM:SS' format. The 'accounting_date' column is also converted to a datetime format using 
    # pd.to_datetime.
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['accounting_date'] = pd.to_datetime(df['accounting_date'])

    # The data from the DataFrame (df) is converted to a list of dictionaries, where each dictionary represents a 
    # transaction. This list of transactions is stored in the transactions variable.
    transactions = df.to_dict('records')
    print(transactions)

    for transaction in transactions:
        print(f"Accounting date before conversion: {transaction['accounting_date']}, type: {type(transaction['accounting_date'])}")

        # It checks if a 'timestamp' key exists in the transaction. If not, it sets the 'timestamp' key to the current 
        # time using time.time().
        if 'timestamp' not in transaction:
            transaction['timestamp'] = time.time()
            print(f"WARNING: Loaded transaction without timestamp: {transaction}")

        # If the 'timestamp' key exists, it converts the value to a Unix timestamp using pd.to_datetime(...).timestamp().    
        else:
            transaction['timestamp'] = pd.to_datetime(transaction['timestamp']).timestamp()
        
        # If the 'accounting_date' key exists and the value is not null, it converts the value to a Unix timestamp 
        # using .timestamp().
        if 'accounting_date' in transaction and not pd.isnull(transaction['accounting_date']):
            transaction['accounting_date'] = transaction['accounting_date'].timestamp()
        
        # It then prints the accounting date and its type after conversion.
        print(f"Accounting date after conversion: {transaction.get('accounting_date')}, type: {type(transaction.get('accounting_date'))}")

        # If the 'debit' key is not present in the transaction, it sets 'debit' to 0 and prints a warning.
        if 'debit' not in transaction:
            print(f"WARNING: Loaded transaction without debit: {transaction}")
            transaction['debit'] = 0

        # If the 'credit' key is not present in the transaction, it sets 'credit' to 0 and prints a warning.
        if 'credit' not in transaction:
            print(f"WARNING: Loaded transaction without credit: {transaction}")
            transaction['credit'] = 0

        # Finally, it converts the 'debit' and 'credit' values to float data type.
        transaction['debit'] = float(transaction['debit'])
        transaction['credit'] = float(transaction['credit'])

    # The function returns the list of processed transactions.
    return transactions