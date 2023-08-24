# Import necessary libraries
import streamlit as st
from dataclasses import dataclass
from typing import List
from datetime import datetime, timezone
import pandas as pd
import hashlib

# Define a data class for storing transaction records
@dataclass
class Record:
    User: str
    Type: str
    Detail: str
    Received: float
    Spent: float

# Define a data class for creating blocks in the blockchain
@dataclass
class Block:

    # Rename the `data` attribute to `record`, and set the data type to `Record`
    Record: Record
    Creator_Id: int
    Previous_Hash: str = "0"
    Timestamp: str = datetime.now(timezone.utc).strftime("%Y-%M-%D %H:%M:%S") 
    Nonce: int = 0

    # Method to hash the block's attributes
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

# Define a class for the blockchain
@dataclass
class PyChain:
    chain: List[Block]  # List to store blocks
    difficulty: int = 3  # Difficulty level for mining

    # Method for proof of work (mining)
    def proof_of_work(self, block):
        calculated_hash = block.hash_block()

        num_of_zeros = "0" * self.difficulty

        while not calculated_hash.startswith(num_of_zeros):
            block.nonce += 1
            calculated_hash = block.hash_block()

        print("Winning Hash:", calculated_hash)
        return block

    # Method to add a block to the blockchain
    def add_block(self, candidate_block):
        block = self.proof_of_work(candidate_block)
        self.chain += [block]

    # Method to check the validity of the blockchain
    def is_valid(self):
        block_hash = self.chain[0].hash_block()

        for block in self.chain[1:]:
            if block_hash != block.prev_hash:
                print("Blockchain is invalid!")
                return False

            block_hash = block.hash_block()

        print("Blockchain is Valid")
        return True

# Cache the setup function to avoid redundant computations
@st.cache(allow_output_mutation=True)
def setup():
    print("Initializing Chain")
    genesis_record = Record(User="System", Type="n/a", Detail="n/a", Received=0.0, Spent=0.0)
    genesis_block = Block(record=genesis_record, creator_id=0)
    return PyChain([genesis_block])

# Initialize the blockchain using the setup function
pychain = setup()

# Markdown for displaying titles
st.markdown("<h1 style='text-align: center;'>Ledger Chain 📒⛓️</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Securely Record and Track Your Money with the Blockchain Ledger</h2>", unsafe_allow_html=True)

# Input fields for transaction details
User = st.text_input("What is your name?")
Type = st.selectbox("What type of transaction is this?", ["Asset", "Liability", "Revenue", "Expense", "Equity"])
Detail = st.text_input("Detail:")
Received = st.text_input("($) Received:", value="0.0")  # Provide a default value
Spent = st.text_input("($) Spent:", value="0.0")  # Provide a default value


# Button to add a new block to the blockchain
if st.button("Add Block 🆕"):
    prev_block = pychain.chain[-1]
    prev_block_hash = prev_block.hash_block()

    new_block = Block(
        record=Record(User=User, Type=Type, Detail=Detail, Spent=float(Spent), Received=float(Received)),
        creator_id=7,
        prev_hash=prev_block_hash
    )

    pychain.add_block(new_block)
    st.success("Block Added Successfully! 👏")

# Create a list of dictionaries for ledger data
ledger_data = []
for i, block in enumerate(pychain.chain, start=1):
    ledger_data.append({
        "Block": i,
        "User": block.record.User,
        "Type": block.record.Type,
        "Detail": block.record.Detail,
        "Received": block.record.Received,
        "Spent": block.record.Spent,
        "Creator Id": block.Creator_Id,
        "Previous Hash": block.Previous_Hash,
        "Timestamp": block.Timestamp,
        "Nonce": block.Nonce
    })

# title for ledger
st.header("Blockchain Ledger")

# Create a Pandas DataFrame from the ledger data and display it
ledger_df = pd.DataFrame(ledger_data)
st.dataframe(ledger_df.drop(columns=["Block"]), width=1000)

# Button to validate the ledger and display the result
if st.button("Validate Ledger 🕵️‍♀️"):
    is_valid = pychain.is_valid()
    if is_valid:
        st.write("✅ Valid! ✅")
    else:
        st.write("❌ Invalid! ❌")

# Button to download the ledger as a CSV file
if st.button("Prepare Ledger for CSV Download 📲"):
    # Create a Pandas DataFrame from the ledger data
    ledger_df = pd.DataFrame(ledger_data)

    # Save the DataFrame to a CSV file
    csv_file = ledger_df.to_csv(index=False)

    # Provide the CSV file for download
    st.download_button(
        label="Download Ledger CSV 💽",
        data=csv_file.encode('utf-8'),
        file_name="ledger.csv",
        mime="text/csv",
    )

