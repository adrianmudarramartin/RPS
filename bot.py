# Bot de piedra, papel, tijeras
# Autor: Adrián Mudarra Martín

# Librerías usadas
from lib2to3.pgen2.token import COLONEQUAL
import random
from sre_parse import parse_template
import telebot
from telebot import types
import sqlite3
import time

# Inicialización de la base de datos
conexion= sqlite3.connect('Datos.sqlite', check_same_thread=False)     
cursor= conexion.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Principal (ID_Chat PRIMARY KEY, Nombre TEXT, Usuario TEXT, Estado TEXT, V1 INT, D1 INT, V3 INT, D3 INT, V5 INT, D5 INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Juego_Maquina (ID_Chat PRIMARY KEY, Tipo_Partida INT, Ganadas INT, Perdidas INT)''')
conexion.commit()

# Inicialización de los parámetros iniciales del bot
TOKEN = open('bot.txt','r').read() # Archivo que incluye únicamente el token del bot
bot = telebot.TeleBot(TOKEN)

# INICIO 
@bot.message_handler(commands=['start'])
def bienvenida(message):
    if Comprobar_Estado(message.chat.id)==1:
        bot.send_message(message.chat.id, '¡Bienvenid@ al bot de Piedra, Papel, Tijeras! Puedes utilizar los siguientes comandos:\n\n/partida_vs_maquina - Inicia una partida contra la máquina.\n/estadisticas - Muestra tus estadísticas generales.')
        cursor.execute('''INSERT OR IGNORE INTO Principal (ID_Chat, Nombre, Usuario, Estado, V1, D1, V3, D3, V5, D5) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (message.chat.id, message.from_user.first_name+' '+message.from_user.last_name, message.from_user.username, 'INICIO', 0, 0, 0, 0, 0, 0))
        conexion.commit()

# Muestra las estadísticas del jugador
@bot.message_handler(commands=['estadisticas'])
def estadisticas(message):
    if Comprobar_Estado(message.chat.id, 'INICIO'):
        cursor.execute('''SELECT V1, D1, V3, D3, V5, D5 FROM Principal WHERE ID_Chat = ?''', (message.chat.id, ))
        est = cursor.fetchone() # Números de las estadísticas
        bot.send_message(message.chat.id, '''*TUS ESTADÍSTICAS*\n
        *A ronda única* ('''+str(est[0]+est[1])+''' jugadas)
        Victorias: '''+str(est[0])+'''
        Derrotas: '''+str(est[1])+'''\n
        *Al mejor de 3* ('''+str(est[2]+est[3])+''' jugadas)
        Victorias: '''+str(est[2])+'''
        Derrotas: '''+str(est[3])+'''\n
        *Al mejor de 5* ('''+str(est[4]+est[5])+''' jugadas)
        Victorias: '''+str(est[4])+'''
        Derrotas: '''+str(est[5])+'''\n''', parse_mode='Markdown')

@bot.message_handler(commands=['partida_vs_maquina'])
def numero_rondas(message):
    if Comprobar_Estado(message.chat.id, 'INICIO'):
        Cambiar_Estado(message.chat.id, 'VS_MÁQUINA_RONDAS')
        teclado = types.ReplyKeyboardMarkup(row_width=1)
        ronda_1 = types.KeyboardButton('Ronda única')
        ronda_3 = types.KeyboardButton('Al mejor de 3')
        ronda_5 = types.KeyboardButton('Al mejor de 5')
        volver = types.KeyboardButton('<< Volver')
        teclado.add(ronda_1, ronda_3, ronda_5, volver)
        bot.send_message(message.chat.id, '¿Qué tipo de partida quieres jugar?', reply_markup= teclado)

