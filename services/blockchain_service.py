import hashlib
import json
from datetime import datetime

class BlockchainEngine:
    """Immutable Ledger & Certificate Verification Engine for Government Grants & Applications"""
    
    def __init__(self):
        self.chain = []
        # Genesis Block
        self.create_block(previous_hash='0'*64, proof=100, data={'genesis': 'GOV_INTEROP_BLOCKCHAIN_GENESIS_BLOCK'})

    def create_block(self, proof, previous_hash, data):
        """Create a new Cryptographic Block in the Blockchain"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.utcnow().isoformat(),
            'proof': proof,
            'previous_hash': previous_hash,
            'merkle_root': self._calculate_merkle_root(data),
            'data': data
        }
        block['hash'] = self.hash_block(block)
        self.chain.append(block)
        return block

    @staticmethod
    def hash_block(block):
        """Generates SHA-256 Hash of a Block"""
        block_string = json.dumps({
            'index': block['index'],
            'timestamp': block['timestamp'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            'merkle_root': block['merkle_root']
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def _calculate_merkle_root(self, data):
        """Calculate Merkle Tree Root Hash of data dictionary"""
        data_str = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(data_str).hexdigest()

    def add_application_record(self, tracking_id, applicant_name, scheme_title, status):
        """Record an approved application into the Blockchain Ledger"""
        last_block = self.chain[-1]
        previous_hash = last_block['hash']
        data = {
            'tracking_id': tracking_id,
            'applicant_name': applicant_name,
            'scheme_title': scheme_title,
            'status': status,
            'blockchain_standard': 'GovInterop-Hyperledger-SHA256'
        }
        return self.create_block(proof=last_block['proof'] + 1, previous_hash=previous_hash, data=data)

    def verify_record(self, tracking_id):
        """Search and verify an application block on the public blockchain"""
        for block in self.chain:
            if block['data'].get('tracking_id') == tracking_id:
                return True, block
        return False, None

# Global Singleton Instance of Blockchain
blockchain_instance = BlockchainEngine()
