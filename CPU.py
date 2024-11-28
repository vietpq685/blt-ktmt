# Các thanh ghi 8086 với phần cao (H) và thấp (L) cho AX, BX, CX, DX, 
# tất cả đều khởi tạo với giá trị 0
registers = {
    'AX': {'H': 00, 'L': 00},
    'BX': {'H': 00, 'L': 00},
    'CX': {'H': 00, 'L': 00},
    'DX': {'H': 00, 'L': 00},
    'CS': 0000, 'IP': 0000, 'SS': 0000, 'SP': 0000,
    'BP': 0000, 'SI': 0000, 'DI': 0000, 'DS': 0000, 'ES': 0
}

error = None

def reset():
    global registers
    registers = {
    'AX': {'H': 00, 'L': 00},
    'BX': {'H': 00, 'L': 00},
    'CX': {'H': 00, 'L': 00},
    'DX': {'H': 00, 'L': 00},
    'CS': 0000, 'IP': 0000, 'SS': 0000, 'SP': 0000,
    'BP': 0000, 'SI': 0000, 'DI': 0000, 'DS': 0000, 'ES': 0
}

def get_text(numb):
    if numb == 0:
        return "thực hiện thành công"
    elif numb == 1:
        return "lệnh không hợp lệ"
    elif numb == 2:
        return "thanh ghi không hợp lệ"
    elif numb == 3:
        return "lệnh \"" + cmd + "\" chưa được hỗ trợ"
    elif numb == 4:
        return f"Lỗi khi thực hiện lệnh: {str(error)}"
    elif numb == 5:
        return "Đã chạy hết các lệnh"

cmd = None

def execute(instruction):
    global cmd
    # Phân tách mã lệnh và toán hạng
    parts = instruction.split()
    if len(parts) < 1:
        return 1
    
    cmd = parts[0].upper()
    operands = parts[1:]

    try:
        if cmd == "MOV":
            # Lệnh MOV: MOV REG, VALUE
            reg, value = operands
            if reg in registers:
                if isinstance(registers[reg], dict):  # AX, BX, CX, DX
                    if value in registers and isinstance(registers[value], dict):
                        registers[reg]['H'] = registers[value]['H']
                        registers[reg]['L'] = registers[value]['L']
                    elif value.startswith('0x'):
                        registers[reg]['L'] = int(value, 16)
                    else:
                        registers[reg]['L'] = int(value)
                else:
                    registers[reg] = int(value)
            else:
                return 2

        elif cmd == "ADD":
            reg, value = operands
            if reg in registers:
                if isinstance(registers[reg], dict):
                    if value in registers and isinstance(registers[value], dict):
                        registers[reg]['L'] += registers[value]['L']
                    else:
                        registers[reg]['L'] += int(value)
                else:
                    if value in registers:
                        registers[reg] += registers[value]
                    else:
                        registers[reg] += int(value)
            else:
                return 2

        elif cmd == "SUB":
            reg, value = operands
            if reg in registers:
                if isinstance(registers[reg], dict):
                    if value in registers and isinstance(registers[value], dict):
                        registers[reg]['L'] -= registers[value]['L']
                    else:
                        registers[reg]['L'] -= int(value)
                else:
                    if value in registers:
                        registers[reg] -= registers[value]
                    else:
                        registers[reg] -= int(value)
            else:
                return 2

        elif cmd == "INC":
            reg = operands[0]
            if reg in registers:
                if isinstance(registers[reg], dict):
                    registers[reg]['L'] += 1
                else:
                    registers[reg] += 1
            else:
                return 2

        elif cmd == "DEC":
            reg = operands[0]
            if reg in registers:
                if isinstance(registers[reg], dict):
                    registers[reg]['L'] -= 1
                else:
                    registers[reg] -= 1
            else:
                return 2
        
        elif cmd == "MUL":
            reg = operands[0]
            if reg in registers and isinstance(registers[reg], dict):
                registers["AX"]['L'] *= registers[reg]['L']
            else:
                return 2
        
        elif cmd == "DIV":
            reg = operands[0]
            if reg in registers and isinstance(registers[reg], dict):
                registers["DX"]['L'] = registers["AX"]['L'] % registers[reg]['L']
                registers["AX"]['L'] = registers["AX"]['L'] // registers[reg]['L']
            else:
                return 2

        else:
            return 3

        # Tăng Instruction Pointer sau mỗi lệnh
        registers['IP'] += 1

        return 0

    except Exception as e:
        global error
        error = e
        return 4