@bot.message_handler(regexp='.*')
def partida(message):
    # Elegir tipo de partida
    if Comprobar_Estado(message.chat.id, 'VS_MÁQUINA_RONDAS'):
        teclado = types.ReplyKeyboardMarkup(row_width=1)
        piedra = types.KeyboardButton('🥌 Piedra 🥌')
        papel = types.KeyboardButton('📄 Papel 📄')
        tijeras = types.KeyboardButton('✂️ Tijeras ✂️')
        teclado.add(piedra, papel, tijeras)
        Cambiar_Estado(message.chat.id, 'VS_MÁQUINA_JUGANDO')
        if message.text=='Ronda única':
            bot.reply_to(message, 'Has elegido jugar a ronda única. ¡Suerte!', reply_markup= teclado)
            cursor.execute('''INSERT OR IGNORE INTO Juego_Maquina (ID_Chat, Tipo_Partida, Ganadas, Perdidas) VALUES (?, ?, ?, ?)''', (message.chat.id, 1, 0, 0))
        elif message.text=='Al mejor de 3':
            bot.reply_to(message, 'Has elegido jugar a tres rondas. ¡Suerte!', reply_markup= teclado)
            cursor.execute('''INSERT OR IGNORE INTO Juego_Maquina (ID_Chat, Tipo_Partida, Ganadas, Perdidas) VALUES (?, ?, ?, ?)''', (message.chat.id, 3, 0, 0))
        elif message.text=='Al mejor de 5':
            bot.reply_to(message, 'Has elegido jugar cinco rondas ¡Suerte!', reply_markup= teclado)
            cursor.execute('''INSERT OR IGNORE INTO Juego_Maquina (ID_Chat, Tipo_Partida, Ganadas, Perdidas) VALUES (?, ?, ?, ?)''', (message.chat.id, 5, 0, 0))
        elif message.text=='<< Volver':
            teclado = types.ReplyKeyboardRemove(selective=False)
            bot.send_message(message.chat.id, 'Puedes utilizar los siguientes comandos:\n\n/partida_vs_maquina - Inicia una partida contra la máquina.\n/estadisticas - Muestra tus estadísticas generales.', reply_markup=teclado)
            Cambiar_Estado(message.chat.id, 'INICIO')
    # Dentro de la partida
    elif Comprobar_Estado(message.chat.id, 'VS_MÁQUINA_JUGANDO'):
        cursor.execute('''SELECT Tipo_Partida, Ganadas, Perdidas FROM Juego_Maquina WHERE ID_Chat = ?''', (message.chat.id, ))
        est = cursor.fetchone()
        maquina = random.choice(['🥌 Piedra 🥌', '📄 Papel 📄', '✂️ Tijeras ✂️'])
        mensaje_bot = bot.reply_to(message, 'La máquina dice.')
        time.sleep(0.7)
        bot.edit_message_text('La máquina dice..', message.chat.id, mensaje_bot.id)
        time.sleep(0.7)
        bot.edit_message_text('La máquina dice...', message.chat.id, mensaje_bot.id)
        time.sleep(0.7)
        bot.edit_message_text('La máquina dice...\n\n'+maquina, message.chat.id, mensaje_bot.id)
        time.sleep(0.7)
        if message.text==maquina:
            bot.send_message(message.chat.id, 'Empate. Elige otra vez     ('+str(est[1])+ ' - '+str(est[2])+')')
        elif (message.text=='🥌 Piedra 🥌' and maquina=='✂️ Tijeras ✂️') or (message.text=='📄 Papel 📄' and maquina=='🥌 Piedra 🥌') or (message.text=='✂️ Tijeras ✂️' and maquina=='📄 Papel 📄'):
            bot.send_message(message.chat.id, 'Ganas.     ('+str(est[1]+1)+ ' - '+str(est[2])+')')
            cursor.execute('''UPDATE Juego_Maquina SET Ganadas = Ganadas+1 WHERE ID_Chat = ?''', (message.chat.id, ))
            cursor.execute('''SELECT Tipo_Partida, Ganadas, Perdidas FROM Juego_Maquina WHERE ID_Chat = ?''', (message.chat.id, ))
            est = cursor.fetchone()
        else:
            bot.send_message(message.chat.id, 'Pierdes.     ('+str(est[1])+ ' - '+str(est[2]+1)+')')
            cursor.execute('''UPDATE Juego_Maquina SET Perdidas = Perdidas+1 WHERE ID_Chat = ?''', (message.chat.id, ))
            cursor.execute('''SELECT Tipo_Partida, Ganadas, Perdidas FROM Juego_Maquina WHERE ID_Chat = ?''', (message.chat.id, ))
            est = cursor.fetchone()
        if (est[0]==1 and (est[1]==1 or est[2]==1)) or (est[0]==3 and (est[1]==2 or est[2]==2)) or (est[0]==5 and (est[1]==3 or est[2]==3)):
            time.sleep(0.7)
            Cambiar_Estado(message.chat.id, 'INICIO')
            if (est[0]==1 and est[1]==1) or (est[0]==3 and est[1]==2) or (est[0]==5 and est[1]==3):
                teclado = types.ReplyKeyboardRemove(selective=False)
                bot.send_message(message.chat.id, '🎉🎉 *VICTORIA* 🎉🎉\n\n/partida\_vs\_maquina - Inicia una partida contra la máquina.\n/estadisticas - Muestra tus estadísticas generales.', parse_mode='Markdown', reply_markup=teclado)
                if est[0]==1: cursor.execute('''UPDATE Principal SET V1 = V1+1  WHERE ID_Chat = ?''', (message.chat.id, ))
                elif est[0]==3: cursor.execute('''UPDATE Principal SET V3 = V3+1  WHERE ID_Chat = ?''', (message.chat.id, ))
                else: cursor.execute('''UPDATE Principal SET V5 = V5+1  WHERE ID_Chat = ?''', (message.chat.id, ))
            elif (est[0]==1 and est[2]==1) or (est[0]==3 and est[2]==2) or (est[0]==5 and est[2]==3):
                teclado = types.ReplyKeyboardRemove(selective=False)
                bot.send_message(message.chat.id, '😔😔 *DERROTA* 😔😔\n\n/partida\_vs\_maquina - Inicia una partida contra la máquina.\n/estadisticas - Muestra tus estadísticas generales.', parse_mode='Markdown', reply_markup=teclado)
                if est[0]==1: cursor.execute('''UPDATE Principal SET D1 = D1+1  WHERE ID_Chat = ?''', (message.chat.id, ))
                elif est[0]==3: cursor.execute('''UPDATE Principal SET D3 = D3+1  WHERE ID_Chat = ?''', (message.chat.id, ))
                else: cursor.execute('''UPDATE Principal SET D5 = D5+1  WHERE ID_Chat = ?''', (message.chat.id, ))
            cursor.execute('''DELETE FROM Juego_Maquina WHERE ID_Chat = ?''', (message.chat.id, ))
    conexion.commit()
               
# Funciones para sintetizar el código de la base de datos
def Comprobar_Estado(ID_Chat, Estado=None):
    cursor.execute('''SELECT Estado FROM Principal WHERE ID_Chat = ?''',(ID_Chat, ))
    try:
        if Estado == cursor.fetchone()[0]: return True
        else: return False
    except: return 1

def Cambiar_Estado(ID_Chat, Estado):
    cursor.execute('''INSERT OR IGNORE INTO Principal (ID_Chat) VALUES (?)''',(ID_Chat, )) 
    cursor.execute('''UPDATE Principal SET Estado = ? WHERE ID_Chat = ?''',(Estado, ID_Chat))
    conexion.commit()

# Mantenemos el bot a la escucha de mensajes
bot.polling(none_stop=False, interval=0, timeout=10)