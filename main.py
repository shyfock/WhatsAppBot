from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient(
    "mongodb+srv://admin:admin@cluster0.sa57c.mongodb.net/cacharreria?retryWrites=true&w=majority"
)
db = cluster["cacharreria"]
users = db["usuarios"]
orders = db["ordenes"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if not bool(user):
        res.message(
            "Hola, gracias por contactar a *Cacharrería Los Marinillos, Pereira*.\nPuede seleccionar alguna "
            "de las siguientes opciones: \n\n*Escriba*\n\n 1️⃣ para *comunicarse* con nosotros \n 2️⃣ para "
            "*ordenar* productos \n 3️⃣ para conocer nuestros *horarios* \n 4️⃣ para solicitar nuestra "
            "*dirección*"
        )
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Por favor escriba una respuesta válida")
            return str(res)

        if option == 1:
            res.message(
                "Puede comunicarse con nosotros a través de teléfono o e-mail.\n\n*Teléfono*: +57 314 5363246 "
                "\n*E-mail*: contacto@marinillos.com"
            )
        elif option == 2:
            res.message("Has entrado al modo *Pedido*")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message(
                "Puede ordenar uno de los siguientes productos: \n\n1️⃣ Producto1 \n2️⃣ Producto 2 \n3️⃣ "
                "Producto 3 \n4️⃣ Producto 4 \n5️⃣ Producto 5 \n6️⃣ Producto 6 \n7️⃣ Producto 7 \n8️⃣ "
                "Producto 8 \n9️⃣ Producto 9 \n0️⃣ Regresar..."
            )
        elif option == 3:
            res.message("Abrimos de Lunes a Sábado de *9:00 A.M. a 6:00 P.M.*")
        elif option == 4:
            res.message(
                "📍*Marinillos Mayorista* carrera 15 con calle 8 \n📍*Marinillos Express* carrera 9 con calle 14"
            )
        else:
            res.message("Por favor escriba una respuesta válida")
            return str(res)
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Por favor escriba una respuesta válida")
            return str(res)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message(
                "Puede seleccionar alguna de las siguientes opciones: \n\n*Escriba*\n\n 1️⃣ para *comunicarse* con "
                "nosotros \n 2️⃣ para *ordenar* productos \n 3️⃣ para conocer nuestros *horarios* \n 4️⃣ para "
                "solicitar nuestra *dirección*"
            )
        elif 1 <= option <= 9:
            products = [
                "Producto 1",
                "Producto 2",
                "Producto 3",
                "Producto 4",
                "Producto 5",
                "Producto 6",
                "Producto 7",
                "Producto 8",
                "Producto 9",
            ]
            selected = products[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            res.message("Muy buena elección 😉")
            res.message("Por favor ingrese su dirección para confirmar el pedido")
        else:
            res.message("Por favor escriba una respuesta válida")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Gracias por comprar con nosotros!")
        res.message(
            f"Hemos recibido tu pedido de {selected} y será entregado en las próximas horas"
        )
        orders.insert_one(
            {
                "number": number,
                "item": selected,
                "address": text,
                "order_time": datetime.now(),
            }
        )
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message(
            "Hola, gracias por contactar a *Cacharrería Los Marinillos, Pereira*.\nPuede seleccionar alguna "
            "de las siguientes opciones: \n\n*Escriba*\n\n 1️⃣ para *comunicarse* con nosotros \n 2️⃣ para "
            "*ordenar* productos \n 3️⃣ para conocer nuestros *horarios* \n 4️⃣ para solicitar nuestra "
            "*dirección*"
        )
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one(
        {"number": number},
        {"$push": {"messages": {"text": text, "date": datetime.now()}}},
    )
    return str(res)


if __name__ == "__main__":
    app.run(port=5000)
