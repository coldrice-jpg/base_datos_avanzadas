from datetime import datetime
from persistent import Persistent
from persistent.list import PersistentList


class Producto(Persistent):

    def __init__(self, codigo: str, nombre: str, precio: float, stock: int) -> None:
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def actualizar_stock(self, cantidad: int) -> None:
        if self.stock + cantidad < 0:
            raise ValueError("El stock no puede ser inferior a cero.")
        self.stock += cantidad
        self._p_changed = True


class Cliente(Persistent):

    def __init__(self, identificador: str, nombre: str, correo: str) -> None:
        self.identificador = identificador
        self.nombre = nombre
        self.correo = correo


class DetalleVenta(Persistent):

    def __init__(self, producto: Producto, cantidad: int, precio_unitario: float) -> None:
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    @property
    def subtotal(self) -> float:
        return self.cantidad * self.precio_unitario


class Venta(Persistent):

    def __init__(self, folio: str, cliente: Cliente) -> None:
        self.folio = folio
        self.cliente = cliente
        self.fecha = datetime.now()
        self.detalles = PersistentList()

    def agregar_detalle(self, producto: Producto, cantidad: int) -> None:
        detalle = DetalleVenta(producto, cantidad, producto.precio)
        self.detalles.append(detalle)
        self._p_changed = True

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.detalles)