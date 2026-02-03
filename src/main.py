import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utxo_manager import UTXOManager
from src.mempool import Mempool
from src.block import mine_block
from src.transaction import generate_tx_id, create_transaction_struct
from tests.test_scenarios import run_test_scenarios

def initialize_genesis(utxo_mgr):
    """Sets up the initial state as defined in Section 5.1[cite: 269]."""
    utxo_mgr.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_mgr.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_mgr.add_utxo("genesis", 2, 20.0, "Charlie")
    utxo_mgr.add_utxo("genesis", 3, 10.0, "David")
    utxo_mgr.add_utxo("genesis", 4, 5.0, "Eve")

def main():
    utxo_mgr = UTXOManager()
    mempool = Mempool()
    initialize_genesis(utxo_mgr)
    print("\n=== Bitcoin Transaction Simulator ===")
    print("Initial UTXOs (Genesis Block):")
    print(f"Alice:   {utxo_mgr.get_balance('Alice')} BTC")
    print(f"Bob:     {utxo_mgr.get_balance('Bob')} BTC")
    print(f"Charlie: {utxo_mgr.get_balance('Charlie')} BTC")
    print(f"David:   {utxo_mgr.get_balance('David')} BTC")
    print(f"Eve:     {utxo_mgr.get_balance('Eve')} BTC")
    while True:
        print("\n=======================")
        print(f"Current Confirmed UTXOs (Mempool: {len(mempool.transactions)} pending):")
        print(f"Alice:   {utxo_mgr.get_balance('Alice'):.4f} BTC")
        print(f"Bob:     {utxo_mgr.get_balance('Bob'):.4f} BTC")
        print(f"Charlie: {utxo_mgr.get_balance('Charlie'):.4f} BTC")
        print(f"David:   {utxo_mgr.get_balance('David'):.4f} BTC")
        print(f"Eve:     {utxo_mgr.get_balance('Eve'):.4f} BTC")
        
        print("\nMain Menu:")
        print("1. Create new transaction")
        print("2. View UTXO set")
        print("3. View mempool")
        print("4. Mine block")
        print("5. Run test scenarios")
        print("6. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            sender = input("Enter sender: ")
            print(f"Available balance: {utxo_mgr.get_balance(sender)}")
            
            recipient = input("Enter recipient: ")
            try:
                amount = float(input("Enter amount: "))
            except ValueError:
                print("Invalid amount.")
                continue

            user_utxos = utxo_mgr.get_utxos_for_owner(sender)
            inputs = []
            input_sum = 0.0
            
            for u in user_utxos:
                inputs.append({
                    "prev_tx": u["tx_id"], 
                    "index": u["index"], 
                    "owner": sender
                })
                input_sum += u["amount"]
                if input_sum >= amount:
                    break
            
            if input_sum < amount:
                print("Error: Insufficient funds available (confirmed).")
                continue

            outputs = [{"amount": amount, "address": recipient}]
            
            fee_rate = 0.001
            change = input_sum - amount - fee_rate
            
            if change >= 0:
                outputs.append({"amount": change, "address": sender})
            elif change < 0:
                print("Error: Not enough funds to cover fee.")
                continue

            print("Creating transaction...")
            tx = create_transaction_struct(generate_tx_id(), inputs, outputs)
            
            success, msg = mempool.add_transaction(tx, utxo_mgr)
            if success:
                print(f"Transaction valid! Fee: {fee_rate:.4f} BTC")
                print(f"Transaction ID: {tx['tx_id']}")
                print("Transaction added to mempool.")
            else:
                print(f"Transaction Rejected: {msg}")

        elif choice == '2':
            print("\n--- Current UTXO Set ---")
            for key, val in utxo_mgr.utxo_set.items():
                print(f"{key}: {val['amount']} BTC ({val['owner']})")

        elif choice == '3':
            print(f"\n--- Mempool ({len(mempool.transactions)} txs) ---")
            for tx in mempool.transactions:
                print(f"ID: {tx['tx_id']} | Fee: {tx.get('fee', 0):.5f} | Inputs: {len(tx['inputs'])}")

        elif choice == '4':
            miner = input("Enter miner name: ")
            mine_block(miner, mempool, utxo_mgr)

        elif choice == '5':
            run_test_scenarios(utxo_mgr, mempool)

        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()