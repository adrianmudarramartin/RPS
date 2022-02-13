# Bot de piedra, papel, tijeras
# Autor: Adrián Mudarra Martín

# Librerías usadas
import random
import telebot
from telebot import types
import sqlite3
import time
from datetime import datetime
import os
import paho.mqtt.client as mqtt

# Inicialización de la base de datos
conexion= sqlite3.connect('Datos.sqlite', check_same_thread=False)     
cursor= conexion.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Principal (ID_Chat PRIMARY KEY, Nombre TEXT, Usuario TEXT, Estado TEXT, V1M INT, D1M INT, V3M INT, D3M INT, V5M INT, D5M INT, V1A INT, D1A INT, V3A INT, D3A INT, V5A INT, D5A INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Juego_Maquina (ID_Chat PRIMARY KEY, Tipo_Partida INT, Ganadas INT, Perdidas INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Juego_Amigo (ID_Chat_1 INT, ID_Chat_2 INT, Invitacion TEXT, Tipo_Partida INT, Hora_Actualizacion TEXT, V_1 INT, V_2 INT, Respuesta_1 TEXT, Respuesta_2 TEXT)''')
conexion.commit()

def on_message(client, data, msg):
    # print(msg.topic + " " + str(msg.payload))
    cursor.execute('''SELECT Nombre, MAX(V1A) FROM Principal''')
    nombre = cursor.fetchone()[0]
    client.publish('V1A',nombre)
    cursor.execute('''SELECT Nombre, MAX(V3A) FROM Principal''')
    nombre = cursor.fetchone()[0]
    client.publish('V3A',nombre)
    cursor.execute('''SELECT Nombre, MAX(V5A) FROM Principal''')
    nombre = cursor.fetchone()[0]
    client.publish('V5A',nombre)
    
client = mqtt.Client("")
client.on_message = on_message
client.username_pw_set(username="pi", password="patatas")
client.connect("localhost", 1883, 60)
client.loop_forever()
client.subscribe("request")

#try:
#    while True:
#        time.sleep(1)
#except KeyboardInterrupt:
#    print("Ok")
#    client.disconnect()
#    client.loop_stop()