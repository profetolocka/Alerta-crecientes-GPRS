#Alerta de crecientes con conectividad GPRS
from SIM800L import Modem 
#import SIM800_SMS

from hcsr04 import HCSR04     
from machine import deepsleep, ADC, Pin
from time import sleep        
import json

#Leer credenciales 
from credenciales import secretos

#API Key de Telegram
telegramAPI = secretos['TL_API_KEY']


'''
Medición de distancias promediada.
Hace 16 lecturas y promedia las lecturas válidas.
Descarta los valores que sean superiores al parámetro de entrada "max"
(a veces la librería que uso devuelve 250 como medida errónea)
Si no puede hacer ninguna lectura válida genera un error
Devuelve la distancia como un valor entero en cm
'''
def medirDistancia (max):
    sumaDistancias=0
    cantValidas=0
    for (medida) in range (16):
        try:
            d = sensor.distance_cm ()
            #print ("medicion=",d)
            sleep (0.1)
        except:
            d = max
            #print ("Err")

        if (d < max):
            sumaDistancias = sumaDistancias + d
            cantValidas +=1
            #print ("cant=",medida)
    
    if (cantValidas>0):
        return (int(sumaDistancias/cantValidas))
    else:
        raise OSError('Error en sensor distancias')
    
'''
Medición del nivel. Pasa la distancia a valores de nivel
Genera error si no logra una medida válida
'''
def medirNivel (max):
    try:
        distancia = medirDistancia (max)
        print ("Dist=",distancia)
        sleep (0.5)
        nivel = max - distancia
        return (int(nivel))

    except:
        raise OSError ("Error al medir nivel")

'''
Se va al modo de bajo consumo hasta la siguiente lectura
'''
def modoBajoConsumo (tiempo):

    print ("A dormir!")
    deepsleep(tiempo)

'''
Prueba de Telegram via IFTTT
'''
def reportaTelegram (texto):
    
    try:
        #Inicializando modem
        modem.initialize()
        print('Estableciendo conexion...')
        print('Señal: "{}%"'.format(modem.get_signal_strength()*100))  #Calidad de la conexion a la red

        #conectando con el modem
        modem.connect(apn='datos.personal.com', user='datos', pwd='datos')       #Conexion del chip con personal
        print('\nModem IP address: "{}"'.format(modem.get_ip_addr()))

        url= 'http://maker.ifttt.com/trigger/Sensor_nivel/with/key/'+telegramAPI+'?value1='+texto
        response = modem.http_request(url, 'GET')
        print('Response status code:', response.status_code)
        print('Response content:', response.content)
    
    except:
        print ("Algún error con el modem")
        #Desconectar modem
        modem.disconnect()

'''
Reporte de Alarmas
'''
def reportarAlarma (tipoAlarma, nivel):
    
    #Reporta el nivel actual
    nivelBateria = pinBateria.read_uv()/500000
    print ("Batería: ", nivelBateria)

    reportaTelegram ("ALARMA "+tipoAlarma+" Nivel="+str(nivel)+" Bat="+str(nivelBateria)) 

#Constantes
distMax = 150.0     		#Nivel 0 o fondo del rio
nivelMax = 100.0     		#Nivel máximo absoluto que genera una alarma
variacionCreciente = 5      #Cm de aumento del nivel para generar alarma
variacionDecreciente = 5    #Cm de disminucion del nivel para generar alarma


tiempoReporte = 1000*60*5  #Tiempo entre reportes

#Para tomar control, borrar
sleep (5) 

#Crear objetos
sensor = HCSR04(trigger_pin=13, echo_pin=12) #pines del Sensor de distancia

pinBateria = ADC (Pin(34))

modem = Modem(MODEM_PWKEY_PIN    = 4,
                MODEM_RST_PIN      = 5,
                MODEM_POWER_ON_PIN = 23,    #pines de conexion etre ESP32 con SIM800L
                MODEM_TX_PIN       = 26,
                MODEM_RX_PIN       = 27)


#Medir el nivel actual del agua
try:
    #Intenta medir el nivel del río
    nivelActual = medirNivel (distMax)
    
except:
    print ("Error al medir nivel!")
    #A dormir para probar luego
    modoBajoConsumo (tiempoReporte)
    
else:
    print ("Nivel=",nivelActual)
    
    #Recuperar el nivel de la medición anterior
    #try:
    
    try:
        #Intenta abrir el archivo de datos para leer
        file = open ("datos.dat", "r")
    
    except:
        #Si el archivo no existe se fija nivel a cero
        print ("Archivo no existe, inicializa a cero")
        nivelAnterior=0
        
    else:
        #Leer nivelAnterior desde el archivo de datos
        nivelAnterior = int(file.read()) 
        print ("Nivel anterior=",nivelAnterior)
        file.close()

    #Grabar el nivel actual (Actualizar)
    file = open ("datos.dat", "w")     #Sobreescribir
    file.write (str(nivelActual))
    file.close() 

    #Calcular Diferencia
    variacion = nivelActual - nivelAnterior

    print ("======================================================")
    print ("Nivel actual:   ", nivelActual)
    print ("Nivel anterior: ", nivelAnterior)
    print ("Variacion:      ", variacion)
    print ("======================================================")



    #Comparar
    #Si la variacion de nivel > variacion Creciente reportar alarma Creciente
    #Si la variacion de nivel > variacion Decreciente reportar alarma Decreciente
    #Si el nivel actual > nivelMax reportar alarma Nivel Maximo

    if (nivelActual > nivelMax):
        print ("ALARMA Nivel máximo")
        reportarAlarma ("NIVEL MAX", nivelActual)
        
    if ((variacion > 0) and (variacion > variacionCreciente)):
        print ("ALARMA Creciente")
        reportarAlarma ("CRECIENTE", nivelActual)
        
    if ((variacion < 0) and (variacion < variacionDecreciente)):
        print ("ALARMA Decreciente")
        reportarAlarma ("DECRECIENTE", nivelActual)
      
    modoBajoConsumo (tiempoReporte)


    