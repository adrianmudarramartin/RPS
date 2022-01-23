# Bot de piedra, papel, tijeras
# Autor: Adrián Mudarra Martín

# Librerías usadas
import telebot
import sqlite3

# Inicialización de la base de datos
conexion= sqlite3.connect('Datos.sqlite', check_same_thread=False)     
cursor= conexion.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Principal (ID_Chat PRIMARY KEY, Nombre TEXT, Usuario TEXT, Estado TEXT, V1 INT, D1 INT, V3 INT, D3 INT, V5 INT, D5 INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Juego_Maquina (ID_Juego_Maquina PRIMARY KEY, ID_Persona SECONDARY KEY REFERENCES Principal(ID_Persona), Numero_Rondas INT, Ganadas INT, Perdidas INT)''')
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
        Derrotas: '''+str(est[0])+'''\n
        *Al mejor de 3* ('''+str(est[2]+est[3])+''' jugadas)
        Victorias: '''+str(est[2])+'''
        Derrotas: '''+str(est[3])+'''\n
        *Al mejor de 5* ('''+str(est[4]+est[5])+''' jugadas)
        Victorias: '''+str(est[4])+'''
        Derrotas: '''+str(est[5])+'''\n''', parse_mode='Markdown')

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