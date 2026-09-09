# Ethereum audit anchoring

The portal seals a hash-chain record automatically whenever a government user creates a challenge, a startup submits a proposal, or a startup submits milestone evidence. The original data and files remain in the portal database and storage; only a SHA-256 fingerprint is suitable for an Ethereum network.

To anchor new record fingerprints on Ethereum:

1. Deploy `contracts/ProcurementAudit.sol` with a government-controlled wallet.
2. Install the project requirements, including `web3`.
3. Set `WEB3_RPC_URL`, `ETHEREUM_AUDIT_CONTRACT`, and `ETHEREUM_PRIVATE_KEY` in the deployment environment. Never commit the private key.
4. Restart the portal. New records will show `ETHEREUM_PENDING` along with their transaction hash.

Without these settings, the portal remains fully usable and records show `LOCAL_SEALED`: tamper-evident within its SQLite audit chain, but not published to a public blockchain.
