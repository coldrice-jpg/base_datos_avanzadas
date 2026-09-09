from persistent import Persistent
from datetime import datetime

class Proveedor(Persistent):
    def __init__(self, id_proveedor: str, nombre: str, contacto: str):
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.contacto = contacto

    def __repr__(self):
        return f"Proveedor({self.id_proveedor}, {self.nombre})"


class Producto(Persistent):
    def __init__(self, id_producto: str, nombre: str, precio: float, existencias: int, proveedor: Proveedor):
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = float(precio)
        self.existencias = int(existencias)
        self.proveedor = proveedor

    def incrementar_existencias(self, cantidad: int):
        if cantidad <= 0:
            raise ValueError("La cantidad a incrementar debe ser positiva.")
        self.existencias += cantidad

    def disminuir_existencias(self, cantidad: int):
        if cantidad <= 0:
            raise ValueError("La cantidad a descontar debe ser positiva.")
        if cantidad > self.existencias:
            raise ValueError(f"Existencias insuficientes para '{self.nombre}'. Disponibles: {self.existencias}.")
        self.existencias -= cantidad

    def __repr__(self):
        return f"Producto({self.id_producto}, '{self.nombre}', ${self.precio:.2f}, Stock: {self.existencias})"


class ItemVenta(Persistent):
    def __init__(self, producto: Producto, cantidad: int):
        self.producto = producto
        self.cantidad = int(cantidad)
        self.precio_unitario = producto.precio

    @property
    def subtotal(self) -> float:
        return self.precio_unitario * self.cantidad


class Venta(Persistent):
    def __init__(self, id_venta: str):
        self.id_venta = id_venta
        self.fecha = datetime.now()
        self.items = [] 

    def agregar_producto(self, producto: Producto, cantidad: int):
        producto.disminuir_existencias(cantidad)
        item = ItemVenta(producto, cantidad)
        self.items.append(item)
        self._p_changed = True

    def calcular_total(self) -> float:
        return sum(item.subtotal for item in self.items)

    def __repr__(self):
        return f"Venta({self.id_venta}, Fecha: {self.fecha.strftime('%Y-%m-%d %H:%M')}, Total: ${self.calcular_total():.2f})"