import time
import random

def generate_tx_id():
    """Generate unique transaction ids"""
    return f"tx_{int(time.time())}_{random.randint(1000, 9999)}"

def create_transaction_struct(tx_id, inputs, outputs):
    return {
        "tx_id": tx_id,
        "inputs": inputs,
        "outputs": outputs
    }