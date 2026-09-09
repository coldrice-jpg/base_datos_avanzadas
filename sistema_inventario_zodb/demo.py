import os
from database import DatabaseManager
from models import Proveedor, Producto, Venta

DB_FILE = "inventario.fs"

def limpiar_bd():
    for ext in ["", ".index", ".lock", ".tmp", ".old"]:
        if os.path.exists(DB_FILE + ext):
            os.remove(DB_FILE + ext)

def sesion_1():
    print("=" * 60)
    print("SESIÓN 1: Creación, Operaciones de Negocio y Guardado en ZODB")
    print("=" * 60)
    
    db = DatabaseManager(DB_FILE)
    db.open()
    root = db.root

    # 1. ALTA DE PROVEEDORES Y PRODUCTOS
    prov1 = Proveedor("PRV-01", "TechDistro Corp", "contacto@techdistro.com")
    prov2 = Proveedor("PRV-02", "Papelería Central", "ventas@central.com")
    root["proveedores"][prov1.id_proveedor] = prov1
    root["proveedores"][prov2.id_proveedor] = prov2

    p1 = Producto("PROD-01", "Monitor 27''", 4500.0, 10, prov1)
    p2 = Producto("PROD-02", "Teclado Mecánico", 1200.0, 15, prov1)
    p3 = Producto("PROD-03", "Mouse Inalámbrico", 450.0, 3, prov1)
    p4 = Producto("PROD-04", "Cuaderno Profesional", 85.0, 50, prov2)
    p5 = Producto("PROD-05", "Pluma Fuente", 620.0, 4, prov2)

    for p in [p1, p2, p3, p4, p5]:
        root["productos"][p.id_producto] = p

    # 2. OPERACIONES DE NEGOCIO: Venta, stock y cálculo de total
    print("\n-> Registrando Venta V-001...")
    venta1 = Venta("V-001")
    venta1.agregar_producto(p1, 2)  # Disminuye stock de Monitor a 8
    venta1.agregar_producto(p2, 1)  # Disminuye stock de Teclado a 14
    root["ventas"][venta1.id_venta] = venta1

    # Operación de negocio: Incrementar existencias
    print("-> Incrementando existencias de Cuadernos (+20)...")
    p4.incrementar_existencias(20)

    # Commit y Cierre
    print("\nEjecutando transaction.commit()...")
    db.commit()
    print("Cerrando la base de datos ZODB...")
    db.close()
    print("Sesión 1 terminada exitosamente.")


def sesion_2():
    print("\n" + "=" * 60)
    print("SESIÓN 2: Reapertura, CRUD y Verificación de Persistencia")
    print("=" * 60)
    
    db = DatabaseManager(DB_FILE)
    db.open()
    root = db.root

    # 3. VERIFICACIÓN DE PERSISTENCIA Y CONSULTA
    print("\n[VERIFICACIÓN] Recuperando productos tras reiniciar aplicación:")
    for prod in root["productos"].values():
        print(f"  * {prod.nombre} | Precio: ${prod.precio} | Existencias: {prod.existencias} | Proveedor: {prod.proveedor.nombre}")

    # 4. MODIFICACIÓN DE OBJETO (UPDATE)
    print("\n[MODIFICACIÓN] Modificando precio del 'Teclado Mecánico'...")
    teclado = root["productos"]["PROD-02"]
    teclado.precio = 1350.0  # Persistent rastrea este cambio de atributo
    db.commit()
    print(f"  * Nuevo precio registrado: ${root['productos']['PROD-02'].precio}")

    # 5. ELIMINACIÓN DE OBJETO (DELETE)
    print("\n[ELIMINACIÓN] Eliminando 'Pluma Fuente' (PROD-05)...")
    del root["productos"]["PROD-05"]
    db.commit()
    print(f"  * Producto eliminado. ¿Sigue en el sistema?: {'PROD-05' in root['productos']}")

    # 6. CONSULTAS SOLICITADAS
    print("\n" + "-" * 40)
    print("CONSULTAS REQUERIDAS")
    print("-" * 40)

    # Consulta A: Mostrar todos los productos registrados
    print("\nA. Todos los productos registrados:")
    for p in root["productos"].values():
        print(f"   - [{p.id_producto}] {p.nombre} - ${p.precio:.2f}")

    # Consulta B: Productos cuyo precio sea superior a determinada cantidad ($1000)
    limite_precio = 1000.0
    print(f"\nB. Productos con precio mayor a ${limite_precio:.2f}:")
    filtrados_precio = [p for p in root["productos"].values() if p.precio > limite_precio]
    for p in filtrados_precio:
        print(f"   - {p.nombre}: ${p.precio:.2f}")

    # Consulta C: Productos disponibles con existencias menores a cierto límite (< 5)
    limite_stock = 5
    print(f"\nC. Productos disponibles con existencias menores a {limite_stock}:")
    bajo_stock = [p for p in root["productos"].values() if 0 < p.existencias < limite_stock]
    for p in bajo_stock:
        print(f"   - {p.nombre} (Stock: {p.existencias})")

    # Consulta D: Productos proporcionados por un determinado proveedor (PRV-01)
    id_buscado = "PRV-01"
    print(f"\nD. Productos del proveedor con ID '{id_buscado}':")
    del_proveedor = [p for p in root["productos"].values() if p.proveedor.id_proveedor == id_buscado]
    for p in del_proveedor:
        print(f"   - {p.nombre} (Proveedor: {p.proveedor.nombre})")

    # Consulta E: Total de ventas
    print("\nE. Total de ventas:")
    total_acumulado = sum(v.calcular_total() for v in root["ventas"].values())
    print(f"   - Número de ventas registradas: {len(root['ventas'])}")
    for v in root["ventas"].values():
        print(f"     * Venta ID {v.id_venta}: ${v.calcular_total():.2f}")
    print(f"   - Monto total acumulado en ventas: ${total_acumulado:.2f}")

    db.close()
    print("\nSesión 2 completada.")

if __name__ == "__main__":
    limpiar_bd()
    sesion_1()
    sesion_2()