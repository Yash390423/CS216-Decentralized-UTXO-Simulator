def validate_transaction(tx, utxo_manager, mempool) -> (bool, str, float):

    total_in = 0.0
    total_out = 0.0
    seen_inputs = set()

    for output in tx["outputs"]:
        if output["amount"] < 0:
            return False, "Invalid output amount (negative)", 0.0
        total_out += output["amount"]

    for inp in tx["inputs"]:
        prev_tx = inp["prev_tx"]
        idx = inp["index"]
        key = (prev_tx, idx)

        if key in seen_inputs:
            return False, f"Double-spend detected in transaction inputs: {key}", 0.0
        seen_inputs.add(key)

        if not utxo_manager.exists(prev_tx, idx):
            return False, f"Input {key} does not exist in UTXO set (or already spent)", 0.0
        
        utxo_data = utxo_manager.get_utxo(prev_tx, idx)
        if utxo_data["owner"] != inp["owner"]:
            return False, f"Signature mismatch: {inp['owner']} does not own {key}", 0.0
        if key in mempool.spent_utxos:
            return False, f"UTXO {key} is already spent in a pending transaction", 0.0

        total_in += utxo_data["amount"]

    if total_in < total_out:
        return False, f"Insufficient funds: Inputs ({total_in}) < Outputs ({total_out})", 0.0

    fee = total_in - total_out
    return True, "Valid", fee