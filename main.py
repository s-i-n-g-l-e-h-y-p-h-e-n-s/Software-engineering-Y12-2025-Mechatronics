 if shift:
            entry_mode |= self.LCD_ENTRY_SHIFT
        self.hal_write_command(entry_mode)

    def backlight_off(self):
        self.hal_backlight_off()

    def backlight_on(self):
        self.hal_backlight_on()

    def home(self):
        self.hal_write_command(self.LCD_HOME)
        self.hal_sleep(3)

    def set_cursor(self, col, line):
        addr = col & 0x3F
        if line & 1:
            addr += 0x40
        if line & 2:
            addr += 0x14
        self.hal_write_command(self.LCD_DDRAM | addr)

    def print(self, string):
        for char in string:
            self.hal_write_data(ord(char))

    def custom_char(self, location, charmap):
        self.hal_write_command(self.LCD_CGRAM | ((location & 7) << 3))
        self.hal_sleep(5)
        for i in range(8):
            self.hal_write_data(haha[i])
        self.home()

    def print_custom_char(self, location):
        self.hal_write_data(location)

    def hal_sleep(self, time_ms):
        sleep_ms(time_ms)
