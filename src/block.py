import time
import random

def generate_tx_id():
    return f"tx_{int(time.time())}_{random.randint(1000, 9999)}"

def mine_block(miner_address: str, mempool, utxo_manager, num_txs = 5):
    selected_txs = mempool.get_top_transactions(num_txs)
    if not selected_txs:
        return "No transactions to mine."
    total_fees = 0
    for tx in selected_txs:
        for inp in tx['inputs']:
            utxo_manager.remove_utxo(inp['prev_tx'], inp['index'])
        
        for idx, out in enumerate(tx['outputs']):
            utxo_manager.add_utxo(tx['tx_id'], idx, out['amount'], out['address'])

        total_fees += tx['fee']
    
    reward_id = f'reward_{int(time.time())}'
    utxo_manager.add_utxo(reward_id, 0, total_fees, miner_address)

    mempool.clear(selected_txs)