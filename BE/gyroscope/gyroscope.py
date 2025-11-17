import board
import adafruit_mpu6050
import busio
import time

import json
import os
# Inizializza l'interfaccia I2C usando i pin del Raspberry Pi
# 'board.SCL' e 'board.SDA' sono i nomi standard dei pin I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Crea un oggetto MPU6050. Il sensore è pronto per essere usato.
mpu = adafruit_mpu6050.MPU6050(i2c)

accelerazione = (0, 0, 0)
giroscopio = (0, 0, 0)
temperatura = 0

# --- Load Calibration Data ---
CALIBRATION_FILE = "calibration_data.json"
acc_offsets = {"x": 0, "y": 0, "z": 0}
gyro_offsets = {"x": 0, "y": 0, "z": 0}

try:
    calibration_path = os.path.join(os.path.dirname(__file__), CALIBRATION_FILE)
    with open(calibration_path, "r") as f:
        data = json.load(f)
        acc_offsets = data["acc_offsets"]
        gyro_offsets = data["gyro_offsets"]
        print("✅ Dati di calibrazione del giroscopio caricati con successo.")
except FileNotFoundError:
    print("⚠️ File di calibrazione non trovato. Il giroscopio funzionerà con valori grezzi.")
except (KeyError, json.JSONDecodeError):
    print("❌ Errore nel file di calibrazione. Il giroscopio funzionerà con valori grezzi.")


def get_info():
    return accelerazione, giroscopio, temperatura

def start_gyro():
    global accelerazione, giroscopio, temperatura
    while True:
        try:
            # Read raw data
            raw_acc = mpu.acceleration
            raw_gyro = mpu.gyro

            # Apply calibration offsets
            accelerazione = (
                raw_acc[0] + acc_offsets["x"],
                raw_acc[1] + acc_offsets["y"],
                raw_acc[2] + acc_offsets["z"],
            )
            giroscopio = (
                raw_gyro[0] + gyro_offsets["x"],
                raw_gyro[1] + gyro_offsets["y"],
                raw_gyro[2] + gyro_offsets["z"],
            )
            temperatura = mpu.temperature
            time.sleep(0.1)
        except OSError:
            # If there's a read error, just skip this iteration
            time.sleep(0.5)
            continue