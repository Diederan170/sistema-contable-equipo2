"""
ContaPlus - Datos de prueba.

Ejecuta este script para insertar rápidamente datos de ejemplo y poder
hacer una demostración inmediata al profesor:

    python datos_prueba.py insertar
    python datos_prueba.py eliminar

"insertar" agrega 3 clientes, 3 ingresos, 3 egresos, 3 facturas y
3 cuentas por pagar.
"eliminar" borra ÚNICAMENTE los registros de prueba (identificados por
el RFC/proveedor que usa este script), sin tocar el resto de tus datos.

IMPORTANTE: como este semestre los datos viven en memoria (no en una
base de datos), correr este script como proceso aparte NO llenará los
datos de la app que ya tienes corriendo con `python app.py` (serían dos
procesos con memoria distinta). Para eso, con la app en modo DEBUG
(por defecto), usa los botones "Datos de prueba" del menú lateral, que
ejecutan estas mismas funciones dentro del proceso de Flask activo.

Este script sigue siendo útil para pruebas manuales rápidas por
consola (`python`, luego `import datos_prueba; datos_prueba.insertar_datos_prueba()`)
o como referencia de las cantidades y campos de ejemplo.
"""

import sys
from datetime import date, timedelta

from database import clientes_db, movimientos_db, facturas_db

RFCS_PRUEBA = ["PRUE010101AAA", "PRUE020202BBB", "PRUE030303CCC"]
PROVEEDOR_PRUEBA = "Proveedor de Prueba SA de CV"


def insertar_datos_prueba():
    nombres = ["Cliente de Prueba Uno", "Cliente de Prueba Dos", "Cliente de Prueba Tres"]
    clientes_ids = []
    for nombre, rfc in zip(nombres, RFCS_PRUEBA):
        if clientes_db.existe_rfc(rfc):
            continue
        fila = clientes_db.crear_cliente(
            nombre, rfc, "5555555555", f"{rfc.lower()}@correo.com", "Calle de Prueba #123"
        )
        clientes_ids.append(fila[0])

    if not clientes_ids:
        # ya existían de una corrida anterior en este mismo proceso
        clientes_ids = [
            f[0] for f in clientes_db.obtener_todos_clientes() if f[2] in RFCS_PRUEBA
        ]

    hoy = date.today()

    for i, cid in enumerate(clientes_ids):
        movimientos_db.crear_ingreso(
            cid, f"Servicio contable {i + 1} (prueba)", hoy - timedelta(days=i),
            1500.00 + i * 250, "Transferencia",
        )

    categorias = ["Papelería", "Software", "Renta"]
    for i, categoria in enumerate(categorias):
        movimientos_db.crear_egreso(
            f"Gasto de prueba {i + 1}", categoria, hoy - timedelta(days=i),
            300.00 + i * 100, PROVEEDOR_PRUEBA,
        )

    for i, cid in enumerate(clientes_ids):
        subtotal = 1000.00 + i * 500
        iva = round(subtotal * 0.16, 2)
        total = round(subtotal + iva, 2)
        facturas_db.crear_factura(
            cid, hoy - timedelta(days=i), f"Factura de prueba {i + 1}", subtotal, iva, total,
        )

    for i in range(3):
        movimientos_db.crear_cuenta_por_pagar(
            PROVEEDOR_PRUEBA, f"Cuenta de prueba {i + 1}", hoy, hoy + timedelta(days=15 + i),
            500.00 + i * 150,
        )

    print("Datos de prueba insertados correctamente: 3 clientes, 3 ingresos, 3 egresos, "
          "3 facturas y 3 cuentas por pagar.")


def eliminar_datos_prueba():
    for fila in clientes_db.obtener_todos_clientes():
        if fila[2] in RFCS_PRUEBA:
            clientes_db.eliminar_cliente(fila[0])

    for fila in movimientos_db.obtener_todos_egresos():
        if fila[5] == PROVEEDOR_PRUEBA:
            movimientos_db.eliminar_egreso(fila[0])

    for fila in movimientos_db.obtener_todas_cuentas_por_pagar():
        if fila[1] == PROVEEDOR_PRUEBA:
            movimientos_db.eliminar_cuenta_por_pagar(fila[0])

    print("Datos de prueba eliminados correctamente.")


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else ""
    if accion == "insertar":
        insertar_datos_prueba()
    elif accion == "eliminar":
        eliminar_datos_prueba()
    else:
        print("Uso: python datos_prueba.py [insertar|eliminar]")
