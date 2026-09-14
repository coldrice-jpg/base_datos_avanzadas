from database import DatabaseManager
from modelos import Producto, Venta
from excepciones import ValidacionDatosError
from typing import List, Tuple
from excepciones import (
    StockInsuficienteError,
    EntidadNoEncontradaError,
    ValidacionDatosError,
)


class VentaService:

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def registrar_venta(
        self, folio: str, cliente_id: str, items: List[Tuple[str, int]]
    ) -> Venta:
        if not items:
            raise ValidacionDatosError("La venta debe incluir al menos un producto.")

        with self._db.get_connection() as root:
            if folio in root["ventas"]:
                raise ValidacionDatosError(f"El folio {folio} ya se encuentra registrado.")

            cliente = root["clientes"].get(cliente_id)
            if not cliente:
                raise EntidadNoEncontradaError(f"Cliente con ID '{cliente_id}' no encontrado.")

            venta = Venta(folio=folio, cliente=cliente)

            for cod_prod, cantidad in items:
                producto = root["productos"].get(cod_prod)
                if not producto:
                    raise EntidadNoEncontradaError(f"Producto '{cod_prod}' inexistente.")
                if producto.stock < cantidad:
                    raise StockInsuficienteError(
                        f"Stock insuficiente para '{producto.nombre}'. "
                        f"Disponible: {producto.stock}, Solicitado: {cantidad}"
                    )

            for cod_prod, cantidad in items:
                producto = root["productos"][cod_prod]
                producto.actualizar_stock(-cantidad)
                venta.agregar_detalle(producto, cantidad)

            root["ventas"][folio] = venta
            return venta

class InventarioService:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def registrar_producto(self, codigo: str, nombre: str, precio: float, stock: int) -> Producto:
        if precio <= 0:
            raise ValidacionDatosError("El precio debe ser un valor positivo.")
        if stock < 0:
            raise ValidacionDatosError("El stock inicial no puede ser negativo.")

        with self._db.get_connection() as root:
            if codigo in root["productos"]:
                raise ValidacionDatosError(f"El producto con código '{codigo}' ya existe.")

            nuevo_producto = Producto(codigo=codigo, nombre=nombre, precio=precio, stock=stock)
            root["productos"][codigo] = nuevo_producto
            return nuevo_producto