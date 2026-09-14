from typing import List
from database import DatabaseManager
from modelos import Producto


class InventarioQueries:

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def productos_disponibles(self) -> List[Producto]:
        with self._db.get_connection() as root:
            return [p for p in root["productos"].values() if p.stock > 0]

    def productos_bajo_stock(self, umbral: int = 5) -> List[Producto]:
        with self._db.get_connection() as root:
            return [p for p in root["productos"].values() if p.stock <= umbral]