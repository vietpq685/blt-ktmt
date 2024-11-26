class Register:
    def __init__(self, name):
        self.name = name
        self._value = 0x0000  # Giá trị 16-bit mặc định là 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if 0 <= val <= 0xFFFF:  # Đảm bảo giá trị trong phạm vi 16-bit
            self._value = val
        else:
            raise ValueError(f"Value {val} out of bounds for register {self.name}")

    @property
    def high(self):
        return (self._value >> 8) & 0xFF  # Byte cao (8-bit)

    @high.setter
    def high(self, val):
        if 0 <= val <= 0xFF:  # Đảm bảo giá trị trong phạm vi 8-bit
            self._value = (self._value & 0x00FF) | (val << 8)
        else:
            raise ValueError(f"High byte {val} out of bounds for register {self.name}")

    @property
    def low(self):
        return self._value & 0xFF  # Byte thấp (8-bit)

    @low.setter
    def low(self, val):
        if 0 <= val <= 0xFF:  # Đảm bảo giá trị trong phạm vi 8-bit
            self._value = (self._value & 0xFF00) | val
        else:
            raise ValueError(f"Low byte {val} out of bounds for register {self.name}")


class CPURegisters:
    def __init__(self):
        # Các thanh ghi chính
        self.registers = {
            "AX": Register("AX"),
            "BX": Register("BX"),
            "CX": Register("CX"),
            "DX": Register("DX"),
            "CS": Register("CS"),
            "IP": Register("IP"),
            "SS": Register("SS"),
            "SP": Register("SP"),
            "BP": Register("BP"),
            "SI": Register("SI"),
            "DI": Register("DI"),
            "DS": Register("DS"),
            "ES": Register("ES"),
        }

    def get(self, name):
        if name in self.registers:
            return self.registers[name].value
        else:
            raise KeyError(f"Register {name} does not exist.")

    def set(self, name, value):
        if name in self.registers:
            self.registers[name].value = value
        else:
            raise KeyError(f"Register {name} does not exist.")

    def get_high(self, name):
        if name in self.registers and hasattr(self.registers[name], "high"):
            return self.registers[name].high
        else:
            raise KeyError(f"Register {name} does not support high byte access.")

    def set_high(self, name, value):
        if name in self.registers and hasattr(self.registers[name], "high"):
            self.registers[name].high = value
        else:
            raise KeyError(f"Register {name} does not support high byte access.")

    def get_low(self, name):
        if name in self.registers and hasattr(self.registers[name], "low"):
            return self.registers[name].low
        else:
            raise KeyError(f"Register {name} does not support low byte access.")

    def set_low(self, name, value):
        if name in self.registers and hasattr(self.registers[name], "low"):
            self.registers[name].low = value
        else:
            raise KeyError(f"Register {name} does not support low byte access.")

    def print_registers(self):
        for name, reg in self.registers.items():
            print(f"{name}: {hex(reg.value)}")


# Sử dụng
cpu = CPURegisters()

# Thiết lập giá trị
cpu.set("AX", 0x1234)
cpu.set_high("BX", 0x12)
cpu.set_low("BX", 0x34)

# Truy xuất giá trị
print(f"AX: {hex(cpu.get('AX'))}")
print(f"BX High: {hex(cpu.get_high('BX'))}")
print(f"BX Low: {hex(cpu.get_low('BX'))}")

# In toàn bộ thanh ghi
cpu.print_registers()
