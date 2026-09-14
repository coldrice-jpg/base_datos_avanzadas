from typing import List, Tuple
from database import DatabaseManager
from modelos import Venta
from excepciones import (
    StockInsuficienteError,
    EntidadNoEncontradaError,
    ValidacionDatosError,
)


class VentaService:
    """Orquesta las operaciones de venta y descuento de stock."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def registrar_venta(
        self, folio: str, cliente_id: str, items: List[Tuple[str, int]]
    ) -> Venta:
        """
        Registra una venta atómicamente.

        :param folio: Identificador único de la venta.
        :param cliente_id: Clave del cliente.
        :param items: Lista de tuplas (codigo_producto, cantidad).
        """
        if not items:
            raise ValidacionDatosError("La venta debe incluir al menos un producto.")

        with self._db.get_connection() as root:
            if folio in root["ventas"]:
                raise ValidacionDatosError(f"El folio {folio} ya se encuentra registrado.")

            cliente = root["clientes"].get(cliente_id)
            if not cliente:
                raise EntidadNoEncontradaError(f"Cliente con ID '{cliente_id}' no encontrado.")

            venta = Venta(folio=folio, cliente=cliente)

            # Validar stock previo a la aplicación de cambios
            for cod_prod, cantidad in items:
                producto = root["productos"].get(cod_prod)
                if not producto:
                    raise EntidadNoEncontradaError(f"Producto '{cod_prod}' inexistente.")
                if producto.stock < cantidad:
                    raise StockInsuficienteError(
                        f"Stock insuficiente para '{producto.nombre}'. "
                        f"Disponible: {producto.stock}, Solicitado: {cantidad}"
                    )

            # Aplicar deducciones de stock y ensamblar venta
            for cod_prod, cantidad in items:
                producto = root["productos"][cod_prod]
                producto.actualizar_stock(-cantidad)
                venta.agregar_detalle(producto, cantidad)

            root["ventas"][folio] = venta
            return venta