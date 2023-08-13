import hashlib
import time
import pickle
import logging
import datetime
import os
from collections import defaultdict
from datetime import datetime
import pandas as pd
from pandas import Timestamp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.backends import default_backend

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

# New class for User with cryptographic capabilities
class User:
    def __init__(self, name):
        self.name = name
        self.private_key = generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def sign_transaction(self, transaction):
        transaction_data = str(transaction).encode()
        signature = self.private_key.sign(
            transaction_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def get_public_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

class Transaction:
    def __init__(self, sender, accounting_class, subclass, debit, credit, transaction_detail=None, accounting_date=None):
        self.timestamp = time.time()
        self.accounting_date = accounting_date if accounting_date else self.timestamp
        self.sender = sender
        self.accounting_class = accounting_class
        self.subclass = subclass
        self.debit = debit
        self.credit = credit
        self.transaction_detail = transaction_detail
        self.signature = sender.sign_transaction(self)

    def to_dict(self):
        data = {
            "timestamp": self.timestamp,
            "accounting_date": self.accounting_date,
            "accounting_class": self.accounting_class,
            "subclass": self.subclass,
            "debit": self.debit,
            "credit": self.credit,
            "sender": self.sender.name,
            "signature": self.signature.hex(),
            "transaction_detail": self.transaction_detail
        }
        if "debit" not in data:
            print(f"WARNING: Transaction without debit: {data}")
        if "credit" not in data:
            print(f"WARNING: Transaction without credit: {data}")
        return data

class Block:
    def __init__(self, transactions, previous_hash, user, block_number, imported=False, import_filename=None):
        self.timestamp = time.time()
        self.transactions = [transaction.to_dict() for transaction in transactions]
        self.previous_hash = previous_hash
        self.user = user
        self.block_number = block_number
        self.hash = self.get_hash()
        self.imported = imported  # Track if the block is imported or not
        self.import_filename = import_filename  # Track the associated import filename

    def get_hash(self):
        header = str(self.transactions) + str(self.previous_hash) + str(self.block_number) + str(self.user)
        header_bytes = header.encode()
        sha = hashlib.sha256(header_bytes)
        return sha.hexdigest()

    def __str__(self):
        output = f"Block {self.block_number}:\n"
        output += f"\tPrevious Hash: {self.previous_hash}\n"
        output += f"\tBlock Hash: {self.hash}\n"
        
        if self.imported:
            output += f"\tImported from file: {self.import_filename}\n"
        
        for transaction in self.transactions:
            output += f"\tDebit: {transaction['debit']}, Credit: {transaction['credit']}, " \
                      f"Accounting Class: {transaction['accounting_class']}, " \
                      f"Subclass: {transaction['subclass']}\n"

        return output

    def validate_contents(self):
        return self.hash == self.get_hash()

class Blockchain:
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

    def get_blocks_for_period(self, start_time, end_time):
        return [block for block in self.chain if start_time <= block.timestamp <= end_time]

    def save_to_file(self, filename):
        with open(filename, 'wb') as f:
            encrypted_chain = encrypt_message(pickle.dumps(self.chain))
            f.write(encrypted_chain)

    def load_from_file(self, filename):
        with open(filename, 'rb') as f:
            encrypted_chain = f.read()
            self.chain = pickle.loads(decrypt_message(encrypted_chain))

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

    def validate_chain(self):
        for block in self.chain:
            if not block.validate_contents():
                return False
        return True

def load_transactions_from_excel(filename):
    df = pd.read_excel(filename)

    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['accounting_date'] = pd.to_datetime(df['accounting_date'])

    transactions = df.to_dict('records')
    print(transactions)

    for transaction in transactions:
        print(f"Accounting date before conversion: {transaction['accounting_date']}, type: {type(transaction['accounting_date'])}")

        if 'timestamp' not in transaction:
            transaction['timestamp'] = time.time()
            print(f"WARNING: Loaded transaction without timestamp: {transaction}")
        else:
            transaction['timestamp'] = pd.to_datetime(transaction['timestamp']).timestamp()

        if 'accounting_date' in transaction and not pd.isnull(transaction['accounting_date']):
            transaction['accounting_date'] = transaction['accounting_date'].timestamp()
        
        print(f"Accounting date after conversion: {transaction.get('accounting_date')}, type: {type(transaction.get('accounting_date'))}")

        if 'debit' not in transaction:
            print(f"WARNING: Loaded transaction without debit: {transaction}")
            transaction['debit'] = 0

        if 'credit' not in transaction:
            print(f"WARNING: Loaded transaction without credit: {transaction}")
            transaction['credit'] = 0

        transaction['debit'] = float(transaction['debit'])
        transaction['credit'] = float(transaction['credit'])

    return transactions

def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """
    Load the previously generated key
    """
    return open("secret.key", "rb").read()

def encrypt_message(message_bytes):
    """
    Encrypts a message
    """
    key = load_key()
    f = Fernet(key)
    encrypted_message = f.encrypt(message_bytes)
    return encrypted_message

def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message  # don't decode

def get_accounting_class_subclasses():
    """
    Prompts the user to select an Accounting Class and Subclass from the predefined dictionary,
    or add a new Accounting Class or Subclass.
    Returns the selected Accounting Class and Subclass.
    """
    print("Select an Accounting Class:")
    for i, accounting_class in enumerate(accounting_classes.keys()):
        print(f"{i + 1}. {accounting_class}")
    print("0. Add a new Accounting Class")
    class_choice = input("Enter the number of the Accounting Class: ")
    
    if class_choice == "0":
        new_class = input("Enter the name of the new Accounting Class: ")
        accounting_classes[new_class] = []
        subclass_choice = input("Enter the name of the Subclass for the new Accounting Class: ")
        accounting_classes[new_class].append(subclass_choice)
        return new_class, subclass_choice
    elif class_choice.isdigit() and 1 <= int(class_choice) <= len(accounting_classes):
        class_index = int(class_choice) - 1
        selected_class = list(accounting_classes.keys())[class_index]
        subclasses = accounting_classes[selected_class]
        print(f"\nSelect a Subclass for {selected_class}:")
        for i, subclass in enumerate(subclasses):
            print(f"{i + 1}. {subclass}")
        print("0. Add a new Subclass")
        subclass_choice = input("Enter the number of the Subclass: ")
        
        if subclass_choice == "0":
            new_subclass = input("Enter the name of the new Subclass: ")
            accounting_classes[selected_class].append(new_subclass)
            return selected_class, new_subclass
        elif subclass_choice.isdigit() and 1 <= int(subclass_choice) <= len(subclasses):
            subclass_index = int(subclass_choice) - 1
            selected_subclass = subclasses[subclass_index]
            return selected_class, selected_subclass
    
    # Invalid choice, recursively call the function again
    print("Invalid choice. Please try again.")
    return get_accounting_class_subclasses()

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

def add_imported_block(ledger, transactions, sender_name, import_filename):
    new_block_number = len(ledger.chain) + 1
    new_block = Block(transactions, ledger.chain[-1].hash if ledger.chain else None, sender_name, new_block_number,
                      imported=True, import_filename=import_filename)
    ledger.chain.append(new_block)
    logging.info(f"Added imported block {new_block_number} by user {sender_name} from file '{import_filename}'")
    ledger.print_blockchain()

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

def generate_balance_sheet(ledger, fiscal_year=('1900-01-01', '9999-12-31')):
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

    totals['Equity'] = totals['Assets'] - totals['Liabilities']

    df = pd.DataFrame.from_dict(balance_sheet, orient='columns')
    totals_row = pd.DataFrame(totals, index=['Total']).transpose()
    df = pd.concat([df, totals_row], axis=1)

    return df

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