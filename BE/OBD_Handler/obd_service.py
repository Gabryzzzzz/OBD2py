import obd
import time

class OBDService:
    def __init__(self, port=None):
        self.connection = obd.OBD("192.168.0.10:35000", protocol="6")
        self.speed = 0
        self.rpm = 800
        self.speed_direction = 1  # 1 = aumenta, -1 = diminuisce
        self.rpm_direction = 1
        self.throttle_pos_direction = 1
        self.throttle_pos = 0

    def get_speed(self):
        """Ottiene la velocità del veicolo"""
        response = self.connection.query(obd.commands.SPEED)
        return response.value.to("kph").magnitude if response.value else None

    def get_rpm(self):
        """Ottiene i giri del motore"""
        response = self.connection.query(obd.commands.RPM)
        return response.value.magnitude if response.value else None

    def get_engine_temp(self):
        """Ottiene la temperatura del motore"""
        response = self.connection.query(obd.commands.COOLANT_TEMP)
        return response.value.magnitude if response.value else None

    def get_engine_temp(self):
        """Ottiene la posizione dell'accelleratore"""
        response = self.connection.query(obd.commands.THROTTLE_POS)
        return response.value.magnitude if response.value else None

    def get_fake_data(self):
        """Simula un aumento e diminuzione ciclica di velocità e RPM"""
        step_speed = 5  # Incremento per la velocità
        step_rpm = 300  # Incremento per gli RPM
        step_throttle = 5  # Incremento per la posizione dell'accelleratore

        # Modifica la velocità ciclicamente tra 0 e 180 km/h
        if self.speed >= 180:
            self.speed_direction = -1
        elif self.speed <= 0:
            self.speed_direction = 1
        self.speed += step_speed * self.speed_direction

        # Modifica gli RPM ciclicamente tra 800 e 7200
        if self.rpm >= 7200:
            self.rpm_direction = -1
        elif self.rpm <= 800:
            self.rpm_direction = 1
        self.rpm += step_rpm * self.rpm_direction

        
        # Modifica la posizione dell'accelleratore ciclicamente tra 0 e 100
        if self.throttle_pos >= 100:
            self.throttle_pos_direction = -1
        elif self.throttle_pos <= 0:
            self.throttle_pos_direction = 1
        self.throttle_pos += step_throttle * self.throttle_pos_direction

        return {
            "speed": self.speed,
            "rpm": self.rpm,
            "engine_temp": 90,  # Valore fisso per la temperatura
            "throttle_pos": self.throttle_pos
        }

    def get_data(self):
        """Ottiene i dati reali se OBD è connesso, altrimenti usa dati fake"""
        if self.connection.is_connected():
            return {
                "speed": self.get_speed(),
                "rpm": self.get_rpm(),
                "engine_temp": self.get_engine_temp(),
                "throttle_pos": self.get_throttle_pos()
            }
        else:
            return self.get_fake_data()
