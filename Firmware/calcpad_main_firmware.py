import time
import board
import digitalio

# 4x4 Keypad Layout:
# [7] [8] [9] [/]
# [4] [5] [6] [*]
# [1] [2] [3] [-]
# [C] [0] [=] [+]

class Calculator:
    def __init__(self):
        self.display_value = "0"
        self.current_value = 0
        self.previous_value = 0
        self.operation = None
        self.new_number = True
        
    def input_digit(self, digit):
        if self.new_number:
            self.display_value = digit
            self.new_number = False
        else:
            if len(self.display_value) < 10:  # Limit display length
                if self.display_value == "0":
                    self.display_value = digit
                else:
                    self.display_value += digit
    
    def input_operation(self, op):
        if not self.new_number:
            self.current_value = float(self.display_value)
        
        if self.operation and not self.new_number:
            self.calculate()
        else:
            self.previous_value = self.current_value
        
        self.operation = op
        self.new_number = True
    
    def calculate(self):
        try:
            if self.operation == '+':
                result = self.previous_value + self.current_value
            elif self.operation == '-':
                result = self.previous_value - self.current_value
            elif self.operation == '*':
                result = self.previous_value * self.current_value
            elif self.operation == '/':
                if self.current_value == 0:
                    self.display_value = "Error"
                    self.clear()
                    return
                result = self.previous_value / self.current_value
            else:
                return
            
            # Format the result
            if result == int(result):
                self.display_value = str(int(result))
            else:
                self.display_value = str(round(result, 6))
            
            self.current_value = result
            self.previous_value = result
            self.operation = None
            self.new_number = True
        except:
            self.display_value = "Error"
            self.clear()
    
    def clear(self):
        self.display_value = "0"
        self.current_value = 0
        self.previous_value = 0
        self.operation = None
        self.new_number = True
    
    def get_display(self):
        return self.display_value


class KeypadMatrix:
    def __init__(self, row_pins, col_pins):
        self.keys = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+']
        ]
        
        self.rows = []
        for pin in row_pins:
            row = digitalio.DigitalInOut(pin)
            row.direction = digitalio.Direction.OUTPUT
            row.value = True
            self.rows.append(row)
        
        self.cols = []
        for pin in col_pins:
            col = digitalio.DigitalInOut(pin)
            col.direction = digitalio.Direction.INPUT
            col.pull = digitalio.Pull.UP 
            self.cols.append(col)
        
        self.last_key = None
        self.last_time = 0
    
    def scan(self):
        """Scan the keypad matrix and return pressed key"""
        current_time = time.monotonic()
        
        # Debounce: ignore if less than 200ms since last press
        if current_time - self.last_time < 0.2:
            return None
        
        for row_num, row in enumerate(self.rows):
            row.value = False
            time.sleep(0.001)  # Small delay for signal to settle
            
            # Check each column
            for col_num, col in enumerate(self.cols):
                if not col.value:  # Column is low (button pressed)
                    key = self.keys[row_num][col_num]
                    
                    # Set row back high
                    row.value = True
                    
                    # Update timing
                    self.last_time = current_time
                    self.last_key = key
                    
                    return key
            
            # Set row back high
            row.value = True
        
        return None


def main():
    # Configured pins for my xiao
    # Row pins: GP26, GP27, GP28, GP29
    # Column pins: GP6, GP7, GP2, GP1
    ROW_PINS = [board.GP26, board.GP27, board.GP28, board.GP29]
    COL_PINS = [board.GP6, board.GP7, board.GP2, board.GP1]
    
    keypad = KeypadMatrix(ROW_PINS, COL_PINS)
    calc = Calculator()
    
    print("Calculator Ready!")
    print("Display:", calc.get_display())
    
    # Main loop
    while True:
        key = keypad.scan()
        
        if key:
            print(f"Key pressed: {key}")
            
            if key in '0123456789':
                calc.input_digit(key)
            elif key in '+-*/':
                calc.input_operation(key)
            elif key == '=':
                calc.calculate()
            elif key == 'C':
                calc.clear()
            
            print("Display:", calc.get_display())
        
        time.sleep(0.01)


if __name__ == "__main__":
    main()
