# import pickle
# import logging



# from class_transaction import Transaction
# from class_block import Block
# from main import accounting_classes, encrypt_message, decrypt_message



# class Blockchain:

#     # The constructor for the Blockchain class initializes the blockchain with a genesis block containing 
#     # a single transaction.
#     def __init__(self, authorized_users):
#         self.chain = []
#         self.authorized_users = authorized_users
#         # Create a genesis block
#         genesis_transaction = Transaction(
#             sender=authorized_users["James"],  # Assuming "James" is always an authorized user
#             accounting_class='Assets',
#             subclass='Cash',
#             debit=0,
#             credit=0,
#             transaction_detail='Genesis block'
#         )
#         self.add_block([genesis_transaction], "James")


#     # This method adds a new block to the blockchain. It checks the validity of the transactions, balances, 
#     # and timestamps before creating and appending the new block to the chain.
#     def add_block(self, transactions, user):
#         if user not in self.authorized_users:
#             raise Exception("Unauthorized user")
#         previous_hash = self.chain[-1].hash if self.chain else None
#         block_number = len(self.chain) + 1  # compute the block number

#         # Validate transaction balancing within the block
#         total_debits = sum(transaction.debit for transaction in transactions)
#         total_credits = sum(transaction.credit for transaction in transactions)
#         if total_debits != total_credits:
#             raise ValueError("Total debits and credits within a block must be equal.")

#         # Validate account existence and subclass matching
#         for transaction in transactions:
#             if transaction.accounting_class not in accounting_classes:
#                 raise ValueError(f"Invalid accounting class: {transaction.accounting_class}")
#             if transaction.subclass not in accounting_classes[transaction.accounting_class]:
#                 accounting_classes[transaction.accounting_class].append(transaction.subclass)

#         # Validate timestamp order
#         timestamps = [transaction.timestamp for transaction in transactions]
#         if timestamps != sorted(timestamps):
#             raise ValueError("Transactions within a block must be ordered by timestamp in ascending order.")

#         new_block = Block(transactions, previous_hash, user, block_number)  # pass block_number to Block constructor
#         self.chain.append(new_block)
#         logging.info(f'Added block {block_number} by user {user}')  # Log that a new block was added
#         self.print_blockchain()

#     # This method returns a list of blocks that fall within the specified time period.
#     def get_blocks_for_period(self, start_time, end_time):
#         return [block for block in self.chain if start_time <= block.timestamp <= end_time]

#     # This method saves the blockchain data to a binary file after encrypting it.
#     def save_to_file(self, filename):
#         with open(filename, 'wb') as f:
#             encrypted_chain = encrypt_message(pickle.dumps(self.chain))
#             f.write(encrypted_chain)

#     # This method loads the encrypted blockchain data from a file and decrypts it to restore the blockchain.
#     def load_from_file(self, filename):
#         with open(filename, 'rb') as f:
#             encrypted_chain = f.read()
#             self.chain = pickle.loads(decrypt_message(encrypted_chain))

#     # This method prints the details of each block in the blockchain, including their attributes and contained 
#     # transactions.
#     def print_blockchain(self):
#         for i, block in enumerate(self.chain):
#             print(f"\nBlock {i + 1}:")
#             print(f"\tPrevious Hash: {block.previous_hash}")
#             print(f"\tBlock Hash: {block.hash}")

#         if block.imported:
#             print(f"\tImported from file: {block.import_filename}")

#         for transaction in block.transactions:
#             print(f"\tDebit: {transaction['debit']}, Credit: {transaction['credit']}, " \
#                   f"Accounting Class: {transaction['accounting_class']}, " \
#                   f"Subclass: {transaction['subclass']}")

#     # This method iterates through the blockchain and validates the contents of each block by checking their hashes.
#     def validate_chain(self):
#         for block in self.chain:
#             if not block.validate_contents():
#                 return False
#         return True