#Alerta de crecientes con conectividad GPRS
from SIM800L import Modem     
from hcsr04 import HCSR04     
from machine import deepsleep 
from time import sleep        
import json

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
        
    

#Constantes
distMax = 150.0     #Nivel 0 o fondo del rio
NivelMax = 100.0     #Nivel máximo que genera una alarma
UmbralMax = 5      #Cm de aumento del nivel para generar alarma
UmbralMin = -5     #Cm de disminucion del nivel para generar alarma

#Para tomar control, borrar
sleep (5)

#Crear objetos
sensor = HCSR04(trigger_pin=13, echo_pin=12) #pines del Sensor de distancia

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
    variacion = nivelAnterior - nivelActual

    print ("======================================================")
    print ("Nivel actual:   ", nivelActual)
    print ("Nivel anterior: ", nivelAnterior)
    print ("Variacion:      ", variacion)
    print ("======================================================")

   
    #Comparar
    

if (variacion) < 0:
    print("Aumentó el nivel respecto a la medicion anterior")
    if (variacion > UmbralMax):
        print("EL NIVEL DEL RIO SOBREPASÓ EL UMBRAL MAXIMO")
        Mensaje = ("EL NIVEL DEL RIO AUMENTÓ RAPIDAMENTE DE: ", str(NivelAnt), "Cm A: ", str(Nivel), "Cm")
    else:
        print("El nivel del rio está en aumento")
        Mensaje = "El nivel del rio está en aumento, se encuentra en: ", str(NivelActual), "Cm"
else:
    print("Disminuyó el nivel respecto a la medicion anterior")
    if (variacion > UmbralMin):
        print("EL NIVEL DEL RIO SOBREPASÓ EL UMBRAL MAXIMO")
        Mensaje = "EL NIVEL DEL RIO DISMINUYÓ RAPIDAMENTE A: ", str(NivelActual), "Cm"
        
# Iniciando modem
modem.initialize()
print('Etableciendo conexion...')
print('Signal strength: "{}%"'.format(modem.get_signal_strength()*100))  #Calidad de la conexion a la red

#conectando con el modem
modem.connect(apn='datos.personal.com', user='datos', pwd='datos')       #Conexion del chip con personal
print('\nModem IP address: "{}"'.format(modem.get_ip_addr()))
print(modem.get_signal_strength())

datos={
    "api_key": "5HSXE8X7QV1WFIAP",
    "field1": NivelActual
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
    
print ("A dormir!")
deepsleep(5000)

    