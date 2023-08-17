import hashlib
import time






class Transaction:

    # This method initializes an instance of the Transaction class. Inside the constructor, the following attributes 
    # are initialized. Inside the constructor, the following attributes are initialized.
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

    # This method converts the transaction object into a dictionary containing its attributes. 
    # The method also includes some validation to check whether both debit and credit are present in the 
    # data dictionary. If either of them is missing, a warning message is printed.
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
    # This is the constructor method for the Block class. It initializes various attributes of the block, such as 
    # timestamp, transactions, previous_hash, user, block_number, hash, imported, and import_filename.
    def __init__(self, transactions, previous_hash, user, block_number, imported=False, import_filename=None):
        self.timestamp = time.time()
        self.transactions = [transaction.to_dict() for transaction in transactions]
        self.previous_hash = previous_hash
        self.user = user
        self.block_number = block_number
        self.hash = self.get_hash()
        self.imported = imported  # Track if the block is imported or not
        self.import_filename = import_filename  # Track the associated import filename
    
    # This method calculates and returns the hash of the block based on its attributes.
    def get_hash(self):
        header = str(self.transactions) + str(self.previous_hash) + str(self.block_number) + str(self.user)
        header_bytes = header.encode()
        sha = hashlib.sha256(header_bytes)
        return sha.hexdigest()
 
    # This method returns a string representation of the block, including its attributes and the details of the 
    # transactions it contains.
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

    # This method checks if the calculated hash of the block matches the stored hash, ensuring the integrity of the 
    # block's contents.
    def validate_contents(self):
        return self.hash == self.get_hash()