import hashlib
import uuid
from dataclasses import dataclass, field


@dataclass
class RecordKeyGenerator(object):
    record: str
    hash: hashlib.blake2b.hexdigest = field(init=False)
    uid: uuid.uuid4 = field(init=False)
    __KEY_LENGTH = 16

    def generate_hash(self):
        _hasher = hashlib.blake2b(digest_size=RecordKeyGenerator.__KEY_LENGTH)
        _hasher.update(self.record.encode('utf-8'))
        self.hash = _hasher.hexdigest()
        return self.hash

    def generate_uuid(self):
        self.uid = uuid.uuid4()
        return self.uid

    def __post_init__(self):
        self.generate_hash()
        self.generate_uuid()
