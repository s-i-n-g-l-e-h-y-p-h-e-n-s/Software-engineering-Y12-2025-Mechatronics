from machine import Pin, I2C
from time import sleep, ticks_ms
import dht
from LCD_LIBRARY import LCD_I2C

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
]

speed = 0.001  # stepper delay

# -------------------------------
# Second Motor Setup (DC Motor)
# -------------------------------
motor2 = Pin(16, Pin.OUT)

# -------------------------------
# Buzzer Setup
# -------------------------------
buzzer = Pin(17, Pin.OUT)
high_temp_threshold = 30  # buzzer triggers above this temperature

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
temp_threshold = 10
temp = 0
hum = 0
last_sensor_time = ticks_ms()
sensor_interval = 2000  # 2 sec
seq_index = 0

motor1_on = False
motor2_on = False
motor1_on_time = 0
motor2_delay = 20000  # 20 seconds

lcd_update_needed = True

while True:
    current_time = ticks_ms()

    # -------------------------------
    # Step Motor 1 continuously if ON
    # -------------------------------
    if motor1_on:
        step = sequence[seq_index]
        for i in range(4):
            pins[i].value(step[i])
        seq_index = (seq_index + 1) % len(sequence)
        sleep(speed)

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
    # Motor activation logic
    # -------------------------------
    if temp > temp_threshold and not motor1_on:
        motor1_on = True
        motor1_on_time = ticks_ms()
        print("Motor 1 turned ON")

    if motor1_on and not motor2_on:
        if ticks_ms() - motor1_on_time >= motor2_delay:
            motor2.value(1)
            motor2_on = True
            print("Motor 2 turned ON")

    # -------------------------------
    # Buzzer activation logic
    # -------------------------------
    if temp >= high_temp_threshold:
        buzzer.value(1)  # turn buzzer ON
    else:
        buzzer.value(0)  # turn buzzer OFF
