import board
import adafruit_mpu6050
import busio
import time
import math

last_time = time.time()

# Inizializza l'interfaccia I2C usando i pin del Raspberry Pi
# 'board.SCL' e 'board.SDA' sono i nomi standard dei pin I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Crea un oggetto MPU6050. Il sensore è pronto per essere usato.
mpu = adafruit_mpu6050.MPU6050(i2c)

accelerazione_ext = [0, 0, 0]
giroscopio_ext = [0, 0, 0]
gyro_threshold = 0.01  # deadzone
temperatura_ext = None

def get_info():
    return accelerazione_ext, giroscopio_ext, temperatura_ext

def start_gyro():
    global temperatura_ext, accelerazione_ext, giroscopio_ext, gyro_threshold, last_time
    while True:
         # Calcola delta time
        now = time.time()
        delta_time = now - last_time
        last_time = now

        accelerazione = mpu.acceleration
        giroscopio = mpu.gyro
        temperatura_ext = mpu.temperature

        gx, gy, gz = giroscopio
        ax, ay, az = accelerazione

        # Applica deadzone
        gx = gx if abs(gx) > gyro_threshold else 0
        gy = gy if abs(gy) > gyro_threshold else 0
        gz = gz if abs(gz) > gyro_threshold else 0

        # Integra la rotazione
        giroscopio_ext[0] += gx * delta_time
        giroscopio_ext[1] += gy * delta_time
        giroscopio_ext[2] += gz * delta_time

         # Integra la rotazione
        accelerazione_ext[0] = ax
        accelerazione_ext[1] = ay
        accelerazione_ext[2] = az

        # time.sleep(0.5)