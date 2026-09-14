"""Servicios orquestadores de la lógica de negocio del sistema."""

from typing import List, Tuple
from database import DatabaseManager
from modelos import Producto, Venta
from excepciones import (
    StockInsuficienteError,
    EntidadNoEncontradaError,
    ValidacionDatosError,
)


class VentaService:
    """Gestiona las transacciones y validaciones del proceso de venta."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        """Inicializa el servicio con el gestor de base de datos."""
        self._db = db_manager

    def registrar_venta(
        self, folio: str, cliente_id: str, items: List[Tuple[str, int]]
    ) -> Venta:
        """
        Procesa de forma atómica una venta deduciendo el stock respectivo.

        :param folio: Código identificador de la venta.
        :param cliente_id: Identificador del cliente comprador.
        :param items: Colección de tuplas con el formato (codigo_producto, unidades).
        :return: Instancia de la Venta generada.
        :raises ValidacionDatosError: Si faltan datos o el folio está repetido.
        :raises EntidadNoEncontradaError: Si no existe el cliente o algún producto.
        :raises StockInsuficienteError: Si no hay inventario suficiente.
        """
        if not items:
            raise ValidacionDatosError("La venta debe incluir al menos un producto.")

        with self._db.get_connection() as root:
            if folio in root["ventas"]:
                raise ValidacionDatosError(f"El folio '{folio}' ya se encuentra registrado.")

            cliente = root["clientes"].get(cliente_id)
            if not cliente:
                raise EntidadNoEncontradaError(f"Cliente con ID '{cliente_id}' no encontrado.")

            # Paso 1: Validar existencias sin alterar datos
            for cod_prod, cantidad in items:
                if cantidad <= 0:
                    raise ValidacionDatosError(f"La cantidad para '{cod_prod}' debe ser mayor a 0.")
                producto = root["productos"].get(cod_prod)
                if not producto:
                    raise EntidadNoEncontradaError(f"Producto '{cod_prod}' inexistente.")
                if producto.stock < cantidad:
                    raise StockInsuficienteError(
                        f"Stock insuficiente para '{producto.nombre}'. "
                        f"Disponible: {producto.stock}, Solicitado: {cantidad}"
                    )

            # Paso 2: Crear venta y descontar unidades
            venta = Venta(folio=folio, cliente=cliente)
            for cod_prod, cantidad in items:
                producto = root["productos"][cod_prod]
                producto.actualizar_stock(-cantidad)
                venta.agregar_detalle(producto, cantidad)

            root["ventas"][folio] = venta
            return venta


class InventarioService:
    """Gestiona el catálogo de productos y existencias."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        """Inicializa el servicio con el gestor de persistencia."""
        self._db = db_manager

    def registrar_producto(
        self, codigo: str, nombre: str, precio: float, stock: int
    ) -> Producto:
        """
        Valida y almacena un nuevo producto en el catálogo.

        :raises ValidacionDatosError: En caso de precios o existencias inválidas.
        """
        if not codigo or not nombre:
            raise ValidacionDatosError("El código y nombre del producto son obligatorios.")
        if precio <= 0:
            raise ValidacionDatosError("El precio debe ser un valor numérico positivo.")
        if stock < 0:
            raise ValidacionDatosError("El stock inicial no puede ser negativo.")

        with self._db.get_connection() as root:
            if codigo in root["productos"]:
                raise ValidacionDatosError(f"El producto con código '{codigo}' ya existe.")

            nuevo_producto = Producto(codigo=codigo, nombre=nombre, precio=precio, stock=stock)
            root["productos"][codigo] = nuevo_producto
            return nuevo_producto