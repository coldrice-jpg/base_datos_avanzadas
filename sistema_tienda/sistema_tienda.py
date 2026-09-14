"""Punto de entrada principal para la gestión de la tienda."""

import os
import sys

from database import DatabaseManager
from servicios import InventarioService, VentaService
from consultas import InventarioQueries
from excepciones import TiendaError


DB_PATH = os.path.join("data", "tienda.fs")
UMBRAL_STOCK_BAJO = 5


def inicializar_datos_prueba(
    inventario_service: InventarioService, db_manager: DatabaseManager
) -> None:
    """Registra datos iniciales de catálogo y clientes para pruebas si la BD está vacía."""
    with db_manager.get_connection() as root:
        if not root["productos"]:
            inventario_service.registrar_producto("P001", "Laptop Pro 14", 18500.00, 8)
            inventario_service.registrar_producto("P002", "Mouse Inalámbrico", 450.00, 3)
            inventario_service.registrar_producto("P003", "Teclado Mecánico", 1200.00, 15)

        if not root["clientes"]:
            from modelos import Cliente
            root["clientes"]["C001"] = Cliente("C001", "Ana Martínez", "ana@example.com")
            root["clientes"]["C002"] = Cliente("C002", "Carlos Gómez", "carlos@example.com")


def main() -> None:
    """Ejecuta el ciclo principal y demuestra el flujo de la aplicación."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db_manager = DatabaseManager(filepath=DB_PATH)
    db_manager.initialize()

    try:
        inventario_service = InventarioService(db_manager)
        venta_service = VentaService(db_manager)
        inventario_queries = InventarioQueries(db_manager)

        inicializar_datos_prueba(inventario_service, db_manager)

        print("=== ESTADO INICIAL DEL INVENTARIO ===")
        for prod in inventario_queries.productos_disponibles():
            print(f"- [{prod.codigo}] {prod.nombre} | Stock: {prod.stock} | Precio: ${prod.precio:,.2f}")

        print("\n=== REGISTRANDO VENTA ===")
        folio_venta = "V-1001"
        items_a_comprar = [
            ("P001", 1),
            ("P002", 2),
        ]

        venta = venta_service.registrar_venta(
            folio=folio_venta,
            cliente_id="C001",
            items=items_a_comprar
        )

        print(f"Venta '{venta.folio}' completada a nombre de: {venta.cliente.nombre}")
        for detalle in venta.detalles:
            print(f"  * {detalle.cantidad}x {detalle.producto.nombre} -> Subtotal: ${detalle.subtotal:,.2f}")
        print(f"TOTAL: ${venta.total:,.2f}")

        print("\n=== PRODUCTOS CON BAJO STOCK (Alerta <= 5) ===")
        for prod in inventario_queries.productos_bajo_stock(umbral=UMBRAL_STOCK_BAJO):
            print(f"! [ALERTA] {prod.nombre}: solo quedan {prod.stock} unidades")

        print("\n=== REPORTE: PRODUCTOS MÁS VENDIDOS ===")
        for nombre, cant in inventario_queries.productos_mas_vendidos():
            print(f"- {nombre}: {cant} piezas vendidas")

    except TiendaError as error_dominio:
        print(f"\n[Error de Operación]: {error_dominio}", file=sys.stderr)
    except Exception as error_inesperado:
        print(f"\n[Error Crítico Inesperado]: {error_inesperado}", file=sys.stderr)
    finally:
        db_manager.close()
        print("\nConexión a ZODB cerrada correctamente.")


if __name__ == "__main__":
    main()