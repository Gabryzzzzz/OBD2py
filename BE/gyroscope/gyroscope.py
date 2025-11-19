import board
import adafruit_mpu6050
import busio
import time

import math
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

# --- Variables for Complementary Filter ---
filtered_pitch = 0.0
filtered_roll = 0.0
last_update_time = 0.0

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
    """Returns the filtered orientation and raw sensor data."""
    # Return the filtered pitch and roll, converted to degrees for easier use in the frontend.
    return math.degrees(filtered_pitch), math.degrees(filtered_roll), temperatura

def start_gyro():
    global accelerazione, giroscopio, temperatura, filtered_pitch, filtered_roll, last_update_time
    

    print("🚀 Avvio del giroscopio...")
    # Filter coefficient (alpha). A higher value trusts the accelerometer more.
    # A lower value trusts the gyroscope more. 0.02 is a good starting point.
    ALPHA = 0.02

    last_update_time = time.monotonic()

    while True:
        try:
            current_time = time.monotonic()
            dt = current_time - last_update_time
            last_update_time = current_time
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

            # --- Complementary Filter Calculations ---

            # 1. Calculate pitch and roll from accelerometer data
            # These angles are stable but noisy.
            acc_pitch = math.atan2(accelerazione[0], math.sqrt(accelerazione[1]**2 + accelerazione[2]**2))
            acc_roll = math.atan2(accelerazione[1], accelerazione[2])

            # 2. Integrate gyroscope data to get change in angle
            # This is responsive but drifts over time.
            # We use the previous filtered angle as the base.
            gyro_pitch = filtered_pitch + giroscopio[1] * dt
            gyro_roll = filtered_roll - giroscopio[0] * dt # Invert gyro X for correct roll

            # 3. Combine the two using the complementary filter
            # new_angle = (1 - alpha) * (gyro_angle) + alpha * (accelerometer_angle)
            filtered_pitch = (1 - ALPHA) * gyro_pitch + ALPHA * acc_pitch
            filtered_roll = (1 - ALPHA) * gyro_roll + ALPHA * acc_roll

            time.sleep(0.01) # Run the filter at a high frequency (e.g., 100Hz)
        except OSError:
            # If there's a read error, just skip this iteration
            time.sleep(0.5)
            continue