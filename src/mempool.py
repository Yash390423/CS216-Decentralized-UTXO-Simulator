from validator import validate_transaction

class Mempool:
    def __init__(self, max_size = 50):
        self.transactions = []
        self.spent_utxos = set()
        self.max_size = max_size

    def add_transaction(self, tx, utxo_manager):
        if len(self.transactions) >= self.max_size:
            self.transactions.sort(key = lambda x: x.get('fee', 0 ))
            removed = self.transactions.pop(0)
            for inp in removed['inputs']:
                self.spent_utxos.remove((inp['prev_tx'], inp['index']))

        is_valid, result = validate_transaction(tx, utxo_manager, self.spent_utxos)
        if is_valid:
            tx['fee'] = result
            self.transactions.append(tx)
            for inp in tx['inputs']:
                self.spent_utxos.add((inp['prev_tc'], inp['index']))
            return True, f"Transaction added. Fee: {tx['fee']}"
        return False, result

    def remove_transaction(self, tx_id) -> (bool, str):
        for tx in self.transactions:
            if tx['tx_id'] == tx_id:
                for inp in tx['inputs']:
                    utxo_key = (inp['prev_tx'], inp['index'])
                    if utxo_key in self.spent_utxos:
                        self.spent_utxos.remove(utxo_key)

                self.transactions.remove(tx)
                return True, f"Transaction {tx_id} removed"
        return False, "Transaction not found."
    
    def get_top_transactions(self, n: int) -> list:
        sorted_txs = sorted(self.transactions, key = lambda x: x.get('fee', 0), reverse = True)
        return sorted_txs[:n]

    def clear(self):
        self.transactions = []
        self.spent_utxos = set()