# REINICIAR fatAPI --> pipenv shell /// uvicorn api:app --reload
# DETENER fastAPI --> ctrl + c


# PRIMERO HAY QUE SELECCIONAR INTERPRETE --> ctrl + shift + p  y selecciono el que diga python y la carpeta donde estoy trabajando
# PARA INSTALAR FASTAPI EN TERMINAL --> tambien instalamos el uvicorn que es con el que 
# se recomienda trabajar con fastapi y el modulo para crear la plantilla de los objetos(cliente) osea pa definir
# la estructura del cliente el cual es pydantic 
# tambien instalamos -r requirements.txt que es pa usar pytest

# Módulos de peticion HTTP( algunos, los que usamos en este caso)
# GET --> consultar por clientes
# POST --> para crear clientes
# PUT --> actualizar clientes
# DELETE --> para borrar clientes

from fastapi import FastAPI, Response, HTTPException # hay que ponerle Response cuando quiero que me devuelva una respuesta que no sea json (html por ej)
from fastapi.responses import JSONResponse # Nos da respuesta de tipo json
headers = {"content-type":"charset=utf-8"} # Esto define un diccionario de cabeceras HTTP para tus respuestas.
# headers es pa hacer compatible el codigo con los signos de ortografia
# 1ero --> crear aplicacion de tipo fastapi
from pydantic import BaseModel, constr, field_validator # constr hace referencia a un tipode dato cadena obligatorio, que servirá para las validaciones del modelo
import database as db
import helpers

class ModeloCliente(BaseModel): # aquí creamos los campos de nuestro modelo
    dni: constr(min_length=3, max_length=3) # indicamos constr como una funcion y establecemos validaciones de esta cadena que seran lo de parentesis
    nombre: constr(min_length=2,max_length=30)
    apellido: constr(min_length=2,max_length=30)

#Creamos una validacion extendida para nuestro ModeloCliente en el campo dni    
class ModeloCrearCliente(ModeloCliente): # creamos esta clase que hereda de modelocleinte y reutilizamos estructura de arriba pero solo
    # como si fuera para formulario de creacion 
    #validador unico para un campo extendiendo las validaciones de la constr
    @field_validator("dni") # le indicamos que vamos a validar de forma extendida el dni
    def validar_dni(cls, dni): # recibe la instancia de la clase y el campo que queremos validar que es dni
        if helpers.dni_valido(dni, db.Clientes.lista):
        # esta funcion de helpers me comprueba tanto si el dni tiene el formato correcto, como si 
        # no esta duplicado
            return dni
        raise ValueError("Cliente ya existente o DNI incorrecto")
    


app = FastAPI( #  Esto crea una instancia de tu aplicación. Todas las rutas (@app.get(...)) se van a registrar aquí.
    title ="API del Gestor de Clientes",
    description="Ofrece diferentes funciones para gestionar los clientes."
)
    



# funcion asincrona osea se ejecuta de manera que no se bloquea el proceso, sino que se 
# ejecuta paralelamente en la memoria
# para registrar esta funcion como una ruta de la api para poder hacer desde el navegador
# usaremos un decorador que es el sigueinte:
#@app.get("/") # le dice a FastAPI que esta función se debe ejecutar cuando alguien accede a / con el método GET.
# le pasamos donde vamos a definir esta ruta, que va a ser la raiz
#este get va a ser el tipo de metodo, solo una funcion de consulta que va a devolver un mensaje
#Borramos la raiz y el html porque ya no los necesitabamos al finalizar todos las solicitudes hasta delete
#async def index(): # define una función asíncrona (permite operaciones rápidas, sin bloquear el servidor).
    
    #content = {"mensaje":"¡Hola Mundo!"} # es el contenido que se va a devolver (un diccionario).
    #return JSONResponse(content=content, headers = headers, media_type="application/json") # hará la conversión entre diccionario a  json
#media_type define el tipo de contenido de la respuesta, también llamado Content-Type.Le dice al navegador o cliente: “Lo que te estoy enviando es un JSON.”
# el media_type de la respuesta en una cadena llamada application/json(esto es nomenclatura)
# y establece el tipo de la salida, del texto a un formato json

# Por ejemplo podemos crear una respuesta en crudo en la ruta /html/ de tipo GET para devolver una cadena con código HTML:
#@app.get('/html/')  #define la ruta para http://localhost:8000/html/
#async def html(): #la función que se ejecuta cuando alguien accede a esa ruta
    #content = """
    #<!DOCTYPE html>
    #<html lang="es">
    #<head>
    #    <meta charset="UTF-8">
    #    <title>¡Hola mundo!</title>
    #</head>
    #<body>
    #    <h1>¡Hola mundo!</h1>
    #</body>
    #</html>
    #""" # contenido es codigo html en crudo
    #return Response(content= content, media_type="text/html")
    

