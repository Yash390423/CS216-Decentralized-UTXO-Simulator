# Bitcoin Transaction & UTXO Simulator  

### **CS 216: Introduction to Blockchain:  Assignment**

## Overview
This project is a **Python-based command-line simulator** that demonstrates Bitcoin's **UTXO (Unspent Transaction Output)** transaction model.  
It simulates the full lifecycle of a transaction: **creation → validation → mempool → mining → confirmation**.

---
## Features Implemented


### UTXO Management
- Tracks all unspent outputs
- Computes balances from UTXOs

### Transaction Validation
- Input existence check
- Ownership verification
- No double-spend within a transaction
- No mempool conflicts
- Conservation of value & fee calculation

### Mempool
- Stores valid unconfirmed transactions
- Prevents double-spending using `spent_utxos`
- Fee-based transaction prioritization

### Mining Simulation
- Selects highest-fee transactions
- Updates UTXO set permanently
- Rewards miner with total transaction fees

### Double-Spending Demonstrations
- Same-transaction double spend
- Mempool conflict
- Race attack (first-seen rule)

---

## Project Structure
```
project_root/
├── main.py                  # Program entry point & CLI
├── README.md
├── src/
│   ├── utxo_manager.py      # UTXO database
│   ├── transaction.py       # Transaction structure & ID generation
│   ├── validator.py         # Transaction validation rules
│   ├── mempool.py           # Mempool management
│   └── block.py             # Mining simulation
└── tests/
    └── test_scenarios.py    # Mandatory test cases (1–10)
```

---

## How to Run

**Requirements:** Python 3.8+ (standard library only)

```bash
cd project_root
python main.py
```

No external libraries or installations are required.

---

## Initial State (Genesis UTXOs)

The simulator starts with the following confirmed UTXOs:

| Owner   | Amount (BTC) |
|---------|-------------|
| Alice   | 50.0        |
| Bob     | 30.0        |
| Charlie | 20.0        |
| David   | 10.0        |
| Eve     | 5.0         |



---


## Test Scenarios

| ID | Test Name | Description |
| :--- | :--- | :--- |
| **1** | Basic Valid Transaction | Verifies a standard transfer (Alice → Bob). |
| **2** | Multiple Inputs | Aggregates multiple small UTXOs to pay a larger amount. |
| **3** | Double-Spend (Same Tx) | Attempts to use the exact same UTXO twice in one transaction input list. |
| **4** | Mempool Conflict | Attempts to create a 2nd transaction using a UTXO already locked in the Mempool. |
| **5** | Insufficient Funds | Ensures a user cannot spend more than their confirmed balance. |
| **6** | Negative Amount | Prevents creating outputs with negative BTC values. |
| **7** | Zero Fee | Allows transactions where Input Sum = Output Sum (Fee = 0). |
| **8** | Race Attack | Simulates two conflicting transactions arriving; verifies the \"First-Seen\" rule. |
| **9** | Mining Flow | Verifies that mining clears the mempool and updates user balances. |
| **10** | Unconfirmed Chain | Prevents spending an output that is sitting in the mempool but not yet mined. |
---

## Program Menu

```
=== Bitcoin Transaction Simulator ===
1. Create new transaction
2. View UTXO set
3. View mempool
4. Mine block
5. Run test scenarios
6. Exit
```
---

### Menu Options:
1.  **Create new transaction:**
    *   Asks for Sender, Recipient, and Amount.
    *   Automatically selects available UTXOs.
    *   Calculates Change and Fees (0.001 BTC default).
    
2.  **View UTXO set:**
    *   Displays the raw database of all unspent coins currently on the ledger.
3.  **View mempool:**
    *   Shows pending transactions waiting to be mined.
4.  **Mine block:**
    *   Simulates a miner processing the block.\n    *   Updates the global UTXO set and rewards the miner.
5.  **Run test scenarios:**
    *   Opens the sub-menu to run the 10 specific logic tests.\
6.  **Exit:** Closes the simulator.

---
## Design Decisions

- **No unconfirmed chaining:** Spending outputs from mempool transactions is rejected, keeping the design simple and deterministic.
- **First-seen rule enforced:** Conflicting transactions are rejected even if a later one has a higher fee.
- **In-memory state only:** No files, databases, or networking used.

---

## Technologies Used

- **Language:** Python
- **Libraries:** Standard Library Only
- **Interface:** Command Line (CLI)

---

**Team Name:** Decentralized

**Team Members:**
- Sholk Parikh – 240008027
- Yash Chaudhary – 240008038
- Mohd Hassan Raza Ansari – 240008019
- Dhyan Chandra – 240041014
