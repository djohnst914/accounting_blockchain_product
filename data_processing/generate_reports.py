from collections import defaultdict
from datetime import datetime
import pandas as pd
from pandas import Timestamp
import logging
from classes.user import User
from classes.blockchain import Blockchain
from data_processing.balance_sheet import generate_balance_sheet
from data_processing.income_statement import generate_income_statement
from data_processing.general_ledger import generate_general_ledger


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



