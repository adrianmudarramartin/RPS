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

# Prepara el entorno de trabajo fuera del repositorio
os.system('libraries.sh')
os.chdir('..')

# Inicialización de la base de datos
conexion= sqlite3.connect('Datos.sqlite', check_same_thread=False)     
cursor= conexion.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Principal (ID_Chat PRIMARY KEY, Nombre TEXT, Usuario TEXT, Estado TEXT, V1M INT, D1M INT, V3M INT, D3M INT, V5M INT, D5M INT, V1A INT, D1A INT, V3A INT, D3A INT, V5A INT, D5A INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Juego_Maquina (ID_Chat PRIMARY KEY, Tipo_Partida INT, Ganadas INT, Perdidas INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Juego_Amigo (ID_Chat_1 INT, ID_Chat_2 INT, Invitacion TEXT, Tipo_Partida INT, Hora_Actualizacion TEXT, V_1 INT, V_2 INT, Respuesta_1 TEXT, Respuesta_2 TEXT)''')
conexion.commit()

print('Me he ejecutado de locos')