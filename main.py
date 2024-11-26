import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
# import command

# Settings font
fontSize = 20
fontName = "Courier"
fontStyle = "bold"
fontOption = (fontName, fontSize, fontStyle)

current_file_save = None    # Biến lưu địa chỉ đường dẫn file khi đã lưu để xử lý trong các hàm khác

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

class run(tk.Tk):
    def create_top_buttons(self):
        # Tạo các nút trên cùng: Open File, Run Code.
        top_frame = tk.Frame(self)
        top_frame.pack(side = "top", fill = "x")

        # Đường kẻ ngăn cách
        line = tk.Frame(self, height = 1, bg="black")
        line.pack(side="top", fill="both")

        # Nút "Single Step"
        single_step_button = tk.Button(
            top_frame,
            text = "Single Step",
            font = (fontName, 10, fontStyle),
            fg = "green",
        )
        single_step_button.pack(side="left", padx=110)

        # Nút "Run All"
        run_all_button = tk.Button(
            top_frame,
            text = "Run All",
            font = (fontName, 10, fontStyle),
            fg = "green",
        )
        run_all_button.pack(side="right", padx=110)

    def create_main_screen(self):
        main_area = tk.Frame(self)
        main_area.pack(side = "top", fill = "both", expand = True)

        # Khung bên trái: Thông số thanh ghi
        frame_left = tk.Frame(main_area)
        frame_left.pack(side="left", fill="both")
        # Đường kẻ ngăn cách
        line1 = tk.Frame(main_area, width = 1, bg="gray")
        line1.pack(side="left", fill="both")
        # Bên trái: Thông số thanh ghi
        label_registers = ttk.Label(frame_left, text="Registers", font=("Arial", 16))
        label_registers.pack(anchor="n")

        self.tree_registers = ttk.Treeview(frame_left, columns=("Value"), show="headings", height=10)
        self.tree_registers.heading("Value", text="Value")
        self.tree_registers.column("Value", width=100)
        self.tree_registers.pack(fill="both", expand=True)

        # Khung ở giữa: Hiển thị code ASM
        frame_middle = tk.Frame(main_area)
        frame_middle.pack(side="left", fill="both")

        # Ở giữa: Hiển thị code ASM
        label_code = ttk.Label(frame_middle, text="Code Here", font=("Arial", 16))
        label_code.pack(anchor="n")

        self.code_text = tk.Text(frame_middle, wrap="none", width=53)
        self.code_text.pack(side="left", fill="both", expand=True)


        # Khung bên phải: Thông số cờ (Flags)
        frame_right = tk.Frame(main_area)
        frame_right.pack(side="right", fill="both")
        # Đường kẻ ngăn cách
        line2 = tk.Frame(main_area, width = 1, bg="gray")
        line2.pack(side="right", fill="both")

        # Bên phải: Thông số cờ (Flags)
        label_flags = ttk.Label(frame_right, text="Flags", font=("Arial", 16))
        label_flags.pack(anchor="n")

        self.tree_flags = ttk.Treeview(frame_right, columns=("Value"), show="headings", height=10)
        self.tree_flags.heading("Value", text="Value")
        self.tree_flags.column("Value", width=60)
        self.tree_flags.pack(fill="both", expand=True)


        # Khung phía dưới: Màn hình đen (Screen)
        frame_bottom = tk.Frame(self, height = 120, bg="black")
        frame_bottom.pack(side="bottom", fill="both")

        # Phía dưới: Màn hình đen
        self.screen_label = tk.Label(frame_bottom, text="", font=("Consolas", 12), bg="black", fg="white")
        self.screen_label.pack(fill="both", expand=True)

    def __init__(self):
        super().__init__()
        # Tên của cửa sổ
        self.title("RUN")
        # Icon app
        self.iconbitmap("asm.ico")

        # Size của cửa sổ
        self.geometry("600x700")
        # Không cho phép resize cửa sổ
        self.resizable(width = False, height = False)

        # Định nghĩa khung bố cục
        # Vùng trên cùng chứa các nút chức năng
        self.create_top_buttons()

        self.create_main_screen()

        # Thêm dữ liệu mẫu vào bảng thanh ghi
        registers_data = [("AH", "0x0000"), ("AL", "0x0000"), ("BH", "0x0000"), ("BL", "0x0000"), ("CH", "0x0000"), ("CL", "0x0000"), ("DH", "0x0000"), ("DL", "0x0000"), ("CS", "0x0000"), ("IP", "0x0000"), ("SS", "0x0000"), ("SP", "0x0000"), ("BP", "0x0000"), ("SI", "0x0000"), ("DI", "0x0000"), ("DS", "0x0000"), ("ES", "0x0000")]
        for reg, val in registers_data:
            self.tree_registers.insert("", "end", values=(reg, val))

        # Thêm code vào khu vực code
        # self.code_text.insert()

        # Thêm dữ liệu mẫu vào bảng cờ
        flags_data = [("CF", "0"), ("ZF", "0"), ("SF", "0"), ("OF", "0"), ("PF", "0"), ("AF", "0"), ("IF", "0"), ("DF", "0")]
        for flag, val in flags_data:
            self.tree_flags.insert("", "end", values=(flag, val))


        # ======== Xử lý sự kiện ======== #

        # Hàm hiển thị thông báo trên màn hình đen
        def append_to_screen(text):
            current_text = self.screen_label["text"]
            self.screen_label["text"] = current_text + "\n" + text



