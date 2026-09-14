"""Módulo de persistencia y ciclo de vida de conexión con ZODB."""

from contextlib import contextmanager
from typing import Generator
import transaction
from ZODB import FileStorage, DB
from BTrees import OOBTree


class DatabaseManager:
    """Administrador centralizado de la conexión y transacciones con ZODB."""

    def __init__(self, filepath: str = "data/tienda.fs") -> None:
        """Configura la ruta del archivo de almacenamiento."""
        self._filepath = filepath
        self._storage = None
        self._db = None

    def initialize(self) -> None:
        """Abre la base de datos e inicializa los árboles solo si no existen."""
        self._storage = FileStorage.FileStorage(self._filepath)
        self._db = DB(self._storage)

        with self.get_connection() as root:
            if "productos" not in root:
                root["productos"] = OOBTree.OOBTree()
            if "clientes" not in root:
                root["clientes"] = OOBTree.OOBTree()
            if "proveedores" not in root:
                root["proveedores"] = OOBTree.OOBTree()
            if "ventas" not in root:
                root["ventas"] = OOBTree.OOBTree()

    @contextmanager
    def get_connection(self) -> Generator[OOBTree.OOBTree, None, None]:
        """
        Context manager transaccional. Aplica commit automáticamente al salir
        o abort si ocurre un error no controlado.
        """
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
        """Cierra ordenadamente el pool de conexiones y el almacenamiento."""
        if self._db:
            self._db.close()
        if self._storage:
            self._storage.close()