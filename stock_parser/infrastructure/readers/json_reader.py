import json
from core.ports.reader_interface import ReaderInterface

class JSONReader(ReaderInterface):
    def read(self, path: str):
        with open(path, "r") as f:
            return json.load(f)
