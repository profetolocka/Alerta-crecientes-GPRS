# ---------------------
# SIM800L example usage
# ---------------------

from SIM800L import Modem
from hcsr04 import HCSR04
from machine import deepsleep
from time import sleep
import json

sensor = HCSR04(trigger_pin=13, echo_pin=12)

def example_usage():
    print('Starting up...')

    # Create new modem object on the right Pins
    modem = Modem(MODEM_PWKEY_PIN    = 4,
                  MODEM_RST_PIN      = 5,
                  MODEM_POWER_ON_PIN = 23,
                  MODEM_TX_PIN       = 26,
                  MODEM_RX_PIN       = 27)

    # Initialize the modem
    modem.initialize()

    # Run some optional diagnostics
    #print('Modem info: "{}"'.format(modem.get_info()))
    #print('Network scan: "{}"'.format(modem.scan_networks()))
    #print('Current network: "{}"'.format(modem.get_current_network()))
    #print('Signal strength: "{}%"'.format(modem.get_signal_strength()*100))

    # Connect the modem
    modem.connect(apn='datos.personal.com', user='datos', pwd='datos') #leave username and password empty if your network don't require them
    print('\nModem IP address: "{}"'.format(modem.get_ip_addr()))
    
    distance2 = sensor.distance_cm()
    suma = 0
    valProm = 0
    valor = 0
    valProg = 0
    valProg2 = 0
    medProg = 0
    nivel = 0
    print ("empezando la medicion")
    while valor < 5:
        distance = sensor.distance_cm()
        print (distance)
        if (distance < 250 and distance > 0):
            suma = suma + distance
            valor = valor + 1
            sleep (1)
        else:
            print ("nula")
            sleep (1)
    valor = 0       
    distance = suma / 6
    suma = 0
    print ("prom", distance)
    if (distance <= 100):
        valor = 0
        valor2 = 0
        med = 0
        while valor < 5:
            
            distance = sensor.distance_cm() 
            if (distance <= 100):
                med = med + 1
                valor = valor + 1
                sleep(5)
            elif (distance > 100):
                valor2 = 5 - valor
                valor = valor + valor2
            else:
                print ("medicion erronea")
                sleep(5)
        valor = 0       
        nivel = 150 - distance
        
        if (med >= 5):
            print ("ATENCION, el nivel del agua sobrepasó el limite: ", nivel, "cm")
            sleep(5)
        else:
            print ("caudal normal, nivel: ", nivel, "cm")
            sleep(5)
                
        
    elif (distance > 100 and distance < 150):
        nivel = 150 - distance
        print ("nivel de agua normal: ", nivel)
        if (distance < distance2):
            valProg = valProg + 1
            distance2 = distance
        else:
            valProg = 0
        if (valProg >= 5):
            nivel = 150 - distance
            print ("el nivel está incrementando en las ultimas 5 mediciones: ", nivel, "cm")
            sleep(5)
        else:
            print ("0")
            sleep(5)
    else:
        print("medicion erronea")
        sleep(1)
    
    Nivel = nivel
    # Example GET
    print('\nNow running demo http GET...')
    url = 'http://api.thingspeak.com/update?api_key=NW2MTDR0MKCY6VL2&field1=' + str(Nivel)
    response = modem.http_request(url, 'GET')
    print('Response status code:', response.status_code)
    print('Response content:', response.content)
    sleep(5)
    print("me voy por 5 segundos...") 
    Nivel = 0
    # Example POST
#    print('Now running demo https POST...')
#    url  = 
#    data = json.dumps({'myparameter': 42})
#    response = modem.http_request(url, 'POST', data, 'application/json')
#    print('Response status code:', response.status_code)
#    print('Response content:', response.content)
    

    # Disconnect Modem
    modem.disconnect()
    
try:
    example_usage()
    deepsleep(5000)
except:
    deepsleep(5000)
    print ("Hubo un error")
    