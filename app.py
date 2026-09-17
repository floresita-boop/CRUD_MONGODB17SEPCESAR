from flask import Flask
import pymongo

# crear el objeto flask
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./static/imagenes"

# crear la conexion a mongo
miConexion = pymongo.MongoClient("mongodb://localhost:27017")

# acceder a la base de datos
baseDatos = miConexion["GESTIONPRODUCTOS"]

# crear objeto para referenciar la colección
productos = baseDatos["PRODUCTOS"]

from controladores.controllerProducto import *

if __name__ == "__main__":
    app.run(port=3000, debug=True)