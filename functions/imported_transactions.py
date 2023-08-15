import os
from functions.load_tx_from_excel import load_transactions_from_excel
from classes.transaction import Transaction


def import_transactions(filename, block_number=None):
    imports_folder = "Imports"

    # Only add .xlsx if it's not already there
    filename_with_extension = f"{filename}.xlsx" if not filename.endswith('.xlsx') else filename

    # Construct file path
    file_path = os.path.join(imports_folder, filename_with_extension)
    
    print(f"Looking for file: {file_path}")

    if not os.path.isdir(imports_folder):
        print(f"Folder '{imports_folder}' not found.")
        return

    if not os.path.isfile(file_path):
        print(f"File '{file_path}' not found.")
        return
    else:
        print(f"File '{file_path}' found.")

    transactions = load_transactions_from_excel(file_path)

    converted_transactions = []

    for transaction in transactions:
        sender = transaction['sender']
        accounting_class = transaction['accounting_class']
        subclass = transaction['subclass']
        debit = transaction['debit']
        credit = transaction['credit']
        transaction_detail = transaction.get('transaction_detail', None)
        accounting_date = transaction.get('accounting_date', None)
        
        sender_name = transaction['sender']  # sender_name is a string

        # Find the correct Wallet instance in your authorized_users dict
        sender = authorized_users.get(sender_name)

        if sender is None:
            print(f"No authorized user found for name: {sender_name}")
            continue  # Skip this transaction

        # Now sender is a Wallet instance and you can create your Transaction
        new_transaction = Transaction(sender, accounting_class, subclass, debit, credit, transaction_detail, accounting_date)

        # Debugging print statement
        print(f"New transaction created with accounting_date: {new_transaction.accounting_date}, type: {type(new_transaction.accounting_date)}")

        if block_number is not None:
            new_transaction.block_number = block_number

        converted_transactions.append(new_transaction)

    total_debits = sum(transaction.debit for transaction in converted_transactions)
    total_credits = sum(transaction.credit for transaction in converted_transactions)

    if total_debits != total_credits:
        print("The total debits and credits within the imported transactions are not equal.")
        user_input = input("Do you want to try importing again? (yes/no): ")
        if user_input.lower() == "yes":
            return import_transactions(filename, block_number)
        else:
            return []

    return converted_transactions