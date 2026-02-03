import sys
import os



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utxo_manager import UTXOManager
from src.mempool import Mempool
from src.block import mine_block
from src.transaction import generate_tx_id, create_transaction_struct

def create_test_tx(utxo_mgr, sender, recipient, amount, fee):
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
        if input_sum >= amount + fee:
            break
            
    if input_sum < amount + fee:
        return None 
        
    outputs = [{"amount": amount, "address": recipient}]
    change = input_sum - amount - fee
    
    if change > 0.000001:
        outputs.append({"amount": change, "address": sender})
        
    tx_id = generate_tx_id()
    return create_transaction_struct(tx_id, inputs, outputs)

def initialize_genesis_for_test(utxo_mgr):
    utxo_mgr.utxo_set = {} 
    utxo_mgr.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_mgr.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_mgr.add_utxo("genesis", 2, 20.0, "Charlie")


def test_1_basic_valid_transaction():
    print("Test: Verify simple Alice -> Bob transaction")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    
    tx = create_test_tx(um, "Alice", "Bob", 10.0)
    success, msg = mp.add_transaction(tx, um)
    
    if success is True and len(mp.transactions) == 1:
        print("Result: Transaction Accepted (VALID)")
        print("Status: [PASS]")
    else:
        print(f"Result: Transaction Rejected. Message: {msg}")
        print("Status: [FAIL]")

def test_2_multiple_inputs():
    print("Test: Verify aggregation of multiple inputs (50 + 20 BTC)")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    
    um.add_utxo("extra_funding", 0, 20.0, "Alice")
    
    tx = create_test_tx(um, "Alice", "Bob", 60.0)
    success, msg = mp.add_transaction(tx, um)
    
    if success is True and len(tx['inputs']) >= 2:
        print(f"Result: Transaction Accepted with {len(tx['inputs'])} inputs.")
        print("Status: [PASS]")
    else:
        print(f"Result: FAILED. Success={success}, Inputs={len(tx['inputs'])}")
        print(f"Message: {msg}")
        print("Status: [FAIL]")

def test_3_double_spend_same_tx():
    print("Test: Alice tries to spend same UTXO twice in ONE transaction")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    
    u = um.get_utxos_for_owner("Alice")[0]
    inp = {"prev_tx": u["tx_id"], "index": u["index"], "owner": "Alice"}
    

    tx = create_transaction_struct(
        generate_tx_id(),
        [inp, inp], 
        [{"amount": 10.0, "address": "Bob"}]
    )
    
    success, msg = mp.add_transaction(tx, um)
    

    if success is False:
        print(f"Result: REJECTED as expected - {msg}")
        print("Status: [PASS]")
    else:
        print("Result: Transaction was wrongly ACCEPTED!")
        print("Status: [FAIL]")
    

def test_4_mempool_conflict():
    print("Test: Attempt to spend a UTXO that is already locked in Mempool")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    
    tx1 = create_test_tx(um, "Alice", "Bob", 10.0)
    mp.add_transaction(tx1, um)
    print("TX1: Alice -> Bob (10 BTC) - IN MEMPOOL")

    tx2 = create_test_tx(um, "Alice", "Charlie", 10.0)
    print("TX2: Alice -> Charlie (Same UTXO) - ATTEMPTING...")
    
    success, msg = mp.add_transaction(tx2, um)
    
    if success is False:
        print(f"Result: REJECTED as expected - {msg}")
        print("Status: [PASS]")
    else:
        print("Result: Double-spend was wrongly ACCEPTED!")
        print("Status: [FAIL]")

def test_5_insufficient_funds():
    print("Test: Bob tries to spend 35 BTC but only has 30 BTC")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    
    tx = create_test_tx(um, "Bob", "Alice", 35.0)
    
    if tx is None:
        print("Result: REJECTED (Insufficient Funds)")
        print("Status: [PASS]")
    else:
        print("Result: Transaction created despite insufficient funds.")
        print("Status: [FAIL]")

def test_6_negative_amount():
    print("Test: Transaction with negative output amount")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    
    u = um.get_utxos_for_owner("Alice")[0]
    tx = create_transaction_struct(
        generate_tx_id(),
        [{"prev_tx": u["tx_id"], "index": u["index"], "owner": "Alice"}],
        [{"amount": -5.0, "address": "Bob"}]
    )
    
    success, msg = mp.add_transaction(tx, um)
    
    if success is False:
        print(f"Result: REJECTED - {msg}")
        print("Status: [PASS]")
    else:
        print("Result: Negative amount transaction was WRONGLY ACCEPTED")
        print("Status: [FAIL]")

