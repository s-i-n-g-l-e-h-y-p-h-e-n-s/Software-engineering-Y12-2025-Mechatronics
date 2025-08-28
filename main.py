from machine import Pin, I2C
from time import sleep, ticks_ms
import dht
from LCD_LIBRARY import LCD_I2C

# -------------------------------
# Output Class With Logic 
# -------------------------------
class output:
    # Initialisation with logic parameters
    def __init__(self, temp_threshold, delay):
        self.temperature_threshold = temp_threshold
        self.delay = delay
        self.timer = 0
        self.on = False
    # Check if delay time has passed
    def checktime(self, current_time):
        if current_time - self.timer >= self.delay:
            return True
        return False
    # Activates output based on temperature
    def checktemp(self, temperature):
        if temperature >= self.temperature_threshold:
            self.on = True
        else:
            self.on = False

# -------------------------------
# Output Instances
# -------------------------------
outputmotor1 = output(28, 0)
outputmotor2 = output(28, 20000)
outputbuzzer = output(35, 0)

# -------------------------------
# Stepper Motor Setup (Motor 1)
# -------------------------------
IN1 = Pin(18, Pin.OUT)
IN2 = Pin(19, Pin.OUT)
IN3 = Pin(20, Pin.OUT)
IN4 = Pin(21, Pin.OUT)
pins = [IN1, IN2, IN3, IN4]

sequence = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1]
] # Step sequence for stepper motor

speed = 0.001  # stepper delay

# -------------------------------
# Second Motor Setup (DC Motor)
# -------------------------------
motor2pin = Pin(16, Pin.OUT)

# -------------------------------
# Buzzer Setup
# -------------------------------
buzzerpin = Pin(17, Pin.OUT)
# -------------------------------
# DHT11 and LCD Setup
# -------------------------------
DHT11_PIN = 15
DHT11 = dht.DHT11(Pin(DHT11_PIN))

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = LCD_I2C(i2c, 0x27, 2, 16)
lcd.backlight_on()
lcd.clear()
degree_char = chr(0xDF)
# -------------------------------
# Main Loop Variables
# -------------------------------
temp = 0
hum = 0
last_sensor_time = ticks_ms()
sensor_interval = 2000  # 2 sec
seq_index = 0

lcd_update_needed = True

while True:
    current_time = ticks_ms()

    # -------------------------------
    # Read DHT11 sensor every 2 sec
    # -------------------------------
    if current_time - last_sensor_time > sensor_interval:
        try:
            DHT11.measure()
            temp = DHT11.temperature()
            hum = DHT11.humidity()
            lcd_update_needed = True
            print("Temp: {:.2f}C, Hum: {:.2f}%".format(temp, hum))
        except OSError:
            print("DHT11 read error")
        last_sensor_time = current_time

    # -------------------------------
    # Update LCD
    # -------------------------------
    if lcd_update_needed:
        lcd.clear()
        lcd.set_cursor(0, 0)
        lcd.print("Temp: {:.2f}{}C".format(temp, degree_char))
        lcd.set_cursor(0, 1)
        lcd.print("Humi: {:.2f}%".format(hum))
        lcd_update_needed = False

    # -------------------------------
    # Motor and buzzer activation logic using output class
    # -------------------------------
    outputmotor1.checktemp(temp)
    outputmotor2.checktemp(temp)
    outputbuzzer.checktemp(temp)

    # Motor 1 (Stepper)
    if outputmotor1.on:
        step = sequence[seq_index]
        for i in range(4):
            pins[i].value(step[i])
        seq_index = (seq_index + 1) % len(sequence)
        sleep(speed)
        if not outputmotor1.timer:
            outputmotor1.timer = current_time  # start timer for motor2

    # Motor 2 (DC Motor)
    if outputmotor1.on and not outputmotor2.on:
        if outputmotor2.checktime(current_time):
            outputmotor2.on = True
            motor2.value(1)
            print("Motor 2 turned ON")

    if not outputmotor1.on:
        # Reset timers and outputs if temp drops
        outputmotor1.timer = 0
        outputmotor2.on = False
        motor2.value(0)

    # Buzzer
    buzzerpin.value(1 if outputbuzzer.on else 0)
