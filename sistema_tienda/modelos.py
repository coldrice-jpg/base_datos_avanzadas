"""Módulo de definición de entidades persistentes del dominio comercial."""

from datetime import datetime
from persistent import Persistent
from persistent.list import PersistentList
from excepciones import StockInsuficienteError


class Producto(Persistent):
    """Representa un producto en catálogo e inventario."""

    def __init__(self, codigo: str, nombre: str, precio: float, stock: int) -> None:
        """Inicializa los datos base del producto."""
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def actualizar_stock(self, cantidad: int) -> None:
        """
        Actualiza el stock sumando o restando unidades.

        :param cantidad: Unidades a ajustar (positivo o negativo).
        :raises StockInsuficienteError: Si el ajuste resulta en stock menor a cero.
        """
        if self.stock + cantidad < 0:
            raise StockInsuficienteError(
                f"Stock insuficiente para '{self.nombre}'. No es posible deducir {abs(cantidad)} unidades."
            )
        self.stock += cantidad
        self._p_changed = True


class Proveedor(Persistent):
    """Representa un proveedor del establecimiento."""

    def __init__(self, rfc: str, razon_social: str, telefono: str) -> None:
        """Inicializa los datos de contacto y fiscales del proveedor."""
        self.rfc = rfc
        self.razon_social = razon_social
        self.telefono = telefono


class Cliente(Persistent):
    """Representa un cliente registrado en la tienda."""

    def __init__(self, identificador: str, nombre: str, correo: str) -> None:
        """Inicializa los datos generales del cliente."""
        self.identificador = identificador
        self.nombre = nombre
        self.correo = correo


class DetalleVenta(Persistent):
    """Ítem unitario registrado en una transacción de venta."""

    def __init__(self, producto: Producto, cantidad: int, precio_unitario: float) -> None:
        """Inicializa la línea de venta con el precio congelado al momento."""
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    @property
    def subtotal(self) -> float:
        """Calcula el importe subtotal del ítem."""
        return self.cantidad * self.precio_unitario


class Venta(Persistent):
    """Representa una orden de compra concretada por un cliente."""

    def __init__(self, folio: str, cliente: Cliente) -> None:
        """Inicializa una venta vacía con fecha actual."""
        self.folio = folio
        self.cliente = cliente
        self.fecha = datetime.now()
        self.detalles = PersistentList()

    def agregar_detalle(self, producto: Producto, cantidad: int) -> None:
        """Agrega un producto vendido al listado de detalles."""
        detalle = DetalleVenta(producto, cantidad, producto.precio)
        self.detalles.append(detalle)
        self._p_changed = True

    @property
    def total(self) -> float:
        """Calcula el total sumando los subtotales de cada detalle."""
        return sum(item.subtotal for item in self.detalles)