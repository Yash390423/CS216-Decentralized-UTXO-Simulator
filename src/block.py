import time
from src.utxo_manager import UTXOManager
from src.mempool import Mempool

def mine_block(miner_address: str, mempool: Mempool, utxo_manager: UTXOManager, num_txs=3):

    selected_txs = mempool.get_top_transactions(num_txs)
    
    if not selected_txs:
        print("No transactions to mine.")
        return

    total_fees = 0.0
    print(f"Mining block with {len(selected_txs)} transactions...")

    for tx in selected_txs:
        for inp in tx["inputs"]:
            utxo_manager.remove_utxo(inp["prev_tx"], inp["index"])

            if (inp["prev_tx"], inp["index"]) in mempool.spent_utxos:
                mempool.spent_utxos.remove((inp["prev_tx"], inp["index"]))

        for i, output in enumerate(tx["outputs"]):
            utxo_manager.add_utxo(tx["tx_id"], i, output["amount"], output["address"])

        total_fees += tx.get('fee', 0)
        
        mempool.remove_transaction(tx["tx_id"])

    if total_fees > 0:
        coinbase_tx_id = f"coinbase_{int(time.time())}"
        utxo_manager.add_utxo(coinbase_tx_id, 0, total_fees, miner_address)
        print(f"Miner {miner_address} receives {total_fees:.5f} BTC reward.")
    
    print("Block mined successfully!")