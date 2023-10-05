#Alerta de crecientes con conectividad GPRS

from SIM800L import Modem     
from hcsr04 import HCSR04     
from machine import deepsleep 
from time import sleep        
import json                   

#Constantes
DistMax = 150      #Nivel 0 o fondo del rio
NivelMax = 100     #Nivel máximo que genera una alarma
UmbralMax = 5      #Cm de aumento del nivel para generar alarma
UmbralMin = -5     #Cm de disminucion del nivel para generar alarma

#Crear objetos

sensor = HCSR04(trigger_pin=13, echo_pin=12) #pines del Sensor de distancia

modem = Modem(MODEM_PWKEY_PIN    = 4,
                MODEM_RST_PIN      = 5,
                MODEM_POWER_ON_PIN = 23,    #pines de conexion etre ESP32 con SIM800L
                MODEM_TX_PIN       = 26,
                MODEM_RX_PIN       = 27)

#Empezando mediciones
MedV = 0
MedF = 0    #variables para promediar 100 mediciones
suma = 0


''' Revisar esto debe estar dentro de un def creo
while (valor < 100 or valor2 < 50):
    dist = sensor.distance_cm()
    print (distance)
    if (dist < 250 and dist > 0):
        suma = suma + dist
        MedV = MedV + 1                 #mide 100 veces y promedia
        sleep (.02)
    else:
        print ("nula")
        MedF = MedF + 1
        sleep (.02)       
dist = suma / MedV
Nivel = DistMax - dist
'''

dist = 100 #dummy

#Recuperar distancia medida anteriormente 
distanciaAnterior=0
file = open ("datos.dat", "r")
distanciaAnterior = int(file.read())
file.write (str(dist))
file.close()
print(distanciaAnterior)
NivelAnt = DistMax - distanciaAnterior

Nivel = DistMax - dist  #REvisar si va aca

#Detectar Diferencia
variacion = distanciaAnterior - dist
if (variacion) > 0:
    print("Aumentó el nivel respecto a la medicion anterior")
    if (variacion > UmbralMax):
        print("EL NIVEL DEL RIO SOBREPASÓ EL UMBRAL MAXIMO")
        Mensaje = ("EL NIVEL DEL RIO AUMENTÓ RAPIDAMENTE DE: ", str(NivelAnt), "Cm A: ", str(Nivel), "Cm")
    else:
        print("El nivel del rio está en aumento")
        Mensaje = "El nivel del rio está en aumento, se encuentra en: ", str(Nivel), "Cm"
else:
    print("Disminuyó el nivel respecto a la medicion anterior")
    if (variacion > UmbralMin):
        print("EL NIVEL DEL RIO SOBREPASÓ EL UMBRAL MAXIMO")
        Mensaje = "EL NIVEL DEL RIO DISMINUYÓ RAPIDAMENTE A: ", str(Nivel), "Cm"
        
# Iniciando modem
modem.initialize()
print('Etableciendo conexion...')
print('Signal strength: "{}%"'.format(modem.get_signal_strength()*100))  #Calidad de la conexion a la red

#conectando con el modem
modem.connect(apn='datos.personal.com', user='datos', pwd='datos')       #Conexion del chip con personal
print('\nModem IP address: "{}"'.format(modem.get_ip_addr()))
print(modem.get_signal_strength())

datos={
    "api_key": "7B9AHBOZ1UWKNQAD",
    "field1": Nivel
    }
#GET
#print('\nNow running demo http GET...')
#url = 'http://api.thingspeak.com/update?api_key=7B9AHBOZ1UWKNQAD&field1=' + str(Nivel)
#response = modem.http_request(url, 'GET')
#print('Response status code:', response.status_code)
#print('Response content:', response.content)
#sleep(5)

#POST
print('Now running demo https POST...')
url  = "http://api.thingspeak.com/update"
data = json.dumps(datos)
response = modem.http_request(url, 'POST', data, 'application/json')
print('Response status code:', response.status_code)#    print('Response content:', response.content)

# Disconnect Modem
modem.disconnect()
    
deepsleep(5000)

    