"""
ContaPlus - Configuración de la aplicación.

Lee la configuración desde variables de entorno (archivo .env). Este
semestre el proyecto no usa base de datos externa (todo se guarda en
memoria, ver database/almacen.py), así que aquí solo queda la
configuración de Flask.
"""

import os
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env (si existe)
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-de-desarrollo-cambia-en-produccion")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
