class UTXOManager:
    def __init__(self):
        self.utxo_set = {}

    def add_utxo(self, tx_id: str, index: int, amount: float, owner: str):
        self.utxo_set[(tx_id, index)] = {
            "amount": float(amount), 
            "owner": owner
        }

    def remove_utxo(self, tx_id: str, index: int):
        if (tx_id, index) in self.utxo_set:
            del self.utxo_set[(tx_id, index)]

    def get_balance(self, owner: str) -> float:
        balance = 0.0
        for utxo in self.utxo_set.values():
            if utxo["owner"] == owner:
                balance += utxo["amount"]
        return balance

    def exists(self, tx_id: str, index: int) -> bool:
        return (tx_id, index) in self.utxo_set

    def get_utxo(self, tx_id: str, index: int):
        return self.utxo_set.get((tx_id, index))

    def get_utxos_for_owner(self, owner: str) -> list:
        utxos = []
        for key, value in self.utxo_set.items():
            if value["owner"] == owner:
                utxos.append({
                    "tx_id": key[0],
                    "index": key[1],
                    "amount": value["amount"]
                })
        return utxos