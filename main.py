
from machine import I2C, Pin
from LCD_LIBRARY import LCD_I2C
import time
import dht

# The Raspberry Pi Pico pin (GP15) connected to the DHT11 sensor
DHT11_PIN = 15

# The I2C address of your LCD (Update if different)
I2C_ADDR = 0x27  # Use the address found using the I2C scanner

# Define the number of rows and columns on your LCD
LCD_ROWS = 2
LCD_COLS = 16

# Initialize the DHT11 sensor
DHT11 = dht.DHT11(machine.Pin(DHT11_PIN))

# Initialize I2C
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Initialize LCD
lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)

# Setup function
lcd.backlight_on()
lcd.clear()

# Custom character for the degree symbol
degree_char = chr(0xDF)

# Main loop: Read data from the DHT11 sensor and display on LCD every 2 seconds
while True:
    try:
        DHT11.measure()
        temperature = DHT11.temperature()  # Gets the temperature in Celsius
        humidity = DHT11.humidity()  # Gets the relative humidity in %
        print("Temperature: {:.2f}°C, Humidity: {:.2f}%".format(temperature, humidity))
        lcd.clear()
        lcd.set_cursor(0, 0) # Move to the beginning of the first row
        lcd.print("Temp: {:.2f}{}C".format(temperature, degree_char))
        lcd.set_cursor(0, 1)  # Move to the beginning of the second row
        lcd.print("Humi: {:.2f}%".format(humidity))
    except OSError as e:
        print("Failed to read from DHT11 sensor:", e)

    time.sleep(2)