# Set the title for the sidebar section
st.header("Financial Tools 🛠️💸")

# Define functions for financial calculations
def calculate_dti(income, debt):
    return debt / income

def calculate_emergency_fund_ratio(cash, expenses):
    return cash / expenses

# Add a header for the net worth calculator
st.markdown("### Net Worth Calculator")

# Dropdown to select a user from the ledger data
selected_user = st.selectbox("Select a User 🧍", ledger_df["User"].unique())

# Filter the ledger data for the selected user
user_data = ledger_df[ledger_df["User"] == selected_user]

# Calculate total assets and total liabilities for the selected user
total_assets = user_data[user_data["Type"] == "Asset"]["Received"].sum()
total_liabilities = user_data[user_data["Type"] == "Liability"]["Spent"].sum()

# Calculate net worth
net_worth = total_assets - total_liabilities

# Display the net worth for the selected user
st.write(f"Net Worth for {selected_user}: ${net_worth:.2f}")

# Add a header for the debt-to-income ratio calculator
st.markdown("### Debt-to-Income Ratio Calculator")

# Input fields for monthly income and debt
income = st.number_input("Monthly Income ($)", value=1000.0, step=100.0)
debt = st.number_input("Monthly Debt ($)", value=500.0, step=100.0)

# Button to calculate the debt-to-income ratio
if st.button("Calculate DTI Ratio 🧮"):
    dti_ratio = calculate_dti(income, debt)
    st.write(f"Your Debt-to-Income Ratio is: {dti_ratio:.2f}")

    if dti_ratio <= 0.4:
        st.write("Congratulations! Your DTI ratio is within a healthy range.")
    else:
        st.write("Your DTI ratio is higher than recommended. Consider managing your debt.")

# Header for the emergency fund ratio calculator
st.markdown("### Emergency Fund Ratio Calculator")

# Input fields for total cash savings and monthly nondiscretionary expenses
cash = st.number_input("Total Cash Savings ($)", value=5000.0, step=100.0)
expenses = st.number_input("Monthly Nondiscretionary Expenses ($)", value=1000.0, step=100.0)

# Button to calculate the emergency fund ratio
if st.button("Calculate Emergency Fund Ratio 🚨"):
    emergency_fund_ratio = calculate_emergency_fund_ratio(cash, expenses)
    st.write(f"Your Emergency Fund Ratio is: {emergency_fund_ratio:.2f}")

    if 3 <= emergency_fund_ratio <= 6:
        st.write("Congratulations! Your emergency fund is within a recommended range.")
    else:
        st.write("Consider building a larger emergency fund to cover 3 to 6 months of expenses.")

# Header for the discretionary expense ratio calculator
st.markdown("### Discretionary Expense Ratio Calculator")

# Input fields for monthly income and discretionary expenses
income = st.number_input("Monthly Income ($)", value=2000.0, step=100.0)
discretionary_expenses = st.number_input("Monthly Discretionary Expenses ($)", value=300.0, step=50.0)

# Button to calculate the discretionary expense ratio
if st.button("Calculate Discretionary Expense Ratio 🗂️"):
    discretionary_ratio = discretionary_expenses / income
    st.write(f"Your Discretionary Expense Ratio is: {discretionary_ratio:.2f}")

    if discretionary_ratio <= 0.3:
        st.write("Congratulations! Your discretionary expense ratio is within a healthy range.")
    else:
        st.write("Consider managing your discretionary expenses to improve your financial standing.")

st.sidebar.write("Chat with your Virtual Finance Assistant 💬")

# Embed the chatbot iframe with black borders and a title in the sidebar
chatbot_iframe = """
<div style="padding: 10px; text-align: center;">
    <h2>Pro$perPal👑</h2>
    <iframe
        src="https://www.chatbase.co/chatbot-iframe/N6GTBP_f9uvB2GumnXfvU"
        width="100%"
        style="height: 100%; min-height: 550px; border: none; overflow-wrap: break-word; max-width: 300px;"
    ></iframe>
</div>
"""
st.sidebar.markdown(chatbot_iframe, unsafe_allow_html=True)

# Add the chat bubble script tags to the sidebar
chat_bubble_script = """
<script>
  window.chatbaseConfig = {
    chatbotId: "N6GTBP_f9uvB2GumnXfvU",
  };
</script>
<script
  src="https://www.chatbase.co/embed.min.js"
  id="N6GTBP_f9uvB2GumnXfvU"
  defer>
</script>
"""
st.sidebar.markdown(chat_bubble_script, unsafe_allow_html=True)

