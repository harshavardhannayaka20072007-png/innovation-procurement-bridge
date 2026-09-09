"""Tamper-evident audit records with an optional Ethereum anchor."""
import hashlib
import json
import os
from datetime import datetime, timezone

from backend.db import execute_db, query_db


def _ethereum_anchor(record_hash):
    """Anchor a digest only when a deployment has been configured by an operator."""
    rpc_url = os.environ.get('WEB3_RPC_URL')
    contract_address = os.environ.get('ETHEREUM_AUDIT_CONTRACT')
    private_key = os.environ.get('ETHEREUM_PRIVATE_KEY')
    if not all((rpc_url, contract_address, private_key)):
        return 'LOCAL_SEALED', None

    try:
        from web3 import Web3
        from eth_account import Account

        web3 = Web3(Web3.HTTPProvider(rpc_url))
        account = Account.from_key(private_key)
        contract = web3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=[{
                'inputs': [{'internalType': 'bytes32', 'name': 'recordHash', 'type': 'bytes32'}],
                'name': 'anchorRecord', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'
            }]
        )
        transaction = contract.functions.anchorRecord(bytes.fromhex(record_hash)).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'chainId': web3.eth.chain_id,
            'gas': 100000,
            'gasPrice': web3.eth.gas_price,
        })
        signed = account.sign_transaction(transaction)
        transaction_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        return 'ETHEREUM_PENDING', transaction_hash.hex()
    except Exception:
        # A local sealed record remains verifiable even if the external anchor is unavailable.
        return 'LOCAL_SEALED', None


def record_event(event_type, entity_type, entity_id, actor, payload):
    """Append an immutable, hash-chained record for a sensitive procurement action."""
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    previous = query_db('SELECT record_hash FROM audit_records ORDER BY record_id DESC LIMIT 1', one=True)
    previous_hash = previous['record_hash'] if previous else 'GENESIS'
    created_at = datetime.now(timezone.utc).isoformat()
    fingerprint = '|'.join((previous_hash, event_type, entity_type, str(entity_id), str(actor.get('user_id')), created_at, payload_json))
    record_hash = hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()
    anchor_status, transaction_hash = _ethereum_anchor(record_hash)

    return execute_db(
        '''INSERT INTO audit_records
           (event_type, entity_type, entity_id, actor_id, actor_name, actor_role, payload, previous_hash, record_hash, anchor_status, transaction_hash, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (event_type, entity_type, entity_id, actor.get('user_id'), actor.get('username'), actor.get('role'),
         payload_json, previous_hash, record_hash, anchor_status, transaction_hash, created_at)
    )