# definimos una nueva ruta para la app, que definimos en /clientes/, esta nos devolverá toda la lista de clientes    
@app.get('/clientes/', tags=["Clientes"])
async def clientes():
    content = [   # vamos a tomar de database la lista de clientes asignandola a content
        cliente.to_dict() for cliente in db.Clientes.lista] # hacemos esto para obtener una lista de diccionarios y asi si acepta el valor el jsonresponse
    # Lo que hicimos es una comprension de listas: [nueva_estructura for elemento in lista] y de nueva estructura le puse el metodo to_dict de la clase
    # cliente que retorna un diccionario ( se encuentra en database )
    return JSONResponse(content=content, headers=headers)

@app.get('/clientes/buscar/{dni}', tags=["Clientes"]) # le pasamos el campo que podemos recuperar que es el dni
async def clientes_buscar(dni:str): # como le estoy pasando en la ruta el campo dni, lo puedo recuperar como un parámetro
    # de la funcion clientes_buscar, incluso puedo definir que es tipo string
    cliente = db.Clientes.buscar(dni=dni)
    if not cliente:   # para que me arroje algo cuando se meta un dni incorrecto, y no solo el error internal server
        raise HTTPException(status_code=404, detail="Cliente NO encontrado") # aquí invocamos un error o una excepcion, la que importamos arriba HTTPException
        
    return JSONResponse(content=cliente.to_dict(), headers=headers)

@app.post('/clientes/crear/', tags=["Clientes"]) # usamos metodo post porque vamos a crear informacion, por eso usamos post que es el metodo que tomaria datos
# de un formulario
async def clientes_crear(datos:ModeloCrearCliente):
    # vamos a crear una instancia de un cliente a partir de una informacion que vamos a recirbir
    # en la peticion y devoleer este cliente en forma json
    # fastapi nos permite hacer uso de la biblioteca pydantic para crear un modelo de un dato y añadirle validaciones
    cliente = db.Clientes.crear(datos.dni, datos.nombre, datos.apellido)
    if cliente: # sii existe un cliente significa que se ha creado en nuestro fichero en nuestra basede datos
        return JSONResponse(content=cliente.to_dict(), headers=headers) # le pido que me retorne nuestro cliente
    # transformado ya a json mediante el todict y las cabeceras
    raise HTTPException(status_code=404, detail="Cliente NO creado") 
    
    
@app.put('/clientes/actualizar/', tags=["Clientes"]) # metodo put porque peticiones put son idenpotentes(si ejecutamos multiples veces la misma solicitud, siempre se va a 
# producir el mismo resultado, a diferencia de post)
async def clientes_actualizar(datos:ModeloCliente): # al actualizar un registro, nuestro programa no permite cambiar un dni, por tanto usamos el 
#ModeloCliente, porque en este metodo no hay validacion de dni
    #debemos primero buscar el cleinte que vamos a actualizar:
    if db.Clientes.buscar(datos.dni): # si esto existe hacemos:
        cliente = db.Clientes.modificar(datos.dni, datos.nombre, datos.apellido)
        #le pasamos dni para que sepa que cliente queremos modificar, y el nuevo nombre y apellido
        if cliente: # si cliente existe, NO es None, signfiica que se ha actualizado correctamente, podríamos devolver el cliente en diccionario en jsonresponse
            return JSONResponse(content=cliente.to_dict(), headers=headers)
            
    raise HTTPException(status_code=404, detail="Cliente NO encontrado") 
    

@app.delete('/clientes/borrar/{dni}', tags=["Clientes"])
async def clientes_borrar(dni:str): # aquí recuperamos el dni como una cadena
    if db.Clientes.buscar(dni): # si se encuentra el cliente a traves del dni
        cliente = db.Clientes.borrar(dni=dni)
        return JSONResponse(content=cliente.to_dict(), headers=headers)
    raise HTTPException(status_code=404, detail="Cliente NO encontrado")  



# al ejecutar hasta aqui no pasa nada y es porque nuestra api es un servicio 
# que debe de mantenerse en marcha y esta definido en nuestra variable app = FastAPI()
# para que ejecute tenemos que usar ubycorn y decirle que utilice la app de este fichero API
# como variable que va a gestionar el servicio, para lo que se usa el comando:pipenv run uvico
# rn api:app --reload (reload detecta algun cambio en el fichero para recargarlo) ahora si se pone en marcha el servicio
print("Servidor de la API...") 





