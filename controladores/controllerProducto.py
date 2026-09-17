from app import app, productos
from flask import Flask, request, render_template, redirect
import pymongo
from werkzeug.utils import secure_filename
import os
from bson.objectid import ObjectId

# 1. Función para validar si existe un producto por su código
def consultarProductoPorCodigo(codigo):
    try:
        consulta = {"codigo": codigo}
        producto = productos.find_one(consulta)
        if(producto is not None):
            return True
        else:
            return False
    except pymongo.errors as error:
        print(error)
        return False

# 2. Ruta de la página principal
@app.route("/")
def inicio():
    # obtener la lista de productos de la colección productos
    listaProductos = productos.find()
    return render_template("listarProductos.html",
                         listaProductos=listaProductos)

# 3. Ruta para procesar y agregar el producto
@app.route("/agregarProducto", methods=["POST"])
def agregarProducto():
    mensaje = ""
    try:
        # recibir los valores de la vista en variables locales
        codigo = int(request.form["txtCodigo"])
        nombre = request.form["txtNombre"]
        precio = int(request.form["txtPrecio"])
        categoria = request.form["cbCategoria"]
        
        # datos de la imagen
        archivo = request.files["fileFoto"]
        nombreArchivo = secure_filename(archivo.filename)
        listaNombreArchivo = nombreArchivo.rsplit(".", 1)
        extension = listaNombreArchivo[1].lower()
        
        # crear el objeto producto de tipo diccionario
        producto = {
            "codigo": codigo,
            "nombre": nombre,
            "precio": precio,
            "categoria": categoria
        }
        
        # validar si existe producto con código
        existe = consultarProductoPorCodigo(codigo)
        if(existe):
            mensaje = "Ya existe producto con ese código"
            return render_template("frmAgregarProducto.html",
                                 producto=producto,
                                 mensaje=mensaje)
        else:
            # ejecutar consulta de inserción de datos
            resultado = productos.insert_one(producto)
            if resultado.acknowledged:
                mensaje = "Producto Agregado Correctamente"
                # obtener el id del producto que se acaba de insertar
                idProducto = resultado.inserted_id
                nuevoNombre = str(idProducto) + "." + str(extension)
                archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nuevoNombre))
                return redirect("/")
    except pymongo.errors as error:
        mensaje = error
        return render_template("frmAgregarProducto.html",
                             producto=producto,
                             mensaje=mensaje)

@app.route("/consultar/<string:idProducto>", methods=["GET"])
def consultarPorId(idProducto):
    try:
        idProducto = ObjectId(idProducto)
        consulta = {"_id": idProducto}
        producto = productos.find_one(consulta)
        return render_template("frmEditarProducto.html", producto=producto)
    except pymongo.errors as error:
        mensaje = error
        listaProductos = productos.find()
        return render_template("listarProductos.html",
                             mensaje=mensaje,
                             listaProductos=listaProductos)

@app.route("/actualizar", methods=["POST"])
def actualizarProducto():
    try:
        # recibir los valores de la vista en variables locales
        codigo = int(request.form["txtCodigo"])
        nombre = request.form["txtNombre"]
        precio = int(request.form["txtPrecio"])
        categoria = request.form["cbCategoria"]
        idProducto = ObjectId(request.form["idProducto"])
        criterio = {"_id": idProducto}
        datosActualizar = {
            "codigo": codigo,
            "nombre": nombre,
            "precio": precio,
            "categoria": categoria
        }
        consulta = {"$set": datosActualizar}
        resultado = productos.update_one(criterio, consulta)
        
        if (resultado.acknowledged):
            mensaje = "Producto Actualizado"
            # verificar si viene foto para actualizarla
            archivo = request.files["fileFoto"]
            if (archivo.filename != ""):
                nombreArchivo = secure_filename(archivo.filename)
                listaNombreArchivo = nombreArchivo.rsplit(".", 1)
                extension = listaNombreArchivo[1].lower()
                nombreArchivoActualizar = str(idProducto) + "." + str(extension)
                archivo.save(os.path.join(app.config["UPLOAD_FOLDER"],
                                          nombreArchivoActualizar))
    except pymongo.errors as error:
        print(error)      
        
@app.route("/eliminar/<string:idProducto>", methods=["GET"])
def eliminarProducto(idProducto):
    try:
        idProducto = ObjectId(idProducto)
        consulta = {"_id": idProducto}
        resultado = productos.delete_one(consulta)
        if (resultado.acknowledged):
            mensaje = "Producto eliminado"
        else:
            mensaje = "Problemas al Eliminar"
    except pymongo.errors as error:
        mensaje = error
    listaProductos = productos.find()
    return render_template("listarProductos.html",
                           mensaje=mensaje, listaProductos=listaProductos)
    
    # Ruta para mostrar el formulario de agregar producto
@app.route("/agregar", methods=["GET"])
def vistaAgregar():
    return render_template("frmAgregarProducto.html")                 