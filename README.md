# Blockchain Accounting System

This is a simple blockchain-based accounting system implemented in Python. It allows users to create transactions, add them to blocks, and maintain a secure and tamper-proof record of financial transactions.

## Features

- Blockchain data structure with blocks and transactions
- Cryptographic signing of transactions using RSA keys
- Validation of transaction balances within blocks
- Validation of account existence and subclass matching
- Ordering of transactions by timestamp
- Logging of blockchain operations to a file
- Importing transactions from an Excel file
- Generation of financial reports: General Ledger, Balance Sheet, and Income Statement

## Prerequisites

- Python 3.x
- pandas library (`pip install pandas`)
- cryptography library (`pip install cryptography`)
- openpyxl library (`pip install openpyxl`)
- xlsxwriter library (`pip install xlsxwriter`)

## Getting Started

1. Clone this repository or download the source code.
2. Install the required libraries as mentioned in the prerequisites.
3. Run the `main.py` file in your Python environment.

## Usage

1. When prompted, you can choose to import transactions from an Excel file or manually add transactions to the blockchain.
2. If importing transactions, provide the filename and ensure the Excel file follows the required format.
3. If manually adding transactions, follow the prompts to enter transaction details such as sender name, accounting class, subclass, debit, credit, and transaction detail.
4. The system will validate the transactions, balance the debits and credits, and check for account and subclass validity.
5. Financial reports can be generated for a specific time period by providing the start and end dates. Reports will be saved in an Excel file named `financial_reports.xlsx`.
6. The blockchain data will be saved to a file named `blockchain_data.txt` before exiting the program.

## File Structure

- `main.py`: The main script that runs the blockchain accounting system.
- `blockchain.py`: Contains the classes for User, Transaction, Block, and Blockchain.
- `utils.py`: Contains utility functions for file operations, encryption, and report generation.
- `blockchain.log`: Log file that records blockchain operations.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).
