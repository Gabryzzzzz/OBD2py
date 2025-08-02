import board
import adafruit_mpu6050
import busio
import time

# Inizializza l'interfaccia I2C usando i pin del Raspberry Pi
# 'board.SCL' e 'board.SDA' sono i nomi standard dei pin I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Crea un oggetto MPU6050. Il sensore è pronto per essere usato.
mpu = adafruit_mpu6050.MPU6050(i2c)

accelerazione = None
giroscopio = None
temperatura = None



def get_info():
    return accelerazione, giroscopio, temperatura

def start_gyro():
    while True:
        # Leggi e stampa l'accelerazione
        accelerazione = mpu.acceleration
        # print("Accelerazione (m/s^2): X=%.2f, Y=%.2f, Z=%.2f" % accelerazione)
        # Leggi e stampa il giroscopio
        giroscopio = mpu.gyro
        # print("Giroscopio (rad/s): X=%.2f, Y=%.2f, Z=%.2f" % giroscopio)

        # Leggi e stampa la temperatura
        temperatura = mpu.temperature
        # print("Temperatura (C): %.2f" % temperatura)
        time.sleep(0.1)