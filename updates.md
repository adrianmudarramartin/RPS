# valpha.0.0 21/01/2022
Añadido archivo de lectura para notificar cambios en las próximas actualizaciones.

# valpha.0.1 22/01/2022
Se añade la función de dar la bienvenida (sólo la primera vez) y añadir al usuario dentro de la base de datos.

WIP -> Añadir un fichero para guardar el token del bot. Este archivo no se subirá al repositorio ya que el token debe ser privado.

WIP -> Añadir función para comprobar estadísticas.

# valpha.0.2 23/01/2022
Se añade la función de estadísticas, donde se pueden comprobar las victorias/derrotas totales jugadas desde el inicio. También se añade la lectura de un archivo para el token del bot.

Extra: Añadidas fechas de salida de cada versión.

WIP -> Añadir función para jugar contra la máquina: Seleccionar cuantas rondas se quieren jugar.

WIP -> Añadir función para jugar contra la máquina: Lectura de mensajes del jugador y respuesta aleatoria del bot para jugar.

# valpha.0.3 24/01/2022
Se añade la función de jugar contra la máquina: Es posible jugar a una ronda, mejor de tres o mejor de cinco todas las partidas que se deseen. Muestra todas las estadísticas completamente.

Nota: Mientras el bot esté en versiones alpha, las bases de datos se borrarán entre una actualización y otra.

Nota: Si se encuentra un fallo, el bot caerá y no volverá a funcionar hasta nuevo aviso.

WIP -> Intentar sintetizar el programa.

WIP -> Configurar Raspberry Pi para que descargue el código de GitHub e inicie el bot cada vez que se reinicie.

# valpha.0.4 25/01/2022
Programa sintetizado (los teclados para Telegram se repetían innecesariamente). Mejorada la calidad de vida a la hora de jugar (El teclado desaparece una vez elegida la opción, no vuelve a aparecer hasta que se vuelva a necesitar). Ahora el programa cambia el repositorio de trabajo una vez iniciado para no subir archivos no deseados a GitHub (La base de datos, el TOKEN del bot o el ID del Admin). Ahora es posible reiniciar la Raspberry mandando el comando /admin al bot (Sólo funciona para el usuario con identificación de administrador). Se incluye un ejecutable para actualizar librerías si se incluye una nueva.

WIP -> Seguir configurando la Raspberry para reiniciarse e iniciar el programa

WIP -> Investigar Node-red, MQTT y la API de Twitter

SEGUNDA ACTUALIZACIÓN: Arreglado un pequeño fallo que no permitía mandar un mensaje al administrador, y por tanto, reiniciar la Raspberry.

# valpha.0.5 27/01/2022
Ahora se puede jugar con un amigo también (añadida otra interfaz completa para el desarrollo de estas partidas).

WIP -> Seguir configurando la Raspberry para reiniciarse e inciar el programa (no lo consigo)

WIP -> Investigar Node-red, MQTT y la API de Twitter

# valpha.0.6 14/02/2022
¡Finalmente! El bot está operativo. Ahora contiene un modo contra random para poder jugar contra cualquier persona. Además, se han realizado todas las interconexiones con Node-red, MQTT y Twitter. Pronto se me ocurrirán cosas para añadir a trabajo futuro. ¡Muchas gracias!