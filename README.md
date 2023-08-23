## **Ledger Chain: Harnessing Blockchain for Secure Financial Transactions**

Blockchain, at its core, is a decentralized ledger of transactions that is secure, transparent, and tamper-proof. The Ledger Chain taps into the immense potential of this technology to offer users a trustworthy environment for logging their financial dealings.

### **Decentralized & Immutable**:

Unlike traditional databases where records are stored in a single location and are susceptible to alterations or hacks, blockchain spreads the data across numerous nodes. Every transaction added to this chain is encrypted and sealed, ensuring that past records cannot be altered without altering subsequent blocks, a feat nearly impossible to achieve without being detected.

### **The Power of the Ledger Chain**:

By utilizing blockchain technology, Ledger Chain provides a secure system where every transaction, once recorded, remains in the system permanently, protected from external threats or internal manipulation. This makes the Ledger Chain an ideal platform for logging financial transactions where the integrity of records is of paramount importance.

### **Versatile Financial Record Keeping**:

The Ledger Chain isn't just about security; it's about flexibility. Users can input various types of financial transactions, whether it's daily expenses, income, investments, or any other monetary exchange. Each entry undergoes the same rigorous process of verification, ensuring the accuracy and authenticity of every single record.

### **Assured Integrity**:

Blockchain's core feature is its cryptographic security. Each block contains a cryptographic hash of the previous block, creating an interconnected chain of transactions. This means that any attempt to alter a transaction would require changing every subsequent block in the chain—a task so computationally intense that it renders tampering infeasible. With Ledger Chain, users can rest easy knowing their financial records are safeguarded with the best in cryptographic security, ensuring the integrity and authenticity of each entry.

---

## *Technologies*

- **Programming Language:** Python
- **Libraries:** pandas, hashlib, io, datetime
- **Web Framework:** Streamlit (`st`)
- **Operating Systems:** Mac OS, Microsoft Windows

---

## *Installation Guide*

1. **Prerequisites:**
    - Ensure you have Python installed:
        - **[Install Python](https://www.python.org/downloads/)**
    - Install required libraries:
        - Streamlit: `pip install streamlit`
        - Pandas: `pip install pandas`

2. **Clone Repo:** 
   Navigate to your desired directory and:
   
    ```bash
    git clone git@github.com:jswhite1992/accounting_blockchain_product.git
    cd <repository-folder-name>
    ```

3. **Running the Application:**
    ```bash
    streamlit run ledgr.py
    ```

---

## *Usage*

1. Open the Streamlit application via your web browser.
2. Input your name and provide transaction details such as the type (Revenue or Expense), specific details (e.g., paycheck, coffee), amounts credited and debited, and any additional notes.
3. Click on the "Add Block" button to add the transaction to the blockchain.
4. View the ledger to see the list of transactions recorded in the blockchain.
5. Validate the blockchain's integrity using the "Validate Ledger" button.
6. Download the blockchain ledger as an Excel file for offline viewing and storage.

---

## *Summary*

**Key Features:**

1. **Record Class:** A dataclass that captures individual transaction records.
2. **Block Class:** Represents individual blocks in the blockchain, holding the record, previous block's hash, a nonce, and other metadata.
3. **PyChain Class:** A blockchain implementation that includes methods for proof-of-work, adding blocks, and validating the chain.
4. **Streamlit Web App:** An intuitive web application that allows users to interact with the blockchain, record transactions, view the ledger, and validate the blockchain.


---
## *Contributors*

**Rosalinda Olvera Fernandez**

[GitHub](https://github.com/rolvera05) - rolvera98271@gmail.com

**Alex Valenzuela**

[GitHub](axvalenzuela@gmail.com) - axvalenzuela@gmail.com

**James White**

[GitHub](jswhite1992@gmail.com) - jswhite1992@gmail.com

**Michelle Silver**

[GitHub](supersilver1978@gmail.com) - supersilver1978@gmail.com

**Dylan Johnston**

[GitHub](dylanhjjohnston@gmail.com) - dylanhjjohnston@gmail.com

---


## *References*

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Hashlib Documentation](https://docs.python.org/3/library/hashlib.html)

---

