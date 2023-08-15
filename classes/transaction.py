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

    # This method converts the transaction object into a dictionary containing its attributes. The method also includes 
    # some validation to check whether both debit and credit are present in the data dictionary. If either of them is 
    # missing, a warning message is printed.
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