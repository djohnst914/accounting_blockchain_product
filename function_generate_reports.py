# import pandas as pd
# import logging
# from function_generate_general_ledger import generate_general_ledger
# from function_generate_balance_sheet import generate_balance_sheet
# from function_generate_income_statement import generate_income_statement
# from class_user import User
# from class_blockchain import Blockchain


# def generate_reports(ledger, start_time=None, end_time=None, filename=None):
#     # Don't ask for input in this function, it will be passed as arguments
#     df_gl = generate_general_ledger(ledger, (start_time, end_time))
#     df_bs = generate_balance_sheet(ledger, (start_time, end_time))
#     df_is = generate_income_statement(ledger, (start_time, end_time))

#     if not df_gl.empty or not df_bs.empty or not df_is.empty:
#         with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
#             if not df_gl.empty:
#                 df_gl.to_excel(writer, sheet_name='General Ledger')
#             if not df_bs.empty:
#                 df_bs.to_excel(writer, sheet_name='Balance Sheet')
#             if not df_is.empty:
#                 df_is.to_excel(writer, sheet_name='Income Statement')

#         logging.info(f'Generated reports: {filename}')
#     else:
#         print("The DataFrames are empty, so an Excel file will not be written.")

# authorized_users = {"James": User("James")}
# logging.info('Authorized users initialized')  # Log that authorized users were initialized

# ledger = Blockchain(authorized_users)