# Sistema de Administración de Tienda (ZODB)

Sistema de gestión comercial refactorizado y desacoplado, desarrollado en Python y respaldado por una base de datos orientada a objetos (BDOO) utilizando ZODB.

## Arquitectura del Proyecto

El sistema se diseñó bajo una separación estricta de responsabilidades:

- **Modelos (`modelos.py`)**: Define las clases del dominio comercial (`Producto`, `Cliente`, `Proveedor`, `Venta`, `DetalleVenta`) que heredan de `persistent.Persistent` para permitir el rastreo automático de cambios.
- **Persistencia (`database.py`)**: Administra el ciclo de vida de la base de datos orientada a objetos (`FileStorage`, `DB`), inicializa las colecciones principales mediante `BTrees` y gestiona las transacciones atómicas a través de un Context Manager con `commit` y `abort`.
- **Lógica de Negocio (`servicios.py`)**: Orquesta las operaciones del sistema (`InventarioService`, `VentaService`), aplicando validaciones estrictas y controlando la deducción de inventario antes de persistir.
- **Consultas (`consultas.py`)**: Proporciona consultas de sólo lectura (`InventarioQueries`) para inventario disponible, alertas de bajo stock, compras por cliente y estadísticas de ventas.
- **Excepciones de Dominio (`excepciones.py`)**: Define una jerarquía de errores personalizados (`StockInsuficienteError`, `EntidadNoEncontradaError`, `ValidacionDatosError`) heredados de `TiendaError`.
- **Interfaz Gráfica (`interfaz_grafica.py`)**: Capa de presentación desarrollada con Tkinter que consume los servicios y consultas del sistema.

---

## Requisitos Previos

- Python 3.8 o superior.
- Administrador de paquetes `pip`.

---

## Instalación y Configuración

1. **Clonar o descargar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd sistema_tienda

2. **Crear y activar un entorno virtual:**
   - En Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - En Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
