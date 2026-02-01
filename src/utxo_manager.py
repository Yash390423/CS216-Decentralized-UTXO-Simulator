class UTXOManager:
    def __init__(self):
        self.utxo_set = {}
    def add_utxo(self, tx_id:str, index: int, amount: float, owner: str):
        self.utxo_set[(tx_id, index)] = {"amount": amount, "owner": owner} [cite:82,99]
    
    def remove_utxo(self, tx_id: str, index: int):
        if (tx_id, index) in self.utxo_set:
            del self.utxo_set([tx_id, index])
    
    def get_balance(self, owner: str) -> float:
        return sum(utxo['amount'] for utxo in self.utxo_set.values() if utxo['owner'] == owner)
    
    def exists(self, tx_id: str, index: int):
        return (tx_id, index) in self.utxo_set
    
    def get_utxo_owner(self, owner: str) -> list:
        return ((tx_id, indx, data['amount']) for (tx_id, idx), data in self.utxo_set.items() if data['owner'] = owner)