class CLemu6808(tk.Tk):
    def check_unsaved_changes(self):
        """Kiểm tra thay đổi chưa lưu và hỏi người dùng có muốn lưu không."""
        current_content = self.code_area.get("1.0", "end-1c")  # Lấy nội dung hiện tại
        if self.current_file:  # Nếu có file đang mở
            try:
                with open(self.current_file, "r") as file:
                    saved_content = file.read()
                if current_content == saved_content:
                    return True  # Không có thay đổi
            except Exception as e:
                print(f"Error reading current file: {e}")
        else:  # Nếu chưa có file được lưu
            if not current_content.strip():  # Nội dung trống
                return True

        # Hiển thị thông báo nếu có thay đổi chưa lưu
        response = messagebox.askyesnocancel(
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save before continuing?",
        )
        if response:  # Người dùng chọn Save
            self.save_file()
            return True
        elif response is None:  # Người dùng chọn Cancel
            return False
        return True  # Người dùng chọn Don't Save

    def new_file(self):
        """Tạo file mới, nhắc nhở lưu file nếu cần."""
        if not self.check_unsaved_changes():
            return
        self.code_area.delete(1.0, "end")
        self.update_line_numbers()
        self.current_file = None  # Reset đường dẫn file

    def open_file(self):
        """Mở file, nhắc nhở lưu file nếu cần."""
        if not self.check_unsaved_changes():
            return
        file_path = filedialog.askopenfilename(
            filetypes = [("ASM Files", "*.asm"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
            self.code_area.delete(1.0, "end")
            self.code_area.insert("1.0", content)
            self.update_line_numbers()
            self.current_file = file_path  # Lưu đường dẫn file đã mở

    def save_file(self, event=None):
        """Lưu nội dung mã vào file. Nếu có file đã mở, sẽ lưu lại vào file đó."""
        if self.current_file:  # Nếu đã có file đang mở
            file_path = self.current_file
        else:
            # Nếu chưa có file, yêu cầu người dùng chọn thư mục và lưu file
            file_path = filedialog.asksaveasfilename(
                defaultextension = ".asm", filetypes = [("ASM Files", "*.asm")]
            )
            if not file_path:
                return
        try:
            with open(file_path, "w") as file:
                content = self.code_area.get("1.0", "end-1c")
                file.write(content)
            self.current_file = file_path  # Lưu đường dẫn file đã lưu
            messagebox.showinfo(
                "Save File", f"File has been saved as {os.path.basename(file_path)}."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def run_code(self):
        """Chạy code (ở đây ta chỉ in nội dung code, nhưng có thể thêm logic chạy code)."""
        if not self.check_unsaved_changes():
            return
        code = self.code_area.get("1.0", "end-1c")
        global current_file_save
        current_file_save = self.current_file
        windowRun = run()
        windowRun.mainloop()

    def create_top_buttons(self):
        # Tạo các nút trên cùng: Open File, Run Code.
        top_frame = tk.Frame(self)
        top_frame.pack(side = "top", fill = "x")

        # Nút "New" (Tạo file)
        open_button = tk.Button(
            top_frame,
            text = "New File",
            command = self.new_file,
            font = (fontName, 12, fontStyle),
        )
        open_button.pack(side = "left")

        # Nút "Open" (Mở file)
        open_button = tk.Button(
            top_frame,
            text = "Open File",
            command = self.open_file,
            font = (fontName, 12, fontStyle),
        )
        open_button.pack(side="left")

        # Nút "Save" (Lưu file)
        save_button = tk.Button(
            top_frame,
            text = "Save File",
            command = self.save_file,
            font = (fontName, 12, fontStyle),
        )
        save_button.pack(side="left")

        # Nút "Run" (Chạy code)
        run_button = tk.Button(
            top_frame,
            text = "RUN",
            command = self.run_code,
            font = (fontName, 12, fontStyle),
            fg = "green",
        )
        run_button.pack(side = "left")

    def update_line_numbers(self, event=None):  # Hàm tạo số thứ tự dòng
        def themCach(a):  # hàm tại khoảng cách để căn lề trái cho số thứ tự dòng
            return (" " * (3 - (len(str(a))))) + str(a)

        # Lấy vị trí cuộn hiện tại của line_numbers
        current_scroll_position = self.line_numbers.yview()

        # Lấy tổng số dòng hiện tại
        total_lines = int(self.code_area.index("end-1c").split(".")[0])
        # Tạo danh sách số thứ tự dòng
        line_numbers = "\n".join(themCach(i) for i in range(1, total_lines + 1))

        # Cập nhật số thứ tự trong Text line_numbers
        self.line_numbers.config(state = "normal")
        self.line_numbers.delete(1.0, "end")
        self.line_numbers.insert(1.0, line_numbers)
        self.line_numbers.config(state = "disabled")

        # Khôi phục vị trí cuộn của line_numbers
        self.line_numbers.yview_moveto(current_scroll_position[0])

    def on_scroll(self, *args):
        self.scrollbar_y.set(*args)
        self.line_numbers.yview_moveto(args[0])
        self.code_area.yview_moveto(args[0])

    def on_scrollbar_move(self, *args):
        self.line_numbers.yview(*args)
        self.code_area.yview(*args)

    def sync_scroll(self, event):
        self.code_area.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def __init__(self):
        super().__init__()
        # Tên của cửa sổ
        self.title("CLemu6808")
        # Icon app
        self.iconbitmap("asm.ico")

        # Size của cửa sổ
        self.geometry("700x800")
        # Cho phép resize cửa sổ
        self.resizable(width = True, height = True)

        # Biến để lưu đường dẫn file hiện tại
        self.current_file = None

        # Vùng trên cùng chứa các nút chức năng
        self.create_top_buttons()

        # Khung chứa số thứ tự dòng
        self.line_numbers = tk.Text(
            self, width = 3, bg = "lightgray", state = "disabled", font = fontOption
        )
        self.line_numbers.pack(side = "left", fill = "y")

        # Vùng nhập Code
        self.code_area_frame = tk.Frame(self)
        self.code_area_frame.pack(side = "right", fill = "both", expand = True)

        # Scroolbar cho chiều dọc
        self.scrollbar_y = tk.Scrollbar(self.code_area_frame, orient = "vertical")
        self.scrollbar_y.pack(side = "right", fill = "y")

        # Vùng nhập mã code
        self.code_area = tk.Text(
            self.code_area_frame,
            wrap = "none",
            undo = True,
            font = fontOption,
            yscrollcommand = self.on_scroll,
        )
        self.code_area.pack(side = "left", fill = "both", expand = True)
        self.code_area.bind("<KeyRelease>", self.update_line_numbers)

        # Cho phép sử dụng Scrollbar để di chuyển lên xuống và trái phải
        self.scrollbar_y.config(command = self.on_scrollbar_move)

        # Đồng bộ cuộn giữa số dòng và vùng nhập code
        self.code_area.bind("<MouseWheel>", self.sync_scroll)
        self.line_numbers.bind("<MouseWheel>", self.sync_scroll)

        # Cập nhật số thứ tự ban đầu
        self.update_line_numbers()


# Run CLemu
if __name__ == "__main__":
    app = CLemu6808()
    app.mainloop()
