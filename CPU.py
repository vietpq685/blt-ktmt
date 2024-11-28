class Register:
    def __init__(self):
        self.AH = 0
        self.AL = 0
        self.BH = 0
        self.BL = 0
        self.CH = 0
        self.CL = 0
        self.DH = 0
        self.DL = 0
        self.CS = 0
        self.IP = 0
        self.SS = 0
        self.SP = 0
        self.BP = 0
        self.SI = 0
        self.DI = 0
        self.DS = 0
        self.ES = 0

    @property
    def AX(self):
        return (self.AH << 8) | self.AL

    @AX.setter
    def AX(self, value):
        self.AH = (value >> 8) & 0xFF
        self.AL = value & 0xFF

    @property
    def BX(self):
        return (self.BH << 8) | self.BL

    @BX.setter
    def BX(self, value):
        self.BH = (value >> 8) & 0xFF
        self.BL = value & 0xFF

    @property
    def CX(self):
        return (self.CH << 8) | self.CL

    @CX.setter
    def CX(self, value):
        self.CH = (value >> 8) & 0xFF
        self.CL = value & 0xFF

    @property
    def DX(self):
        return (self.DH << 8) | self.DL

    @DX.setter
    def DX(self, value):
        self.DH = (value >> 8) & 0xFF
        self.DL = value & 0xFF

    def print_registers(self):
        # In tất cả thanh ghi ở base 16
        return {name: hex(getattr(self, name)) for name in vars(self)}


registers = Register()
error = ""
cmd = ""
reg = ""

def reset():
    global registers
    registers = Register()

def get_text(numb):
    if numb == 0:
        return "Operation successful"
    elif numb == 1:
        return "Invalid command"
    elif numb == 2:
        return f"The register \"{reg}\" is invalid"
    elif numb == 3:
        return f"The command \"{cmd}\" is not supported"
    elif numb == 4:
        return f"Error executing command: {error}"
    elif numb == 5:
        return "All commands have been executed"

def convert_value(value):
    """Chuyển đổi giá trị đầu vào từ các hệ cơ số khác nhau (base 2, 10, 16) sang số thập phân"""
    if value.lower().startswith('0x'):
        return int(value, 16)  # Hệ thập lục phân
    elif value.lower().startswith('0b'):
        return int(value, 2)  # Hệ nhị phân
    elif value.lower().endswith('h'):  # Xử lý trường hợp nhập hexadecimal không có tiền tố '0x'
        return int(value[:-1], 16)  # Loại bỏ 'h' và chuyển đổi sang thập lục phân
    else:
        return int(value)  # Hệ thập phân

def execute(command):
    global cmd
    global reg

    lst = command.split()
    if len(lst) < 1:
        return 1

    cmd = lst[0].upper()
    operands = [operand.upper() if operand.isalpha() else operand for operand in lst[1:]]

    try:
        # MOV
        if cmd == "MOV":
            reg, value = operands
            if hasattr(registers, reg):
                if hasattr(registers, value):
                    setattr(registers, reg, getattr(registers, value))
                else:
                    setattr(registers, reg, convert_value(value))  # Chuyển giá trị về thập phân
            else:
                return 2

        # ADD
        elif cmd == "ADD":
            reg, value = operands
            if hasattr(registers, reg):
                if hasattr(registers, value):
                    setattr(registers, reg, getattr(registers, reg) + getattr(registers, value))
                else:
                    setattr(registers, reg, getattr(registers, reg) + convert_value(value))  # Chuyển giá trị về thập phân
            else:
                return 2

        # SUB
        elif cmd == "SUB":
            reg, value = operands
            if hasattr(registers, reg):
                if hasattr(registers, value):
                    setattr(registers, reg, getattr(registers, reg) - getattr(registers, value))
                else:
                    setattr(registers, reg, getattr(registers, reg) - convert_value(value))  # Chuyển giá trị về thập phân
            else:
                return 2

        # INC
        elif cmd == "INC":
            reg = operands[0]
            if hasattr(registers, reg):
                setattr(registers, reg, getattr(registers, reg) + 1)
            else:
                return 2

        # DEC
        elif cmd == "DEC":
            reg = operands[0]
            if hasattr(registers, reg):
                setattr(registers, reg, getattr(registers, reg) - 1)
            else:
                return 2

        # MUL
        elif cmd == "MUL":
            reg = operands[0]
            if hasattr(registers, reg) and hasattr(registers, "AX"):
                registers.AX *= getattr(registers, reg)
            else:
                return 2

        # DIV
        elif cmd == "DIV":
            reg = operands[0]
            if hasattr(registers, reg) and hasattr(registers, "AX"):
                registers.DX = registers.AX % getattr(registers, reg)
                registers.AX = registers.AX // getattr(registers, reg)
            else:
                return 2

        else:
            return 3

        registers.IP += 1
        return 0

    except Exception as e:
        global error
        error = e
        return 4