def test_7_zero_fee():
    print("Test: Transaction with 0 fee (Inputs == Outputs)")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    u = um.get_utxos_for_owner("Alice")[0]
    tx = create_transaction_struct(
        generate_tx_id(),
        [{"prev_tx": u["tx_id"], "index": u["index"], "owner": "Alice"}],
        [{"amount": 50.0, "address": "Bob"}]
    )
    
    success, msg = mp.add_transaction(tx, um)
    
    if success is True:
        print("Result: Zero Fee Transaction Accepted (VALID)")
        print("Status: [PASS]")
    else:
        print(f"Result: Rejected. Msg: {msg}")
        print("Status: [FAIL]")

def test_8_race_attack():
    print("Test: Race Attack (First-Seen Rule)")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    
    tx1 = create_test_tx(um, "Alice", "Bob", 10.0, fee=0.001)
    tx2 = create_test_tx(um, "Alice", "Charlie", 10.0, fee=0.005) 
    
    print("1. Low-fee merchant TX (Fee: 0.001) arrives first...")
    success1, _ = mp.add_transaction(tx1, um)
    
    print("2. High-fee attack TX (Fee: 0.005) arrives second...")
    success2, msg2 = mp.add_transaction(tx2, um)
    
    if success1 is True and success2 is False:
        print(f"Result: High-fee attack REJECTED as expected.")
        print(f"Reason: {msg2}")
        print("Status: [PASS]")
    else:
        print(f"Result: Failed. TX1_Accepted={success1}, TX2_Accepted={success2}")
        print("Status: [FAIL]")

def test_9_mining_flow():
    print("Test: Mining clears mempool and updates UTXOs")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    
    tx = create_test_tx(um, "Alice", "Bob", 10.0)
    mp.add_transaction(tx, um)
    
    start_bal = um.get_balance("Bob")
    print(f"Bob Start Balance: {start_bal}")
    
    mine_block("Miner1", mp, um)
    
    end_bal = um.get_balance("Bob")
    print(f"Bob End Balance: {end_bal} (Confirmed!)")
    if len(mp.transactions) == 0 and end_bal > start_bal:
        print("Result: Mempool empty, Balance updated.")
        print("Status: [PASS]")
    else:
        print(f"Result: Mining check failed. Mempool Count={len(mp.transactions)}, Balance Diff={end_bal - start_bal}")
        print("Status: [FAIL]")

def test_10_unconfirmed_chain():
    print("Test: Spending an unconfirmed UTXO (Chaining)")
    um = UTXOManager()
    initialize_genesis_for_test(um)
    mp = Mempool()
    
    tx1 = create_test_tx(um, "Alice", "Bob", 10.0)
    mp.add_transaction(tx1, um)
    print("TX1: Alice -> Bob (In Mempool, not mined yet)")
    
    inp = {"prev_tx": tx1['tx_id'], "index": 0, "owner": "Bob"}
    
    tx2 = create_transaction_struct(
        generate_tx_id(),
        [inp],
        [{"amount": 5.0, "address": "Charlie"}]
    )
    
    print("TX2: Bob -> Charlie (Using unconfirmed output from TX1)")
    success, msg = mp.add_transaction(tx2, um)
    
    if success is False:
        print(f"Result: REJECTED as expected - {msg}")
        print("Status: [PASS]")
    else:
        print("Result: Unconfirmed chain was wrongly ACCEPTED!")
        print("Status: [FAIL]")



def run_test_scenarios(utxo_mgr, mempool):
    
    tests = {
        1: ("Basic Valid Transaction", test_1_basic_valid_transaction),
        2: ("Multiple Inputs", test_2_multiple_inputs),
        3: ("Double-Spend (Same Tx)", test_3_double_spend_same_tx),
        4: ("Mempool Conflict", test_4_mempool_conflict),
        5: ("Insufficient Funds", test_5_insufficient_funds),
        6: ("Negative Amount", test_6_negative_amount),
        7: ("Zero Fee", test_7_zero_fee),
        8: ("Race Attack", test_8_race_attack),
        9: ("Mining Flow", test_9_mining_flow),
        10: ("Unconfirmed Chain", test_10_unconfirmed_chain)
    }

    print("\n Select Test Scenario ")
    for num, (name, _) in tests.items():
        print(f"{num}. {name}")
    
    try:
        choice = int(input("\nEnter test number (1-10): "))
        if choice in tests:
            name, func = tests[choice]
            print(f"\n--- Running Test {choice}: {name} ---")
            try:
                func()
                print("\n[PASS] Test Completed Successfully.")
            except AssertionError as e:
                print(f"\n[FAIL] Test Failed: {e}")
            except Exception as e:
                print(f"\n[ERROR] Exception: {e}")
        else:
            print("Invalid test number.")
    except ValueError:
        print("Invalid input. Please enter a number.")
