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

def execute_instruction(instruction):
    # Phân tách mã lệnh và toán hạng
    parts = instruction.split()
    if len(parts) < 1:
        return "Lệnh không hợp lệ"
    
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
                return "Thanh ghi không hợp lệ"

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
                return "Thanh ghi không hợp lệ"

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
                return "Thanh ghi không hợp lệ"

        elif cmd == "INC":
            reg = operands[0]
            if reg in registers:
                if isinstance(registers[reg], dict):
                    registers[reg]['L'] += 1
                else:
                    registers[reg] += 1
            else:
                return "Thanh ghi không hợp lệ"

        elif cmd == "DEC":
            reg = operands[0]
            if reg in registers:
                if isinstance(registers[reg], dict):
                    registers[reg]['L'] -= 1
                else:
                    registers[reg] -= 1
            else:
                return "Thanh ghi không hợp lệ"
        
        elif cmd == "MUL":
            reg = operands[0]
            if reg in registers and isinstance(registers[reg], dict):
                registers["AX"]['L'] *= registers[reg]['L']
            else:
                return "Thanh ghi không hợp lệ"
        
        elif cmd == "DIV":
            reg = operands[0]
            if reg in registers and isinstance(registers[reg], dict):
                registers["DX"]['L'] = registers["AX"]['L'] % registers[reg]['L']
                registers["AX"]['L'] = registers["AX"]['L'] // registers[reg]['L']
            else:
                return "Thanh ghi không hợp lệ"

        else:
            return "Lệnh không được hỗ trợ"

        # Tăng Instruction Pointer sau mỗi lệnh
        registers['IP'] += 1

        return "Lệnh thực hiện thành công"

    except Exception as e:
        return f"Lỗi khi thực hiện lệnh: {str(e)}"