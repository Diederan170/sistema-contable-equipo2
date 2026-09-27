

from datetime import date, datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from config import Config
from database.conexion import probar_conexion, ErrorBaseDatos
from database import clientes_db

from servicios import clientes_service as clientes_srv
from servicios import contabilidad_service as contab_srv
from servicios import facturas_service as facturas_srv
from servicios import reportes_service as reportes_srv
from servicios.clientes_service import ErrorValidacion as ErrorClientes
from servicios.contabilidad_service import ErrorValidacion as ErrorContabilidad
from servicios.facturas_service import ErrorValidacion as ErrorFacturas

app = Flask(__name__)
app.config.from_object(Config)

ErroresNegocio = (ErrorClientes, ErrorContabilidad, ErrorFacturas, ErrorBaseDatos)



# Manejo centralizado de errores: nunca se muestra el error técnico


@app.errorhandler(ErrorBaseDatos)
def manejar_error_bd(error):
    flash(str(error), "error")
    return redirect(request.referrer or url_for("dashboard"))


@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("base.html", contenido_404=True), 404


def _hoy():
    return date.today().isoformat()



# RUTA RAÍZ Y DASHB

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    try:
        resumen = reportes_srv.resumen_general()
        recientes = reportes_srv.movimientos_recientes(8)
    except ErroresNegocio as error:
        flash(str(error), "error")
        resumen, recientes = {}, []
    return render_template("dashboard.html", resumen=resumen, recientes=recientes)



# CLIENTES


@app.route("/clientes")
def clientes():
    texto = request.args.get("q", "").strip()
    orden = request.args.get("orden", "")
    try:
        if texto:
            lista = clientes_srv.buscar_clientes(texto)
        else:
            lista = clientes_srv.listar_clientes(orden_por=orden or None)
    except ErroresNegocio as error:
        flash(str(error), "error")
        lista = []
    return render_template("clientes.html", clientes=lista, q=texto, orden=orden)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def clientes_nuevo():
    if request.method == "POST":
        try:
            clientes_srv.crear_cliente(
                request.form.get("nombre", ""),
                request.form.get("rfc", ""),
                request.form.get("telefono", ""),
                request.form.get("correo", ""),
                request.form.get("direccion", ""),
            )
            flash("Cliente registrado correctamente.", "exito")
            return redirect(url_for("clientes"))
        except ErroresNegocio as error:
            flash(str(error), "error")
            return render_template("cliente_form.html", cliente=request.form, modo="nuevo")
    return render_template("cliente_form.html", cliente={}, modo="nuevo")


@app.route("/clientes/<int:cliente_id>/editar", methods=["GET", "POST"])
def clientes_editar(cliente_id):
    if request.method == "POST":
        try:
            clientes_srv.editar_cliente(
                cliente_id,
                request.form.get("nombre", ""),
                request.form.get("rfc", ""),
                request.form.get("telefono", ""),
                request.form.get("correo", ""),
                request.form.get("direccion", ""),
            )
            flash("Cliente actualizado correctamente.", "exito")
            return redirect(url_for("clientes"))
        except ErroresNegocio as error:
            flash(str(error), "error")
            return render_template("cliente_form.html", cliente=request.form, modo="editar", cliente_id=cliente_id)

    try:
        cliente = clientes_srv.obtener_cliente(cliente_id)
    except ErroresNegocio as error:
        flash(str(error), "error")
        return redirect(url_for("clientes"))
    return render_template("cliente_form.html", cliente=cliente.to_dict(), modo="editar", cliente_id=cliente_id)


@app.route("/clientes/<int:cliente_id>/eliminar", methods=["POST"])
def clientes_eliminar(cliente_id):
    try:
        clientes_srv.eliminar_cliente(cliente_id)
        flash("Cliente eliminado correctamente.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("clientes"))



# INGRESOS


@app.route("/ingresos")
def ingresos():
    texto = request.args.get("q", "").strip()
    orden = request.args.get("orden", "")
    try:
        lista = contab_srv.buscar_ingresos(texto) if texto else contab_srv.listar_ingresos()
        if orden == "cantidad_desc":
            lista = contab_srv.ordenar_ingresos_por_cantidad(lista, descendente=True)
        elif orden == "cantidad_asc":
            lista = contab_srv.ordenar_ingresos_por_cantidad(lista, descendente=False)
        total = contab_srv.total_ingresos()
        lista_clientes = clientes_srv.listar_clientes()
    except ErroresNegocio as error:
        flash(str(error), "error")
        lista, total, lista_clientes = [], 0, []
    return render_template("ingresos.html", ingresos=lista, total=total, q=texto, orden=orden,
                            clientes=lista_clientes, metodos=sorted(contab_srv.METODOS_PAGO_VALIDOS))


@app.route("/ingresos/nuevo", methods=["POST"])
def ingresos_nuevo():
    try:
        contab_srv.crear_ingreso(
            request.form.get("cliente_id", type=int),
            request.form.get("descripcion", ""),
            request.form.get("fecha") or _hoy(),
            request.form.get("cantidad", ""),
            request.form.get("metodo_pago", ""),
        )
        flash("Ingreso registrado correctamente.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("ingresos"))


@app.route("/ingresos/<int:ingreso_id>/eliminar", methods=["POST"])
def ingresos_eliminar(ingreso_id):
    try:
        contab_srv.eliminar_ingreso(ingreso_id)
        flash("Ingreso eliminado correctamente.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("ingresos"))


# ------------------------------------------------------------------
# EGRESOS
# ------------------------------------------------------------------

@app.route("/egresos")
def egresos():
    texto = request.args.get("q", "").strip()
    orden = request.args.get("orden", "")
    try:
        lista = contab_srv.buscar_egresos(texto) if texto else contab_srv.listar_egresos()
        if orden == "cantidad_desc":
            lista = contab_srv.ordenar_egresos_por_cantidad(lista, descendente=True)
        elif orden == "cantidad_asc":
            lista = contab_srv.ordenar_egresos_por_cantidad(lista, descendente=False)
        total = contab_srv.total_egresos()
    except ErroresNegocio as error:
        flash(str(error), "error")
        lista, total = [], 0
    return render_template("egresos.html", egresos=lista, total=total, q=texto, orden=orden,
                            categorias=sorted(contab_srv.CATEGORIAS_EGRESO_VALIDAS))


@app.route("/egresos/nuevo", methods=["POST"])
def egresos_nuevo():
    try:
        contab_srv.crear_egreso(
            request.form.get("descripcion", ""),
            request.form.get("categoria", ""),
            request.form.get("fecha") or _hoy(),
            request.form.get("cantidad", ""),
            request.form.get("proveedor", ""),
        )
        flash("Egreso registrado correctamente.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("egresos"))


@app.route("/egresos/<int:egreso_id>/eliminar", methods=["POST"])
def egresos_eliminar(egreso_id):
    try:
        contab_srv.eliminar_egreso(egreso_id)
        flash("Egreso eliminado correctamente.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("egresos"))



# FACTURAS


@app.route("/facturas")
def facturas():
    texto = request.args.get("q", "").strip()
    orden = request.args.get("orden", "")
    try:
        lista = facturas_srv.buscar_facturas(texto) if texto else facturas_srv.listar_facturas()
        if orden == "fecha_desc":
            lista = facturas_srv.ordenar_facturas_por_fecha(lista, descendente=True)
        elif orden == "fecha_asc":
            lista = facturas_srv.ordenar_facturas_por_fecha(lista, descendente=False)
        lista_clientes = clientes_srv.listar_clientes()
    except ErroresNegocio as error:
        flash(str(error), "error")
        lista, lista_clientes = [], []
    return render_template("facturas.html", facturas=lista, q=texto, orden=orden, clientes=lista_clientes)


@app.route("/facturas/nueva", methods=["POST"])
def facturas_nueva():
    try:
        facturas_srv.crear_factura(
            request.form.get("cliente_id", type=int),
            request.form.get("fecha") or _hoy(),
            request.form.get("concepto", ""),
            request.form.get("subtotal", ""),
        )
        flash("Factura creada correctamente. IVA y total calculados automáticamente.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("facturas"))


@app.route("/facturas/<int:factura_id>/estado", methods=["POST"])
def facturas_cambiar_estado(factura_id):
    try:
        facturas_srv.cambiar_estado_factura(factura_id, request.form.get("estado", ""))
        flash("Estado de la factura actualizado.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("facturas"))


@app.route("/facturas/<int:factura_id>/eliminar", methods=["POST"])
def facturas_eliminar(factura_id):
    try:
        facturas_srv.eliminar_factura(factura_id)
        flash("Factura eliminada correctamente.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("facturas"))



# CUENTAS POR COBRAR / PAGAR


@app.route("/cuentas-cobrar")
def cuentas_cobrar():
    try:
        lista = facturas_srv.listar_cuentas_por_cobrar()
        total = facturas_srv.total_pendiente_por_cobrar()
    except ErroresNegocio as error:
        flash(str(error), "error")
        lista, total = [], 0
    return render_template("cuentas_cobrar.html", cuentas=lista, total=total)


@app.route("/cuentas-pagar")
def cuentas_pagar():
    try:
        lista = contab_srv.listar_cuentas_por_pagar()
        total = contab_srv.total_pendiente_por_pagar()
    except ErroresNegocio as error:
        flash(str(error), "error")
        lista, total = [], 0
    return render_template("cuentas_pagar.html", cuentas=lista, total=total)


@app.route("/cuentas-pagar/nueva", methods=["POST"])
def cuentas_pagar_nueva():
    try:
        contab_srv.crear_cuenta_por_pagar(
            request.form.get("proveedor", ""),
            request.form.get("descripcion", ""),
            request.form.get("fecha") or _hoy(),
            request.form.get("fecha_limite") or _hoy(),
            request.form.get("cantidad", ""),
        )
        flash("Cuenta por pagar registrada correctamente.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("cuentas_pagar"))


@app.route("/cuentas-pagar/<int:cuenta_id>/pagar", methods=["POST"])
def cuentas_pagar_pagar(cuenta_id):
    try:
        contab_srv.marcar_cuenta_pagar_pagada(cuenta_id)
        flash("Cuenta marcada como pagada.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("cuentas_pagar"))


@app.route("/cuentas-pagar/<int:cuenta_id>/eliminar", methods=["POST"])
def cuentas_pagar_eliminar(cuenta_id):
    try:
        contab_srv.eliminar_cuenta_por_pagar(cuenta_id)
        flash("Cuenta por pagar eliminada.", "exito")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("cuentas_pagar"))



# HISTORIAL (PILA - LIFO)


@app.route("/historial")
def historial():
    try:
        pila = contab_srv.obtener_pila_historial()
        elementos = pila.to_list()  # ya viene en orden LIFO (cima primero)
        vacio = pila.is_empty()
        cima = pila.peek()
    except ErroresNegocio as error:
        flash(str(error), "error")
        elementos, vacio, cima = [], True, None
    return render_template("historial.html", elementos=elementos, vacio=vacio, cima=cima)


@app.route("/historial/pop", methods=["POST"])
def historial_pop():
    try:
        elemento = contab_srv.pop_historial()
        if elemento:
            flash(f"POP: se extrajo la operación más reciente -> '{elemento['operacion']}'.", "exito")
        else:
            flash("La pila de historial está vacía, no hay nada que extraer (POP).", "error")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("historial"))



# COLA DE FACTURAS (FIFO)


@app.route("/cola")
def cola():
    try:
        cola_obj = facturas_srv.obtener_cola_facturas()
        elementos = cola_obj.to_list()  # orden FIFO (frente primero)
        vacio = cola_obj.is_empty()
        frente = cola_obj.front()
    except ErroresNegocio as error:
        flash(str(error), "error")
        elementos, vacio, frente = [], True, None
    return render_template("cola.html", elementos=elementos, vacio=vacio, frente=frente)


@app.route("/cola/procesar", methods=["POST"])
def cola_procesar():
    try:
        factura = facturas_srv.procesar_primera_factura()
        if factura:
            flash(f"DEQUEUE: se procesó la factura #{factura.id} ({factura.concepto}) -> marcada como Pagada.",
                  "exito")
        else:
            flash("La cola de facturas pendientes está vacía.", "error")
    except ErroresNegocio as error:
        flash(str(error), "error")
    return redirect(url_for("cola"))



# REPORTES


@app.route("/reportes")
def reportes():
    try:
        resumen = reportes_srv.resumen_general()
    except ErroresNegocio as error:
        flash(str(error), "error")
        resumen = {}
    return render_template("reportes.html", resumen=resumen)



# UTILIDAD: estado del almacenamiento en memoria


@app.route("/api/estado-bd")
def api_estado_bd():
    conectado = probar_conexion()
    return jsonify({"conectado": conectado})



# DATOS DE PRUEBA 

if Config.DEBUG:
    import datos_prueba

    @app.route("/dev/datos-prueba/insertar", methods=["POST"])
    def dev_insertar_datos_prueba():
        datos_prueba.insertar_datos_prueba()
        flash("Datos de prueba insertados.", "exito")
        return redirect(url_for("dashboard"))

    @app.route("/dev/datos-prueba/eliminar", methods=["POST"])
    def dev_eliminar_datos_prueba():
        datos_prueba.eliminar_datos_prueba()
        flash("Datos de prueba eliminados.", "exito")
        return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
