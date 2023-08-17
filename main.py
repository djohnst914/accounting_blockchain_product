import pickle
import logging
import os
import pandas as pd
from class_user import User
from class_transaction import Transaction
from class_block import Block
from function_load_transactions_from_excel import load_transactions_from_excel
from function_fernet_key import encrypt_message, decrypt_message
from function_generate_general_ledger import generate_general_ledger
from function_add_imported_block import add_imported_block
from function_generate_balance_sheet import generate_balance_sheet
from function_generate_income_statement import generate_income_statement
from function_generate_trial_balance import generate_trial_balance


def main():



# When you run this code, the logging configuration will be set up, and any subsequent log messages   
# generated by your application using the logging module will be written to the "blockchain.log" file 
# with the specified format and timestamp.
    logging.basicConfig(filename='blockchain.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


# Predefined dictionary of Accounting Classes and Subclasses
accounting_classes = {
    'Assets': ['Cash', 'Accounts Receivable', 'Inventory'],
    'Liabilities': ['Accounts Payable', 'Loans Payable', 'Accrued Expenses'],
    'Equity': ['Owner\'s Capital', 'Retained Earnings'],
    'Revenue': ['Sales', 'Service Revenue'],
    'Expenses': ['Rent Expense', 'Salaries Expense', 'Utilities Expense']
}


class Blockchain:

    # The constructor for the Blockchain class initializes the blockchain with a genesis block containing 
    # a single transaction.
    def __init__(self, authorized_users):
        self.chain = []
        self.authorized_users = authorized_users
        # Create a genesis block
        genesis_transaction = Transaction(
            sender=authorized_users["James"],  # Assuming "James" is always an authorized user
            accounting_class='Assets',
            subclass='Cash',
            debit=0,
            credit=0,
            transaction_detail='Genesis block'
        )
        self.add_block([genesis_transaction], "James")


    # This method adds a new block to the blockchain. It checks the validity of the transactions, balances, 
    # and timestamps before creating and appending the new block to the chain.
    def add_block(self, transactions, user):
        if user not in self.authorized_users:
            raise Exception("Unauthorized user")
        previous_hash = self.chain[-1].hash if self.chain else None
        block_number = len(self.chain) + 1  # compute the block number

        # Validate transaction balancing within the block
        total_debits = sum(transaction.debit for transaction in transactions)
        total_credits = sum(transaction.credit for transaction in transactions)
        if total_debits != total_credits:
            raise ValueError("Total debits and credits within a block must be equal.")

        # Validate account existence and subclass matching
        for transaction in transactions:
            if transaction.accounting_class not in accounting_classes:
                raise ValueError(f"Invalid accounting class: {transaction.accounting_class}")
            if transaction.subclass not in accounting_classes[transaction.accounting_class]:
                accounting_classes[transaction.accounting_class].append(transaction.subclass)

        # Validate timestamp order
        timestamps = [transaction.timestamp for transaction in transactions]
        if timestamps != sorted(timestamps):
            raise ValueError("Transactions within a block must be ordered by timestamp in ascending order.")

        new_block = Block(transactions, previous_hash, user, block_number)  # pass block_number to Block constructor
        self.chain.append(new_block)
        logging.info(f'Added block {block_number} by user {user}')  # Log that a new block was added
        self.print_blockchain()

    # This method returns a list of blocks that fall within the specified time period.
    def get_blocks_for_period(self, start_time, end_time):
        return [block for block in self.chain if start_time <= block.timestamp <= end_time]

    # This method saves the blockchain data to a binary file after encrypting it.
    def save_to_file(self, filename):
        with open(filename, 'wb') as f:
            encrypted_chain = encrypt_message(pickle.dumps(self.chain))
            f.write(encrypted_chain)

    # This method loads the encrypted blockchain data from a file and decrypts it to restore the blockchain.
    def load_from_file(self, filename):
        with open(filename, 'rb') as f:
            encrypted_chain = f.read()
            self.chain = pickle.loads(decrypt_message(encrypted_chain))

    # This method prints the details of each block in the blockchain, including their attributes and contained 
    # transactions.
    def print_blockchain(self):
        for i, block in enumerate(self.chain):
            print(f"\nBlock {i + 1}:")
            print(f"\tPrevious Hash: {block.previous_hash}")
            print(f"\tBlock Hash: {block.hash}")

        if block.imported:
            print(f"\tImported from file: {block.import_filename}")

        for transaction in block.transactions:
            print(f"\tDebit: {transaction['debit']}, Credit: {transaction['credit']}, " \
                  f"Accounting Class: {transaction['accounting_class']}, " \
                  f"Subclass: {transaction['subclass']}")


    # This method iterates through the blockchain and validates the contents of each block by checking their hashes.
    def validate_chain(self):
        for block in self.chain:
            if not block.validate_contents():
                return False
        return True


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


def export_blockchain_to_excel(ledger, filename, fiscal_year=None):
    df_gl = generate_general_ledger(ledger, fiscal_year)

    if df_gl.empty:
        print("No transactions for the specified fiscal year.")
        return

    # Split the data by Accounting Class and Subclass
    grouped_data = df_gl.groupby('Accounting Class')

    # Write each Accounting Class to a separate sheet in Excel
    writer = pd.ExcelWriter(filename)
    for accounting_class, data in grouped_data:
        data = data.drop('Accounting Class', axis=1)
        data.to_excel(writer, sheet_name=accounting_class, index=False)
    writer.save()

    # Save the blockchain data to the 'blockchain_data.txt' file
    ledger.save_to_file("blockchain_data.txt")


def generate_reports(ledger, start_time=None, end_time=None, filename=None):
    # Don't ask for input in this function, it will be passed as arguments
    df_gl = generate_general_ledger(ledger, (start_time, end_time))
    df_bs = generate_balance_sheet(ledger, (start_time, end_time))
    df_is = generate_income_statement(ledger, (start_time, end_time))

    if not df_gl.empty or not df_bs.empty or not df_is.empty:
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            if not df_gl.empty:
                df_gl.to_excel(writer, sheet_name='General Ledger')
            if not df_bs.empty:
                df_bs.to_excel(writer, sheet_name='Balance Sheet')
            if not df_is.empty:
                df_is.to_excel(writer, sheet_name='Income Statement')

        logging.info(f'Generated reports: {filename}')
    else:
        print("The DataFrames are empty, so an Excel file will not be written.")

authorized_users = {"James": User("James")}
logging.info('Authorized users initialized')  # Log that authorized users were initialized

ledger = Blockchain(authorized_users)


# Load the blockchain if a save file exists
if os.path.isfile("blockchain_data.txt"):
    ledger.load_from_file("blockchain_data.txt")
logging.info('Blockchain created')  # Log that the blockchain was created

# If the user wants to import transactions from a file
user_input = input('Do you want to import transactions from a file? (yes/no): ')
if user_input.lower() == 'yes':
    filename = input('Enter the filename: ')
    # Check if '.xlsx' is already in the filename
    filename = filename if filename.endswith('.xlsx') else f"{filename}.xlsx"
    try:
        transactions = import_transactions(filename)
        if transactions:
            sender_name = input('Enter the sender name: ')
            add_imported_block(ledger, transactions, sender_name, filename)
        else:
            print('No transactions found in the file.')
    except FileNotFoundError:
        print('File not found.')
    except Exception as e:
        print(f'Error importing transactions: {str(e)}')


start_date = end_date = None
start_time = end_time = None

user_input = input('Do you want to generate a Trial Balance report for a specific time period? (yes/no): ')
if user_input.lower() == 'yes':
    start_date = input('Enter the start date (YYYY-MM-DD): ')
    end_date = input('Enter the end date (YYYY-MM-DD): ')
    try:
        start_time = pd.to_datetime(start_date)
        end_time = pd.to_datetime(end_date)
        filename = 'trial_balance_report.xlsx'
        generate_trial_balance(ledger, fiscal_year=(start_time, end_time), filename=filename)
        print(f"Trial Balance report generated successfully. File saved as '{filename}'")
    except ValueError:
        print("Invalid date format. Please enter dates in the format 'YYYY-MM-DD'.")
else:
    print("No Trial Balance report was generated.")

user_input = input('Do you want to generate financial reports for a specific time period? (yes/no): ')
if user_input.lower() == 'yes':
    start_date = input('Enter the start date (YYYY-MM-DD): ')
    end_date = input('Enter the end date (YYYY-MM-DD): ')
    try:
        start_time = pd.to_datetime(start_date)
        end_time = pd.to_datetime(end_date)
        reports_filename = 'financial_statements.xlsx'
        generate_reports(ledger, start_time, end_time, reports_filename)
        print(f"Financial reports generated successfully. File saved as '{reports_filename}'")
    except ValueError:
        print("Invalid date format. Please enter dates in the format 'YYYY-MM-DD'.")
else:
    print("No financial reports were generated.")

export_blockchain_to_excel(ledger, 'blockchain_data.xlsx', fiscal_year=(start_time, end_time))

# Save the blockchain before exiting
ledger.save_to_file("blockchain_data.txt")
logging.info('Blockchain saved to file')  # Log that the blockchain was saved to file



if __name__ == "__main__":
    main()





# Commented out by James White
#########################################################################################################
# while True:
#     user_input = input('Do you want to add a new block? (yes/no): ')
#     if user_input.lower() == 'yes':
#         # First transaction
#         print("Enter details for the first transaction:")
#         sender_name1 = input('Enter the sender name: ')
#         accounting_class1, subclass1 = get_accounting_class_subclasses()
#         debit1 = float(input('Enter the debit: '))
#         credit1 = float(input('Enter the credit: '))
#         transaction_detail1 = input('Enter the transaction detail (optional): ')
#         accounting_date1 = input('Enter the accounting date (YYYY-MM-DD) or leave blank for today: ')
#         if accounting_date1:
#             accounting_date1 = pd.to_datetime(accounting_date1).timestamp()

#         # Second transaction
#         print("Enter details for the second transaction:")
#         sender_name2 = input('Enter the sender name: ')
#         accounting_class2, subclass2 = get_accounting_class_subclasses()
#         debit2 = float(input('Enter the debit: '))
#         credit2 = float(input('Enter the credit: '))
#         transaction_detail2 = input('Enter the transaction detail (optional): ')
#         accounting_date2 = input('Enter the accounting date (YYYY-MM-DD) or leave blank for today: ')

#         # Check if the totals of debits and credits are equal
#         if debit1 + debit2 != credit1 + credit2:
#             print("The total debits and credits do not match. Please reenter the transactions.")
#             continue

#         # Create the Transaction objects
#         transaction1 = Transaction(
#             sender=authorized_users[sender_name1],
#             accounting_class=accounting_class1,
#             subclass=subclass1,
#             debit=debit1,
#             credit=credit1,
#             transaction_detail=transaction_detail1,
#             accounting_date=accounting_date1,
#         )
#         transaction2 = Transaction(
#             sender=authorized_users[sender_name2],
#             accounting_class=accounting_class2,
#             subclass=subclass2,
#             debit=debit2,
#             credit=credit2,
#             transaction_detail=transaction_detail2,
#             accounting_date=accounting_date2,
#         )
        
#         # Add the transactions to a new block
#         new_block_number = len(ledger.chain) + 1
#         ledger.add_block([transaction1, transaction2], sender_name1)

#         # If the user wants to import transactions from a file
#         user_input = input('Do you want to import transactions from a file? (yes/no): ')
#         if user_input.lower() == 'yes':
#             filename = input('Enter the filename: ')
#             transactions = import_transactions(filename, new_block_number)
#             if transactions:
#                 sender_name = input('Enter the sender name: ')
#                 ledger.add_block(transactions, sender_name)
#             else:
#                 print('No transactions found in the file.')
#     elif user_input.lower() == 'no':
#         break
#     else:
#         print('Invalid input. Please enter "yes" or "no".')

#######################################################################################################



