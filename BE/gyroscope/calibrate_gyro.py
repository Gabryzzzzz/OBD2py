import board
import adafruit_mpu6050
import busio
import time
import json
import os

# --- Configuration ---
CALIBRATION_SAMPLES = 1000  # Number of samples to average for calibration
CALIBRATION_FILE = "calibration_data.json" # File to store offset data

def calibrate():
    """
    Performs calibration of the MPU6050 sensor.
    The sensor must be placed on a flat, level surface and kept still.
    """
    print("--- MPU6050 Calibration Utility ---")
    
    # Initialize I2C and MPU6050 sensor
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        mpu = adafruit_mpu6050.MPU6050(i2c)
        print("✅ Sensor connected successfully.")
    except Exception as e:
        print(f"❌ Error initializing sensor: {e}")
        print("   Please check the I2C connection and try again.")
        return

    print("\nPlace the sensor on a flat, level surface.")
    print("The calibration will begin in 5 seconds. Do not move the sensor.")
    time.sleep(5)

    print(f"\nCollecting {CALIBRATION_SAMPLES} samples...")

    # Variables to accumulate readings
    acc_x_sum = 0
    acc_y_sum = 0
    acc_z_sum = 0
    gyro_x_sum = 0
    gyro_y_sum = 0
    gyro_z_sum = 0

    # Collect samples
    for i in range(CALIBRATION_SAMPLES):
        try:
            acc = mpu.acceleration
            gyro = mpu.gyro

            acc_x_sum += acc[0]
            acc_y_sum += acc[1]
            acc_z_sum += acc[2]

            gyro_x_sum += gyro[0]
            gyro_y_sum += gyro[1]
            gyro_z_sum += gyro[2]
            
            # Print progress
            if (i + 1) % 100 == 0:
                print(f"  ... collected {i + 1}/{CALIBRATION_SAMPLES} samples")

            time.sleep(0.01) # Small delay between readings
        except OSError as e:
            print(f"\n❌ Error reading from sensor: {e}")
            print("   Calibration failed. Please try again.")
            return

    # --- Calculate Offsets ---
    # Gyroscope should be 0 when still. The offset is the negative of the average reading.
    gyro_offsets = {
        "x": - (gyro_x_sum / CALIBRATION_SAMPLES),
        "y": - (gyro_y_sum / CALIBRATION_SAMPLES),
        "z": - (gyro_z_sum / CALIBRATION_SAMPLES),
    }

    # Accelerometer should be (0, 0, 9.81) when flat.
    # We calculate the offset needed to correct the X and Y axes to 0,
    # and the Z axis to gravity (approx 9.81 m/s^2).
    acc_offsets = {
        "x": - (acc_x_sum / CALIBRATION_SAMPLES),
        "y": - (acc_y_sum / CALIBRATION_SAMPLES),
        "z": 9.81 - (acc_z_sum / CALIBRATION_SAMPLES),
    }

    calibration_data = {"gyro_offsets": gyro_offsets, "acc_offsets": acc_offsets}

    # Save data to file
    with open(os.path.join(os.path.dirname(__file__), CALIBRATION_FILE), "w") as f:
        json.dump(calibration_data, f, indent=4)

    print("\n✅ Calibration complete!")
    print(f"Offset data saved to '{CALIBRATION_FILE}'")
    print("\nOffsets calculated:")
    print(json.dumps(calibration_data, indent=2))

if __name__ == "__main__":
    calibrate()