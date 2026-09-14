from contextlib import contextmanager
from typing import Generator
import transaction
from ZODB import FileStorage, DB
from BTrees._OOBTree import OOBTree


class DatabaseManager:

    def __init__(self, filepath: str = "data/tienda.fs") -> None:
        self._filepath = filepath
        self._storage = None
        self._db = None

    def initialize(self) -> None:
        self._storage = FileStorage.FileStorage(self._filepath)
        self._db = DB(self._storage)

        with self.get_connection() as root:
            if "productos" not in root:
                root["productos"] = OOBTree()
            if "clientes" not in root:
                root["clientes"] = OOBTree()
            if "ventas" not in root:
                root["ventas"] = OOBTree()
            transaction.commit()

    @contextmanager
    def get_connection(self) -> Generator[OOBTree, None, None]:
        connection = self._db.open()
        try:
            root = connection.root()
            yield root
            transaction.commit()
        except Exception:
            transaction.abort()
            raise
        finally:
            connection.close()

    def close(self) -> None:
        if self._db:
            self._db.close()
        if self._storage:
            self._storage.close()