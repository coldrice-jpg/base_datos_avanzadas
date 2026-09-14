"""Consultas de sólo lectura y generación de reportes sobre ZODB."""

from typing import List, Tuple
from collections import Counter
from database import DatabaseManager
from modelos import Producto, Venta


class InventarioQueries:
    """Módulo de consultas de inventario y análisis de ventas."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        """Inicializa el módulo de consultas."""
        self._db = db_manager

    def productos_disponibles(self) -> List[Producto]:
        """Obtiene la lista de productos que cuentan con stock positivo."""
        with self._db.get_connection() as root:
            return [p for p in root["productos"].values() if p.stock > 0]

    def productos_bajo_stock(self, umbral: int = 5) -> List[Producto]:
        """Obtiene productos con unidades menores o iguales al umbral dado."""
        with self._db.get_connection() as root:
            return [p for p in root["productos"].values() if p.stock <= umbral]

    def ventas_cliente(self, cliente_id: str) -> List[Venta]:
        """
        Consulta el historial de órdenes pertenecientes a un cliente.

        :param cliente_id: Clave identificadora del cliente.
        :return: Lista de ventas registradas para el cliente.
        """
        with self._db.get_connection() as root:
            return [
                v for v in root["ventas"].values()
                if v.cliente.identificador == cliente_id
            ]

    def productos_mas_vendidos(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        Determina los productos con mayor demanda por total de unidades vendidas.

        :param top_n: Límite de productos a retornar.
        :return: Lista de tuplas con el nombre del producto y la suma de unidades vendidas.
        """
        conteo: Counter = Counter()
        with self._db.get_connection() as root:
            for venta in root["ventas"].values():
                for detalle in venta.detalles:
                    conteo[detalle.producto.nombre] += detalle.cantidad

        return conteo.most_common(top_n)