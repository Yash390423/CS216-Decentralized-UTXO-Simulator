from src.validator import validate_transaction

class Mempool:
    def __init__(self, max_size=50):
        self.transactions = []  
        self.spent_utxos = set()  
        self.max_size = max_size

    def add_transaction(self, tx, utxo_manager) -> (bool, str):
        """Validate and add transaction. Return (success, message)."""
        if len(self.transactions) >= self.max_size:
            return False, "Mempool is full"

        is_valid, msg, fee = validate_transaction(tx, utxo_manager, self)
        
        if is_valid:
            tx['fee'] = fee 
            self.transactions.append(tx)
            
            for inp in tx["inputs"]:
                self.spent_utxos.add((inp["prev_tx"], inp["index"]))
            return True, f"Transaction added. Fee: {fee:.5f} BTC"
        else:
            return False, msg

    def remove_transaction(self, tx_id: str):
        tx_to_remove = None
        for tx in self.transactions:
            if tx["tx_id"] == tx_id:
                tx_to_remove = tx
                break
        
        if tx_to_remove:
            self.transactions.remove(tx_to_remove)
            return True
        return False

    def get_top_transactions(self, n: int) -> list:
        """Return top N transactions by fee (highest first). [cite: 178]"""
        sorted_txs = sorted(self.transactions, key=lambda x: x.get('fee', 0), reverse=True)
        return sorted_txs[:n]

    def clear(self):
        """Clear all transactions."""
        self.transactions = []
        self.spent_utxos = set()