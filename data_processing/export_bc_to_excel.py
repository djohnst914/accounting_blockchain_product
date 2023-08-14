import pandas as pd
from data_processing.export_bc_to_excel import generate_general_ledger


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