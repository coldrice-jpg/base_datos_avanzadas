import ZODB
import ZODB.FileStorage
import transaction
from BTrees._OOBTree import OOBTree

class DatabaseManager:
    def __init__(self, db_filename: str = "inventario.fs"):
        self.db_filename = db_filename
        self.storage = None
        self.db = None
        self.connection = None
        self.root = None

    def open(self):
        self.storage = ZODB.FileStorage.FileStorage(self.db_filename)
        self.db = ZODB.DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()

        if "productos" not in self.root:
            self.root["productos"] = OOBTree()
        if "proveedores" not in self.root:
            self.root["proveedores"] = OOBTree()
        if "ventas" not in self.root:
            self.root["ventas"] = OOBTree()
            
        transaction.commit()

    def commit(self):
        transaction.commit()

    def abort(self):
        transaction.abort()

    def close(self):
        if self.connection is not None:
            self.connection.close()
        if self.db is not None:
            self.db.close()
        if self.storage is not None:
            self.storage.close()