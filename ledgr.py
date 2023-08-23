import streamlit as st
from dataclasses import dataclass
from typing import List
import datetime as datetime
import pandas as pd
import hashlib
import io


@dataclass
class Record:
    User: str
    Accounting_Class: str
    Subclass: str
    Debits: float
    Credits: float
    Transaction_Detail: str

@dataclass
class Block:

    # Rename the `data` attribute to `record`, and set the data type to `Record`
    record: Record
    creator_id: int
    prev_hash: str = "0"
    timestamp: str = datetime.datetime.utcnow().strftime("%Y-%M-%D %H:%M:%S") 
    nonce: int = 0

    def hash_block(self):
        sha = hashlib.sha256()

        record = str(self.record).encode()
        sha.update(record)

        creator_id = str(self.creator_id).encode()
        sha.update(creator_id)

        timestamp = str(self.timestamp).encode()
        sha.update(timestamp)

        prev_hash = str(self.prev_hash).encode()
        sha.update(prev_hash)

        nonce = str(self.nonce).encode()
        sha.update(nonce)

        return sha.hexdigest()


@dataclass
class PyChain:
    chain: List[Block]
    difficulty: int = 3

    def proof_of_work(self, block):

        calculated_hash = block.hash_block()

        num_of_zeros = "0" * self.difficulty

        while not calculated_hash.startswith(num_of_zeros):

            block.nonce += 1

            calculated_hash = block.hash_block()

        print("Wining Hash", calculated_hash)
        return block

    def add_block(self, candidate_block):
        block = self.proof_of_work(candidate_block)
        self.chain += [block]

    def is_valid(self):
        block_hash = self.chain[0].hash_block()

        for block in self.chain[1:]:
            if block_hash != block.prev_hash:
                print("Blockchain is invalid!")
                return False

            block_hash = block.hash_block()

        print("Blockchain is Valid")
        return True
    
@st.cache(allow_output_mutation=True)
def setup():
    print("Initializing Chain")
    genesis_record = Record(User="System", Accounting_Class="n/a", Subclass="n/a", Debits=0.0, Credits=0.0, Transaction_Detail="n/a")
    genesis_block = Block(record=genesis_record, creator_id=0)
    return PyChain([genesis_block])


pychain = setup()

st.markdown("<h1 style='text-align: center;'>Ledger Chain</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Record and Track Your Money with the Blockchain 😎</h2>", unsafe_allow_html=True)

User = st.text_input("What is your name?")
Accounting_Class = st.text_input("What kind of transaction is this? (Revenue or Expense)")
Subclass = st.text_input("Is it a paycheck, coffee, gas, etc.?")
Credits = st.text_input("Money Received:")
Debits = st.text_input("Money Spent:")
Transaction_Detail = st.text_input("Make a Note!")

if st.button("Add Block"):
    prev_block = pychain.chain[-1]
    prev_block_hash = prev_block.hash_block()

    new_block = Block(
        record=Record(User=User, Accounting_Class=Accounting_Class, Subclass=Subclass, Debits=float(Debits), Credits=float(Credits), Transaction_Detail=Transaction_Detail),
        creator_id=7,
        prev_hash=prev_block_hash
    )

    pychain.add_block(new_block)
    st.success("Block Added Successfully!")

st.markdown("## Blockchain Ledger")

ledger_data = []
for i, block in enumerate(pychain.chain, start=1):
    ledger_data.append({
        "Block": i,
        "User": block.record.User,
        "Item Type": block.record.Accounting_Class,
        "Item Description": block.record.Subclass,
        "Money Spent": block.record.Debits,
        "Money Received": block.record.Credits,
        "Transaction Detail": block.record.Transaction_Detail,
        "Creator Id": block.creator_id,
        "Prev Hash": block.prev_hash,
        "Timestamp": block.timestamp,
        "Nonce": block.nonce
    })

ledger_df = pd.DataFrame(ledger_data)
st.dataframe(ledger_df.drop(columns=["Block"]), width=1000)

if st.button("Validate Ledger🕵️‍♀️"):
    is_valid = pychain.is_valid()
    if is_valid:
        st.write("✅Valid!")
    else:
        st.write("❌Invalid!")

st.header("Download Blockchain Ledger")

if st.button("Prepare Ledger for Download📲"):
    ledger_data = []

    for block in pychain.chain:
        ledger_data.append({
            "User": block.record.User,
            "Item Type": block.record.Accounting_Class,
            "Item Description": block.record.Subclass,
            "Money Spent": block.record.Debits,
            "Money Received": block.record.Credits,
            "Transaction Detail": block.record.Transaction_Detail,
            "Creator Id": block.creator_id,
            "Prev Hash": block.prev_hash,
            "Timestamp": block.timestamp,
            "Nonce": block.nonce
        })

    blockchain_excel = pd.DataFrame(ledger_data).astype(str)
    excel_file = io.BytesIO()
    excel_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    blockchain_excel.to_excel(excel_writer, sheet_name='Blockchain Ledger', index=False)
    excel_writer.save()
    excel_file.seek(0)
    
    # Download the Excel file directly
    st.download_button(
        label="Download Ledger as an Excel💽",
        data=excel_file,
        file_name="blockchain_ledger.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )