# ContaPlus — Sistema de Administración Contable

> **Nota de este semestre:** por indicación del profesor, la versión
> actual **no usa base de datos externa**: todo se guarda en memoria
> (ver `database/almacen.py`). El script `sql/database.sql` y el uso de
> PostgreSQL se retoman el próximo semestre; por eso se conservan en el
> repositorio tal cual.

## 1. Qué es ContaPlus

ContaPlus es un sistema web de administración contable desarrollado como
proyecto académico para la materia **Estructura de Datos**. Simula un
despacho de administración contable que presta servicios a pequeñas y
medianas empresas, permitiendo administrar clientes, ingresos, egresos,
facturas, cuentas por cobrar/pagar, historial de operaciones y reportes.

## 2. Objetivo

Además de ser un sistema funcional, ContaPlus demuestra de forma **real**
(no decorativa) el uso de estructuras de datos y algoritmos clásicos:
lista enlazada, pila (LIFO), cola (FIFO), búsqueda lineal/binaria y
ordenamiento (Bubble Sort / Insertion Sort), implementados manualmente en
Python.

## 3. Tecnologías

- **Backend:** Python 3 + Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Almacenamiento:** en memoria (Lista Enlazada propia), sin base de datos externa este semestre

## 4. Estructura del proyecto

```
ContaPlus/
├── app.py                     # Rutas Flask y arranque de la app
├── config.py                  # Configuración de Flask (lee variables de entorno)
├── datos_prueba.py            # Funciones para insertar/eliminar datos de ejemplo
├── requirements.txt
├── .env.example
├── estructuras/                # Estructuras de datos académicas
│   ├── lista.py
│   ├── pila.py
│   ├── cola.py
│   ├── busqueda.py
│   └── ordenamiento.py
├── modelos/                    # Clases de datos (dataclasses)
├── database/
│   ├── almacen.py              # Almacenamiento en memoria (reemplaza a PostgreSQL este semestre)
│   ├── conexion.py             # Compatibilidad (ya no conecta a nada externo)
│   ├── clientes_db.py
│   ├── movimientos_db.py
│   └── facturas_db.py
├── servicios/                  # Lógica de negocio + validaciones
├── templates/                  # Vistas HTML (Jinja2)
├── static/css, static/js       # Estilos y JS
├── sql/database.sql            # Script de PostgreSQL, reservado para el próximo semestre
└── tests/                      # Pruebas básicas

```

## 5. Requisitos

- Python 3.10 o superior
- Visual Studio Code (recomendado, con la extensión de Python)

## 6. Instalación de Python

Descarga e instala Python desde https://www.python.org/downloads/
Verifica la instalación:

```bash
python --version
```

## 7. Configuración del archivo .env (opcional)

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Puedes cambiar `SECRET_KEY` por una clave propia. No es obligatorio
para correr el proyecto en local.

## 8. Instalación de dependencias

Se recomienda usar un entorno virtual:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

## 9. Ejecución del proyecto

Con el entorno virtual activado:

```bash
python app.py
```

Deberías ver un mensaje indicando que Flask está corriendo en
`http://127.0.0.1:5000`. Al no depender de una base de datos externa,
arranca de inmediato.

## 10. Acceso desde el navegador

Abre tu navegador en:

```
http://127.0.0.1:5000
```

Serás redirigido automáticamente al Dashboard.

## 11. Estructuras de datos utilizadas

| Estructura         | Archivo                        | Dónde se usa                                   |
|---------------------|---------------------------------|-------------------------------------------------|
| Lista enlazada       | `estructuras/lista.py`         | Disponible como estructura genérica de apoyo    |
| Pila (LIFO)          | `estructuras/pila.py`          | Página `/historial`                              |
| Cola (FIFO)          | `estructuras/cola.py`          | Página `/cola`                                   |
| Búsqueda lineal      | `estructuras/busqueda.py`      | Buscadores de Clientes, Ingresos, Egresos, Facturas |
| Búsqueda binaria     | `estructuras/busqueda.py`      | Disponible para búsquedas por ID en listas ordenadas |
| Bubble / Insertion Sort | `estructuras/ordenamiento.py` | Ordenar clientes, ingresos, egresos y facturas |

Nota: `database/almacen.py` también usa la Lista Enlazada como
almacenamiento base de cada "tabla" (clientes, ingresos, egresos,
facturas, cuentas por pagar, movimientos e historial).

## 12. Cómo probar la búsqueda

1. Ve a **Clientes**, **Ingresos**, **Egresos** o **Facturas**.
2. Escribe un texto en el campo de búsqueda (nombre, RFC, correo, descripción o concepto).
3. El sistema usa `busqueda_lineal()` (implementada manualmente) para filtrar resultados.

## 13. Cómo probar el ordenamiento

1. En **Clientes**, usa el selector "Ordenar por" (nombre o fecha de registro).
2. En **Ingresos** o **Egresos**, ordena por cantidad (mayor a menor o viceversa).
3. En **Facturas**, ordena por fecha.
4. Internamente se ejecuta `bubble_sort()` sobre los datos guardados en memoria.

## 14. Cómo probar la Pila (historial)

1. Ve a **Historial** en el menú lateral.
2. Cada operación que realices en el sistema (registrar cliente, ingreso, factura, etc.) se apila automáticamente (**PUSH**).
3. La página muestra la **cima** de la pila (**PEEK**) y todo el contenido en orden LIFO.
4. Presiona **"Ejecutar POP"** para extraer la operación más reciente y observar el comportamiento LIFO en vivo.

## 15. Cómo probar la Cola (facturas pendientes)

1. Crea algunas facturas desde **Facturas** (quedan con estado "Pendiente").
2. Ve a **Cola de facturas**: verás las facturas pendientes en orden FIFO.
3. La página muestra el elemento al **frente** (**FRONT**) y si la cola está vacía (**IS_EMPTY**).
4. Presiona **"Ejecutar DEQUEUE"** para procesar la primera factura pendiente (se marca como "Pagada") y observa cómo la siguiente pasa al frente.

## 16. Datos de prueba

Como los datos viven en memoria, deben cargarse **dentro del proceso
de Flask que ya está corriendo**. Con la app en marcha (`python
app.py`, modo DEBUG por defecto), usa los botones del menú lateral:

- **➕ Datos de prueba** — agrega 3 clientes, 3 ingresos, 3 egresos, 3 facturas y 3 cuentas por pagar.
- **🗑️ Borrar prueba** — elimina únicamente esos registros de ejemplo.

(El script `python datos_prueba.py insertar` por separado ya NO llena
la app en ejecución, porque sería un proceso distinto con su propia
memoria; se conserva solo como referencia/para pruebas manuales por
consola.)

## 17. Ejecutar las pruebas básicas

```bash
python -m unittest discover tests
```

Esto verifica: disponibilidad del almacenamiento, cálculo de
IVA/total/balance, comportamiento de la pila y la cola, y los
algoritmos de búsqueda y ordenamiento. Al no depender de una base de
datos externa, ya no hay pruebas que se salten por falta de conexión.

## 18. Notas de seguridad

- Como no hay una base de datos externa este semestre, no aplica el riesgo de inyección SQL (no se ejecuta SQL en el flujo normal de la app).
- Los datos viven solo en memoria RAM del proceso de Flask: se pierden al reiniciar el servidor (no hay persistencia en disco).
- Los errores de negocio (validaciones) nunca muestran detalles técnicos crudos al usuario; se traducen a mensajes comprensibles.
