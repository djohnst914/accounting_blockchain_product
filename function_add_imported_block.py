import logging
from class_block import Block


def add_imported_block(ledger, transactions, sender_name, import_filename):
    new_block_number = len(ledger.chain) + 1
    new_block = Block(transactions, ledger.chain[-1].hash if ledger.chain else None, sender_name, new_block_number,
                      imported=True, import_filename=import_filename)
    ledger.chain.append(new_block)
    logging.info(f"Added imported block {new_block_number} by user {sender_name} from file '{import_filename}'")
    ledger.print_blockchain()