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
import threading

# Prepara el entorno de trabajo fuera del repositorio
os.system('libraries.sh')
os.chdir('..')

# Inicialización de la base de datos
conexion= sqlite3.connect('Datos.sqlite', check_same_thread=False)     
cursor= conexion.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Principal (ID_Chat PRIMARY KEY, Nombre TEXT, Usuario TEXT, Estado TEXT, V1M INT, D1M INT, V3M INT, D3M INT, V5M INT, D5M INT, V1A INT, D1A INT, V3A INT, D3A INT, V5A INT, D5A INT, V5R INT, D5R INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Juego_Maquina (ID_Chat PRIMARY KEY, Tipo_Partida INT, Ganadas INT, Perdidas INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Juego_Amigo (ID_Chat_1 INT, ID_Chat_2 INT, Invitacion TEXT, Tipo_Partida INT, Hora_Actualizacion TEXT, V_1 INT, V_2 INT, Respuesta_1 TEXT, Respuesta_2 TEXT)''')
# cursor.execute('''CREATE TABLE IF NOT EXISTS Juego_Rival (ID_Chat_1 INT, ID_Chat_2 INT, Invitacion TEXT, Tipo_Partida INT, Hora_Actualizacion TEXT, V_1 INT, V_2 INT, Respuesta_1 TEXT, Respuesta_2 TEXT)''')
conexion.commit()

# Información del bot y el ID del administrador
TOKEN = open('bot.txt','r').read() # Archivo que incluye únicamente el token del bot
bot = telebot.TeleBot(TOKEN)
ID_Admin = open('ID_Admin.txt','r').read() # Archivo que incluye únicamente el ID de Telegram del administrador
ID_Rival = None

# REINICIAR - ADMINISTRADOR
@bot.message_handler(commands=['admin'])
def reboot(message):
    if message.chat.id==int(ID_Admin):
        bot.send_message(int(ID_Admin), 'Reiniciando el sistema para actualizar...')
        time.sleep(5)
        os.system('sudo reboot')
# INICIO 
@bot.message_handler(commands=['start'])
def bienvenida(message):
    # print(message.chat.id) # Sirve para obtener la ID del administrador. No se usa cuando el programa está en funcionamiento completo
    if Comprobar_Estado(message.chat.id)==10:
        if message.from_user.username==None:
             bot.send_message(message.chat.id, 'Bienvenid@! Por desgracia, parece que no te has puesto un nombre de usuario en Telegram. Ve a Ajustes de Telegram y cuando estés listo vuelve a usar /start')
        else:
            bot.send_message(message.chat.id, '¡Bienvenid@ al bot de Piedra, Papel, Tijeras! Puedes utilizar los siguientes comandos:\n\n/partida_vs_maquina - Inicia una partida contra la máquina.\n/partida_vs_amigo - Inicia una partida con quien quieras.\n/partida_vs_random - Te empareja con alguien al azar (Mejor de 5)\n/estadisticas - Muestra tus estadísticas generales.')
            if message.from_user.last_name==None:
                cursor.execute('''INSERT OR IGNORE INTO Principal (ID_Chat, Nombre, Usuario, Estado, V1M, D1M, V3M, D3M, V5M, D5M, V1A, D1A, V3A, D3A, V5A, D5A, V5R, D5R) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (message.chat.id, message.from_user.first_name, message.from_user.username, 'INICIO', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            else:
                cursor.execute('''INSERT OR IGNORE INTO Principal (ID_Chat, Nombre, Usuario, Estado, V1M, D1M, V3M, D3M, V5M, D5M, V1A, D1A, V3A, D3A, V5A, D5A, V5R, D5R) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (message.chat.id, message.from_user.first_name+' '+message.from_user.last_name, message.from_user.username, 'INICIO', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        conexion.commit()

# Muestra las estadísticas del jugador
@bot.message_handler(commands=['estadisticas'])
def estadisticas(message):
    if Comprobar_Estado(message.chat.id, 'INICIO'):
        cursor.execute('''SELECT V1M, D1M, V3M, D3M, V5M, D5M, V1A, D1A, V3A, D3A, V5A, D5A, V5R, D5R FROM Principal WHERE ID_Chat = ?''', (message.chat.id, ))
        est = cursor.fetchone() # Números de las estadísticas
        bot.send_message(message.chat.id, '''*TUS ESTADÍSTICAS*\n\n
        *CONTRA LA MÁQUINA*
        *(1)* V: '''+str(est[0])+''' D: '''+str(est[1])+''' ('''+str(est[0]+est[1])+''' jugadas)
        *(3)* V: '''+str(est[2])+''' D: '''+str(est[3])+''' ('''+str(est[2]+est[3])+''' jugadas)
        *(5):* V: '''+str(est[4])+''' D: '''+str(est[5])+''' ('''+str(est[4]+est[5])+''' jugadas)\n
        *CONTRA AMIGOS*
        *(1)* V: '''+str(est[6])+''' D: '''+str(est[7])+''' ('''+str(est[6]+est[7])+''' jugadas)
        *(3)* V: '''+str(est[8])+''' D: '''+str(est[9])+''' ('''+str(est[8]+est[9])+''' jugadas)
        *(5)* V: '''+str(est[10])+''' D: '''+str(est[11])+''' ('''+str(est[10]+est[11])+''' jugadas)\n
        *CONTRA ALEATORIO*
        V: '''+str(est[12])+''' D: '''+str(est[13])+''' ('''+str(est[12]+est[13])+''' jugadas)''', parse_mode='Markdown')


@bot.message_handler(commands=['partida_vs_maquina'])
def numero_rondas_maquina(message):
    if Comprobar_Estado(message.chat.id, 'INICIO'):
        Cambiar_Estado(message.chat.id, 'VS_MÁQUINA_RONDAS')
        bot.send_message(message.chat.id, '¿Qué tipo de partida quieres jugar?', reply_markup=teclado('Ronda'))

@bot.message_handler(commands=['partida_vs_amigo'])
def numero_rondas_maquina(message):
    if Comprobar_Estado(message.chat.id, 'INICIO'):
        Cambiar_Estado(message.chat.id, 'VS_AMIGO_RONDAS')
        bot.send_message(message.chat.id, '¿Qué tipo de partida quieres jugar?', reply_markup=teclado('Ronda'))

@bot.message_handler(commands=['partida_vs_random'])
def numero_rondas_maquina(message):
    global ID_Rival
    if Comprobar_Estado(message.chat.id, 'INICIO'):
        Cambiar_Estado(message.chat.id, 'VS_RANDOM_ESPERANDO')
        if ID_Rival == None:
            bot.send_message(message.chat.id, 'Esperando rival...', reply_markup=teclado('Cancelar'))
            ID_Rival = message.chat.id
        else:
            cursor.execute('''INSERT INTO Juego_Amigo (ID_Chat_1, ID_Chat_2, Tipo_Partida, V_1, V_2) VALUES (?, ?, ?, ?, ?)''', (message.chat.id, ID_Rival, 5, 0, 0))
            Cambiar_Estado(message.chat.id, 'VS_RANDOM_JUGANDO')
            Cambiar_Estado(ID_Rival, 'VS_RANDOM_JUGANDO')
            cursor.execute('''SELECT Nombre FROM Principal WHERE ID_Chat = ?''', (ID_Rival, ))
            nombre = cursor.fetchone()[0]
            bot.send_message(message.chat.id, 'Te enfrentarás a '+nombre+' ,¡Suerte!', reply_markup=teclado('RPS'))
            cursor.execute('''SELECT Usuario FROM Principal WHERE ID_Chat = ?''', (message.chat.id, ))
            nombre = cursor.fetchone()[0]
            bot.send_message(ID_Rival, 'Te enfrentarás a '+nombre+' ,¡Suerte!', reply_markup=teclado('RPS'))
            ID_Rival = None

@bot.message_handler(regexp='.*')
def partida(message):
    # VS RANDOM - Cancelar partida
    global ID_Rival
    if Comprobar_Estado(message.chat.id, 'VS_RANDOM_ESPERANDO') and message.text=='- Cancelar -':
        Cambiar_Estado(message.chat.id, 'INICIO')
        bot.send_message(message.chat.id, 'Cancelado', reply_markup=teclado('Off'))
        ID_Rival = None

    # VS AMIGO - Desarrollo de la partida
    if Comprobar_Estado(message.chat.id, 'VS_AMIGO_RONDAS'):
        if message.text=='Ronda única':
            cursor.execute('''INSERT OR IGNORE INTO Juego_Amigo (ID_Chat_1, Tipo_Partida) VALUES (?, ?)''', (message.chat.id, 1))
            Cambiar_Estado(message.chat.id, 'VS_AMIGO_USUARIO')
            bot.send_message(message.chat.id, 'Has elegido jugar a ronda única. Introduce el usuario de Telegram de tu amigo *(sin incluir @)*', parse_mode='Markdown', reply_markup=teclado('Off'))
        elif message.text=='Al mejor de 3':
            cursor.execute('''INSERT OR IGNORE INTO Juego_Amigo (ID_Chat_1, Tipo_Partida) VALUES (?, ?)''', (message.chat.id, 3))
            Cambiar_Estado(message.chat.id, 'VS_AMIGO_USUARIO')
            bot.send_message(message.chat.id, 'Has elegido jugar al mejor de 3. Introduce el usuario de Telegram de tu amigo *(sin incluir @)*', parse_mode='Markdown', reply_markup=teclado('Off'))
        elif message.text=='Al mejor de 5':
            cursor.execute('''INSERT OR IGNORE INTO Juego_Amigo (ID_Chat_1, Tipo_Partida) VALUES (?, ?)''', (message.chat.id, 5))
            Cambiar_Estado(message.chat.id, 'VS_AMIGO_USUARIO')
            bot.send_message(message.chat.id, 'Has elegido jugar al mejor de 5. Introduce el usuario de Telegram de tu amigo *(sin incluir @)*', parse_mode='Markdown', reply_markup=teclado('Off'))
        elif message.text=='<< Volver':
            bot.send_message(message.chat.id, 'Puedes utilizar los siguientes comandos:\n\n/partida_vs_maquina - Inicia una partida contra la máquina.\n/partida_vs_amigo - Inicia una partida con quien quieras.\n/partida_vs_random - Te empareja con alguien al azar (Mejor de 5)\n/estadisticas - Muestra tus estadísticas generales.', reply_markup=teclado('Off'))
            Cambiar_Estado(message.chat.id, 'INICIO')
        
    elif Comprobar_Estado(message.chat.id, 'VS_AMIGO_USUARIO'):
        cursor.execute('''SELECT COUNT(*) FROM Principal WHERE Usuario = ?''', (message.text,))
        registrado = cursor.fetchone()
        if registrado[0]!=1:
            Cambiar_Estado(message.chat.id, 'INICIO')
            cursor.execute('''DELETE FROM Juego_Amigo WHERE ID_Chat_1 = ?''', (message.chat.id, ))
            bot.reply_to(message, 'Este usuario no existe o no está en la base de datos. Pídele a tu amigo que inicie el bot (/start)', reply_markup=teclado('Off'))
        else:
            cursor.execute('''SELECT Nombre, ID_Chat, Estado FROM Principal WHERE Usuario = ?''', (message.text,))
            info_invitado = cursor.fetchone()
            if info_invitado[2]=='INICIO':
                Cambiar_Estado(info_invitado[1],'VS_AMIGO_INVITADO') 
                Cambiar_Estado(message.chat.id, 'VS_AMIGO_INVITANDO')
                cursor.execute('''SELECT Nombre, Usuario FROM Principal WHERE ID_Chat = ?''', (message.chat.id,))
                info_anfitrion = cursor.fetchone()
                cursor.execute('''UPDATE Juego_Amigo SET ID_Chat_2 = ?, Invitacion = 'PENDIENTE' WHERE ID_Chat_1 = ?''', (info_invitado[1], message.chat.id ))
                cursor.execute('''SELECT Tipo_Partida FROM Juego_Amigo WHERE ID_Chat_1 = ?''', (message.chat.id, ))
                tipo_partida = cursor.fetchone()
                bot.reply_to(message, 'Petición enviada a '+info_invitado[0]+'. Esperando respuesta...', reply_markup=teclado('Cancelar'))
                bot.send_message(info_invitado[1], 'Has recibido una invitación de '+info_anfitrion[0]+' (@'+info_anfitrion[1]+') para jugar una partida al mejor de '+str(tipo_partida[0])+'.\n\n¿Aceptas la invitación?', reply_markup=teclado('Aceptar'))
            else:
                Cambiar_Estado(message.chat.id, 'INICIO')
                bot.send_message(message.chat.id, 'El usuario está ahora mismo en partida, inténtalo más tarde.')
                cursor.execute('''DELETE FROM Juego_Amigo WHERE ID_Chat_1 = ?''', (message.chat.id, ))
    
    elif Comprobar_Estado(message.chat.id, 'VS_AMIGO_INVITANDO'):
        if message.text=='- Cancelar -':
            cursor.execute('''SELECT ID_Chat_2 FROM Juego_Amigo WHERE ID_Chat_1 = ?''', (message.chat.id,))
            id_invitado = cursor.fetchone()
            cursor.execute('''SELECT Tipo_Partida FROM Juego_Amigo WHERE ID_Chat_1 = ?''', (message.chat.id, ))
            tipo_partida = cursor.fetchone()
            Cambiar_Estado(message.chat.id, 'INICIO')
            Cambiar_Estado(id_invitado[0], 'INICIO')
            bot.send_message(message.chat.id, 'Se ha cancelado la solicitud.', reply_markup=teclado('Off'))
            bot.send_message(id_invitado[0], 'Han cancelado la solicitud de partida. ¿Quizás más tarde?', reply_markup=teclado('Off'))

    
    elif Comprobar_Estado(message.chat.id, 'VS_AMIGO_INVITADO'):
        cursor.execute('''SELECT ID_Chat_1 FROM Juego_Amigo WHERE ID_Chat_2 = ?''', (message.chat.id,))
        id_anfitrion = cursor.fetchone()
        if message.text=='Aceptar':
            cursor.execute('''UPDATE Juego_Amigo SET Invitacion = 'ACEPTADA', Hora_Actualizacion = ?, V_1 = 0, V_2 = 0 WHERE ID_Chat_2 = ?''', (datetime.now().strftime("%H:%M:%S"), message.chat.id, ))
            Cambiar_Estado(message.chat.id, 'VS_AMIGO_JUGANDO')
            Cambiar_Estado(id_anfitrion[0], 'VS_AMIGO_JUGANDO')
            bot.send_message(message.chat.id, 'Se ha aceptado la solicitud, ¡que comience la partida!', reply_markup=teclado('RPS'))
            bot.send_message(id_anfitrion[0], 'Tu solicitud ha sido aceptada, ¡que comience la partida!', reply_markup=teclado('RPS'))
        else:
            Cambiar_Estado(message.chat.id, 'INICIO')
            Cambiar_Estado(id_anfitrion[0], 'INICIO')
            bot.send_message(message.chat.id, 'Se ha rechazado la solicitud.', reply_markup=teclado('Off'))
            bot.send_message(id_anfitrion[0], 'Tu solicitud ha sido rechazada, ¡qué pena!', reply_markup=teclado('Off'))

    elif Comprobar_Estado(message.chat.id, 'VS_AMIGO_JUGANDO') or Comprobar_Estado(message.chat.id, 'VS_RANDOM_JUGANDO'):
        cursor.execute('''UPDATE Juego_Amigo SET Respuesta_1 = ? WHERE ID_Chat_1 = ?''', (message.text, message.chat.id))
        cursor.execute('''UPDATE Juego_Amigo SET Respuesta_2 = ? WHERE ID_Chat_2 = ?''', (message.text, message.chat.id))
        cursor.execute('''SELECT ID_Chat_1, ID_Chat_2, V_1, V_2, Respuesta_1, Respuesta_2, Tipo_Partida FROM Juego_Amigo WHERE ID_Chat_1 = ? OR ID_Chat_2 = ?''', (message.chat.id, message.chat.id))
        info = cursor.fetchone()
        #print(info)
        if info[4]==None:
            bot.send_message(info[0],'*Tu rival ha enviado su respuesta.*', parse_mode='Markdown')
            bot.reply_to(message,'Respuesta enviada. Esperando respuesta del rival...', reply_markup=teclado('Off'))
        elif info[5]==None:
            bot.send_message(info[1],'*Tu rival ha enviado su respuesta.*', parse_mode='Markdown')
            bot.reply_to(message,'Respuesta enviada. Esperando respuesta del rival...', reply_markup=teclado('Off'))
        if info[4]!=None and info[5]!=None:
            mensaje_bot_1 = bot.send_message(info[0], '.')
            mensaje_bot_2 = bot.send_message(info[1], '.')
            time.sleep(0.1)
            bot.edit_message_text('..', info[0], mensaje_bot_1.id)
            bot.edit_message_text('..', info[1], mensaje_bot_2.id)
            time.sleep(0.1)
            bot.edit_message_text('...', info[0], mensaje_bot_1.id)
            bot.edit_message_text('...', info[1], mensaje_bot_2.id)
            time.sleep(0.15)
            bot.edit_message_text(info[5], info[0], mensaje_bot_1.id)
            bot.edit_message_text(info[4], info[1], mensaje_bot_2.id)
            time.sleep(0.7)
            if info[4]==info[5]:
                pass
            elif (info[4]=='🥌 Piedra 🥌' and info[5]=='✂️ Tijeras ✂️') or (info[4]=='📄 Papel 📄' and info[5]=='🥌 Piedra 🥌') or (info[4]=='✂️ Tijeras ✂️' and info[5]=='📄 Papel 📄'):
                cursor.execute('''UPDATE Juego_Amigo SET V_1=V_1+1 WHERE ID_Chat_1 = ?''', (info[0],))
                cursor.execute('''SELECT ID_Chat_1, ID_Chat_2, V_1, V_2, Respuesta_1, Respuesta_2, Tipo_Partida FROM Juego_Amigo WHERE ID_Chat_1 = ?''', (info[0], ))
                info = cursor.fetchone()
            else:
                cursor.execute('''UPDATE Juego_Amigo SET V_2=V_2+1 WHERE ID_Chat_1 = ?''', (info[0],))
                cursor.execute('''SELECT ID_Chat_1, ID_Chat_2, V_1, V_2, Respuesta_1, Respuesta_2, Tipo_Partida FROM Juego_Amigo WHERE ID_Chat_1 = ?''', (info[0], ))
                info = cursor.fetchone()
            if (info[6]==1 and (info[2]==1 or info[3]==1)) or (info[6]==3 and (info[2]==2 or info[3]==2)) or (info[6]==5 and (info[2]==3 or info[3]==3)):
                time.sleep(0.1)
                Cambiar_Estado(info[0], 'INICIO')
                Cambiar_Estado(info[1], 'INICIO')
                if (info[6]==1 and info[2]==1) or (info[6]==3 and info[2]==2) or (info[6]==5 and info[2]==3):
                    bot.send_message(info[0], '🎉🎉 *VICTORIA* 🎉🎉     ('+str(info[2])+' - '+str(info[3])+')\n\n/partida\_vs\_maquina - Inicia una partida contra la máquina.\n/partida\_vs\_amigo - Inicia una partida con quien quieras.\n/partida\_vs\_random - Te empareja con alguien al azar (Mejor de 5)\n/estadisticas - Muestra tus estadísticas generales.', parse_mode='Markdown', reply_markup=teclado('Off'))
                    bot.send_message(info[1], '😔😔 *DERROTA* 😔😔     ('+str(info[3])+' - '+str(info[2])+')\n\n/partida\_vs\_maquina - Inicia una partida contra la máquina.\n/partida\_vs\_amigo - Inicia una partida con quien quieras.\n/partida\_vs\_random - Te empareja con alguien al azar (Mejor de 5)\n/estadisticas - Muestra tus estadísticas generales.', parse_mode='Markdown', reply_markup=teclado('Off'))
                    if info[6]==1:
                        cursor.execute('''UPDATE Principal SET V1A = V1A+1  WHERE ID_Chat = ?''', (info[0], ))
                        cursor.execute('''UPDATE Principal SET D1A = D1A+1  WHERE ID_Chat = ?''', (info[1], ))
                    elif info[6]==3: 
                        cursor.execute('''UPDATE Principal SET V3A = V3A+1  WHERE ID_Chat = ?''', (info[0], ))
                        cursor.execute('''UPDATE Principal SET D3A = D3A+1  WHERE ID_Chat = ?''', (info[1], ))
                    else: 
                        if Comprobar_Estado(message.chat.id, 'VS_AMIGO_JUGANDO'):
                            cursor.execute('''UPDATE Principal SET V5A = V5A+1  WHERE ID_Chat = ?''', (info[0], ))
                            cursor.execute('''UPDATE Principal SET D5A = D5A+1  WHERE ID_Chat = ?''', (info[1], ))
                        else:
                            cursor.execute('''UPDATE Principal SET V5R = V5R+1  WHERE ID_Chat = ?''', (info[0], ))
                            cursor.execute('''UPDATE Principal SET D5R = D5R+1  WHERE ID_Chat = ?''', (info[1], ))

                elif (info[6]==1 and info[3]==1) or (info[6]==3 and info[3]==2) or (info[6]==5 and info[3]==3):
                    bot.send_message(info[1], '🎉🎉 *VICTORIA* 🎉🎉     ('+str(info[3])+' - '+str(info[2])+')\n\n/partida\_vs\_maquina - Inicia una partida contra la máquina.\n/partida\_vs\_amigo - Inicia una partida con quien quieras.\n/partida\_vs\_random - Te empareja con alguien al azar (Mejor de 5)\n/estadisticas - Muestra tus estadísticas generales.', parse_mode='Markdown', reply_markup=teclado('Off'))
                    bot.send_message(info[0], '😔😔 *DERROTA* 😔😔     ('+str(info[2])+' - '+str(info[3])+')\n\n/partida\_vs\_maquina - Inicia una partida contra la máquina.\n/partida\_vs\_amigo - Inicia una partida con quien quieras.\n/partida\_vs\_random - Te empareja con alguien al azar (Mejor de 5)\n/estadisticas - Muestra tus estadísticas generales.', parse_mode='Markdown', reply_markup=teclado('Off'))
                    if info[6]==1:
                        cursor.execute('''UPDATE Principal SET V1A = V1A+1  WHERE ID_Chat = ?''', (info[1], ))
                        cursor.execute('''UPDATE Principal SET D1A = D1A+1  WHERE ID_Chat = ?''', (info[0], ))  
                    elif info[6]==3: 
                        cursor.execute('''UPDATE Principal SET V3A = V3A+1  WHERE ID_Chat = ?''', (info[1], ))
                        cursor.execute('''UPDATE Principal SET D3A = D3A+1  WHERE ID_Chat = ?''', (info[0], ))
                    else: 
                        if Comprobar_Estado(message.chat.id, 'VS_AMIGO_JUGANDO'):
                            cursor.execute('''UPDATE Principal SET V5A = V5A+1  WHERE ID_Chat = ?''', (info[1], ))
                            cursor.execute('''UPDATE Principal SET D5A = D5A+1  WHERE ID_Chat = ?''', (info[0], ))
                        else:
                            cursor.execute('''UPDATE Principal SET V5A = V5R+1  WHERE ID_Chat = ?''', (info[1], ))
                            cursor.execute('''UPDATE Principal SET D5A = D5R+1  WHERE ID_Chat = ?''', (info[0], ))
                cursor.execute('''DELETE FROM Juego_Amigo WHERE ID_Chat_1 = ?''', (info[0], ))
            else:
                if info[4]==info[5]:
                    bot.send_message(info[0], 'Empate. Elige otra vez     ('+str(info[2])+' - '+str(info[3])+')', reply_markup=teclado('RPS'))
                    bot.send_message(info[1], 'Empate. Elige otra vez     ('+str(info[3])+' - '+str(info[2])+')', reply_markup=teclado('RPS'))
                elif (info[4]=='🥌 Piedra 🥌' and info[5]=='✂️ Tijeras ✂️') or (info[4]=='📄 Papel 📄' and info[5]=='🥌 Piedra 🥌') or (info[4]=='✂️ Tijeras ✂️' and info[5]=='📄 Papel 📄'):
                    bot.send_message(info[0], 'Ganas.     ('+str(info[2])+' - '+str(info[3])+')', reply_markup=teclado('RPS'))
                    bot.send_message(info[1], 'Pierdes.     ('+str(info[3])+' - '+str(info[2])+')', reply_markup=teclado('RPS'))
                else:
                    bot.send_message(info[1], 'Ganas.     ('+str(info[3])+' - '+str(info[2])+')', reply_markup=teclado('RPS'))
                    bot.send_message(info[0], 'Pierdes.     ('+str(info[2])+' - '+str(info[3])+')', reply_markup=teclado('RPS'))
                cursor.execute('''UPDATE Juego_Amigo SET Respuesta_1 = ?, Respuesta_2 = ? WHERE ID_Chat_1 = ?''', (None, None, info[0]))

    # VS MÁQUINA - Desarrollo de la partida        
    elif Comprobar_Estado(message.chat.id, 'VS_MÁQUINA_RONDAS'):
        Cambiar_Estado(message.chat.id, 'VS_MÁQUINA_JUGANDO')
        if message.text=='Ronda única':
            bot.reply_to(message, 'Has elegido jugar a ronda única. ¡Suerte!', reply_markup=teclado('RPS'))
            cursor.execute('''INSERT OR IGNORE INTO Juego_Maquina (ID_Chat, Tipo_Partida, Ganadas, Perdidas) VALUES (?, ?, ?, ?)''', (message.chat.id, 1, 0, 0))
        elif message.text=='Al mejor de 3':
            bot.reply_to(message, 'Has elegido jugar a tres rondas. ¡Suerte!', reply_markup=teclado('RPS'))
            cursor.execute('''INSERT OR IGNORE INTO Juego_Maquina (ID_Chat, Tipo_Partida, Ganadas, Perdidas) VALUES (?, ?, ?, ?)''', (message.chat.id, 3, 0, 0))
        elif message.text=='Al mejor de 5':
            bot.reply_to(message, 'Has elegido jugar cinco rondas ¡Suerte!', reply_markup=teclado('RPS'))
            cursor.execute('''INSERT OR IGNORE INTO Juego_Maquina (ID_Chat, Tipo_Partida, Ganadas, Perdidas) VALUES (?, ?, ?, ?)''', (message.chat.id, 5, 0, 0))
        elif message.text=='<< Volver':
            bot.send_message(message.chat.id, 'Puedes utilizar los siguientes comandos:\n\n/partida_vs_maquina - Inicia una partida contra la máquina.\n/partida_vs_amigo - Inicia una partida con quien quieras.\n/partida_vs_random - Te empareja con alguien al azar (Mejor de 5)\n/estadisticas - Muestra tus estadísticas generales.', reply_markup=teclado('Off'))
            Cambiar_Estado(message.chat.id, 'INICIO')
    
    elif Comprobar_Estado(message.chat.id, 'VS_MÁQUINA_JUGANDO'):
        cursor.execute('''SELECT Tipo_Partida, Ganadas, Perdidas FROM Juego_Maquina WHERE ID_Chat = ?''', (message.chat.id, ))
        est = cursor.fetchone()
        maquina = random.choice(['🥌 Piedra 🥌', '📄 Papel 📄', '✂️ Tijeras ✂️'])
        mensaje_bot = bot.send_message(message.chat.id, '-', reply_markup=teclado('Off'))
        bot.delete_message(message.chat.id, mensaje_bot.id) 
        mensaje_bot = bot.reply_to(message, 'La máquina dice')
        bot.edit_message_text('La máquina dice.', message.chat.id, mensaje_bot.id)
        time.sleep(0.1)
        bot.edit_message_text('La máquina dice..', message.chat.id, mensaje_bot.id)
        time.sleep(0.1)
        bot.edit_message_text('La máquina dice...', message.chat.id, mensaje_bot.id)
        time.sleep(0.1)
        bot.edit_message_text('La máquina dice...\n\n'+maquina, message.chat.id, mensaje_bot.id)
        time.sleep(0.1)
        if message.text==maquina:
            pass
        elif (message.text=='🥌 Piedra 🥌' and maquina=='✂️ Tijeras ✂️') or (message.text=='📄 Papel 📄' and maquina=='🥌 Piedra 🥌') or (message.text=='✂️ Tijeras ✂️' and maquina=='📄 Papel 📄'):
            cursor.execute('''UPDATE Juego_Maquina SET Ganadas = Ganadas+1 WHERE ID_Chat = ?''', (message.chat.id, ))
            cursor.execute('''SELECT Tipo_Partida, Ganadas, Perdidas FROM Juego_Maquina WHERE ID_Chat = ?''', (message.chat.id, ))
            est = cursor.fetchone()
        else:
            cursor.execute('''UPDATE Juego_Maquina SET Perdidas = Perdidas+1 WHERE ID_Chat = ?''', (message.chat.id, ))
            cursor.execute('''SELECT Tipo_Partida, Ganadas, Perdidas FROM Juego_Maquina WHERE ID_Chat = ?''', (message.chat.id, ))
            est = cursor.fetchone()

        if (est[0]==1 and (est[1]==1 or est[2]==1)) or (est[0]==3 and (est[1]==2 or est[2]==2)) or (est[0]==5 and (est[1]==3 or est[2]==3)):
            time.sleep(0.1)
            Cambiar_Estado(message.chat.id, 'INICIO')
            if (est[0]==1 and est[1]==1) or (est[0]==3 and est[1]==2) or (est[0]==5 and est[1]==3):
                bot.send_message(message.chat.id, '🎉🎉 *VICTORIA* 🎉🎉     ('+str(est[1])+' - '+str(est[2])+')\n\n/partida\_vs\_maquina - Inicia una partida contra la máquina.\n/partida\_vs\_amigo - Inicia una partida con quien quieras.\n/partida\_vs\_random - Te empareja con alguien al azar (Mejor de 5)\n/estadisticas - Muestra tus estadísticas generales.', parse_mode='Markdown', reply_markup=teclado('Off'))
                if est[0]==1: cursor.execute('''UPDATE Principal SET V1M = V1M+1  WHERE ID_Chat = ?''', (message.chat.id, ))
                elif est[0]==3: cursor.execute('''UPDATE Principal SET V3M = V3M+1  WHERE ID_Chat = ?''', (message.chat.id, ))
                else: cursor.execute('''UPDATE Principal SET V5M = V5M+1  WHERE ID_Chat = ?''', (message.chat.id, ))
            elif (est[0]==1 and est[2]==1) or (est[0]==3 and est[2]==2) or (est[0]==5 and est[2]==3):
                bot.send_message(message.chat.id, '😔😔 *DERROTA* 😔😔     ('+str(est[1])+' - '+str(est[2])+')\n\n/partida\_vs\_maquina - Inicia una partida contra la máquina.\n/partida\_vs\_amigo - Inicia una partida con quien quieras.\n/partida\_vs\_random - Te empareja con alguien al azar (Mejor de 5)\n/estadisticas - Muestra tus estadísticas generales.', parse_mode='Markdown', reply_markup=teclado('Off'))
                if est[0]==1: cursor.execute('''UPDATE Principal SET D1M = D1M+1  WHERE ID_Chat = ?''', (message.chat.id, ))
                elif est[0]==3: cursor.execute('''UPDATE Principal SET D3M = D3M+1  WHERE ID_Chat = ?''', (message.chat.id, ))
                else: cursor.execute('''UPDATE Principal SET D5M = D5M+1  WHERE ID_Chat = ?''', (message.chat.id, ))
            cursor.execute('''DELETE FROM Juego_Maquina WHERE ID_Chat = ?''', (message.chat.id, ))
        else:
            if message.text==maquina:
                bot.send_message(message.chat.id, 'Empate. Elige otra vez     ('+str(est[1])+ ' - '+str(est[2])+')', reply_markup=teclado('RPS'))
            elif (message.text=='🥌 Piedra 🥌' and maquina=='✂️ Tijeras ✂️') or (message.text=='📄 Papel 📄' and maquina=='🥌 Piedra 🥌') or (message.text=='✂️ Tijeras ✂️' and maquina=='📄 Papel 📄'):
                bot.send_message(message.chat.id, 'Ganas.     ('+str(est[1])+ ' - '+str(est[2])+')', reply_markup=teclado('RPS'))
            else:
                bot.send_message(message.chat.id, 'Pierdes.     ('+str(est[1])+ ' - '+str(est[2])+')', reply_markup=teclado('RPS'))
    conexion.commit()
               
# Funciones para sintetizar el código de la base de datos
def Comprobar_Estado(ID_Chat, Estado=None):
    cursor.execute('''SELECT Estado FROM Principal WHERE ID_Chat = ?''',(ID_Chat, ))
    try:
        if Estado == cursor.fetchone()[0]: return True
        else: return False
    except: return 10

def Cambiar_Estado(ID_Chat, Estado):
    cursor.execute('''INSERT OR IGNORE INTO Principal (ID_Chat) VALUES (?)''',(ID_Chat, )) 
    cursor.execute('''UPDATE Principal SET Estado = ? WHERE ID_Chat = ?''',(Estado, ID_Chat))
    conexion.commit()

# Teclados de telegram utilizados
def teclado(tipo):
    teclado = 0
    if tipo=='Ronda':
        teclado = types.ReplyKeyboardMarkup(row_width=1)
        ronda_1 = types.KeyboardButton('Ronda única')
        ronda_3 = types.KeyboardButton('Al mejor de 3')
        ronda_5 = types.KeyboardButton('Al mejor de 5')
        volver = types.KeyboardButton('<< Volver')
        teclado.add(ronda_1, ronda_3, ronda_5, volver)
    elif tipo=='RPS':
        teclado = types.ReplyKeyboardMarkup(row_width=1)
        piedra = types.KeyboardButton('🥌 Piedra 🥌')
        papel = types.KeyboardButton('📄 Papel 📄')
        tijeras = types.KeyboardButton('✂️ Tijeras ✂️')
        teclado.add(piedra, papel, tijeras)
    elif tipo=='Aceptar':
        teclado = types.ReplyKeyboardMarkup(row_width=2)
        aceptar = types.KeyboardButton('Aceptar')
        rechazar = types.KeyboardButton('Rechazar')
        teclado.add(aceptar, rechazar)
    elif tipo=='Cancelar':
        teclado = types.ReplyKeyboardMarkup(row_width=1)
        cancelar = types.KeyboardButton('- Cancelar -')
        teclado.add(cancelar)
    elif tipo=='Off':
        teclado = types.ReplyKeyboardRemove(selective=False)
    return teclado


bot.send_message(int(ID_Admin), 'El programa se encuentra operativo.')

# Hebra para cliente MQTT
def hebra_mqtt():
    def on_message(client, data, msg):
        cursor.execute('''SELECT Nombre FROM Principal WHERE V1M=(SELECT MAX(V1M) FROM Principal)''')
        nombre = cursor.fetchone()[0]
        client.publish('V1M',nombre)
        cursor.execute('''SELECT Nombre FROM Principal WHERE V1M=(SELECT MAX(V3M) FROM Principal)''')
        nombre = cursor.fetchone()[0]
        client.publish('V3M',nombre)
        cursor.execute('''SELECT Nombre FROM Principal WHERE V1M=(SELECT MAX(V5M) FROM Principal)''')
        nombre = cursor.fetchone()[0]
        client.publish('V5M',nombre)
        cursor.execute('''SELECT Nombre FROM Principal WHERE V1A=(SELECT MAX(V1A) FROM Principal)''')
        nombre = cursor.fetchone()[0]
        client.publish('V1A',nombre)
        cursor.execute('''SELECT Nombre FROM Principal WHERE V3A=(SELECT MAX(V3A) FROM Principal)''')
        nombre = cursor.fetchone()[0]
        client.publish('V3A',nombre)
        cursor.execute('''SELECT Nombre FROM Principal WHERE V5A=(SELECT MAX(V5A) FROM Principal)''')
        nombre = cursor.fetchone()[0]
        client.publish('V5A',nombre)
        cursor.execute('''SELECT Nombre FROM Principal WHERE V5R=(SELECT MAX(V5R) FROM Principal)''')
        nombre = cursor.fetchone()[0]
        client.publish('V5R',nombre)
    
    client = mqtt.Client("")
    client.on_message = on_message
    client.username_pw_set(username="pi", password="patatas")
    client.connect("localhost", 1883, 60)
    client.subscribe("request")
    client.loop_forever()
hebra = threading.Thread(target=hebra_mqtt)
hebra.start()

# Mantenemos el bot a la escucha de mensajes
bot.polling(none_stop=False, interval=0, timeout=300)