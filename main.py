import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import CPU

# Settings font
fontSize = 20
fontName = "Courier"
fontStyle = "bold"
fontOption = (fontName, fontSize, fontStyle)

flags = {'CF': 0, 'ZF': 0, 'SF': 0, 'OF': 0, 'PF': 1, 'AF': 0, 'IF': 0, 'DF': 0}

current_file_save = None    # Biến lưu địa chỉ đường dẫn file khi đã lưu để xử lý trong các hàm khác

class run(tk.Toplevel):
    def display_register(self):
        # Cập nhật giá trị các thanh ghi trong giao diện
        for reg, widgets in self.register_labels.items():
            if isinstance(widgets, dict):  # Các thanh ghi 16-bit (AX, BX, CX, DX)
                h_val = getattr(self.cpu.registers, reg[0] + 'H')  # Lấy giá trị phần cao (H)
                l_val = getattr(self.cpu.registers, reg[0] + 'L')  # Lấy giá trị phần thấp (L)
                widgets['H'].delete(0, tk.END)
                widgets['L'].delete(0, tk.END)
                widgets['H'].insert(0, f"{h_val:02X}")
                widgets['L'].insert(0, f"{l_val:02X}")
            else:  # Các thanh ghi bổ sung (CS, IP, SS, ...)
                reg_val = getattr(self.cpu.registers, reg)  # Lấy giá trị thanh ghi
                widgets.delete(0, tk.END)
                widgets.insert(0, f"{reg_val:04X}")

    def display_flag(self):
        global flags
        # In giá trị các flag
        for flg, widgets in self.flag_labels.items():
            flag_val = flags[flg]
            widgets.delete(0, tk.END)
            widgets.insert(0, str(flag_val))

    def run_asm_code(self, content):
        line_code = content.strip()
        result = self.cpu.execute(line_code)

        return result

    def single_step(self):
        """Đọc thêm một hoặc nhiều dòng từ file và hiển thị."""
        if self.file:  # Kiểm tra xem file đã mở hay chưa
            while True:
                next_line = self.file.readline()
                if next_line:
                    self.code_text.insert("end", next_line)
                    # Kiểm tra xem dòng có hợp lệ không, nếu dòng đã hợp lệ thì dừng vònd lặp
                    stripped_line = next_line.strip()
                    if (
                        stripped_line and  # Dòng trống
                        not stripped_line.startswith((';', '.', 'main', 'end', 'INT 21h')) and
                        not stripped_line.endswith((':', 'main'))  # Kết thúc bằng các từ không mong muốn
                    ):
                        end = self.run_asm_code(next_line)
                        if end != 0:
                            self.file.close()
                            self.file = None
                            self.close_window(end)
                            break
                        else:
                            # Hiển thị kết quả
                            self.print_to_console(end)
                            # Cập nhật thanh ghi
                            self.display_register()
                            break
                else:
                    self.print_to_console(5)
                    self.file.close()
                    self.file = None
                    break

    def run_all(self): # Chạy nhiều single_step liền nhau
        while self.file:  # Kiểm tra xem file đã mở hay chưa
            self.single_step()

    def create_top_buttons(self):
        # Tạo các nút trên cùng: Run Single (chạy từng dòng lệnh), Run All (Chạy tất cả các dòng lệnh còn lại).
        top_frame = tk.Frame(self)
        top_frame.pack(side = "top", fill = "x")

        # Đường kẻ ngăn cách
        line = tk.Frame(self, height = 1, bg="black")
        line.pack(side="top", fill="both")

        # Nút "Single Step"
        single_step_button = tk.Button(
            top_frame,
            text = "Single Step",
            command = self.single_step,
            font = (fontName, 10, fontStyle),
            fg = "green",
        )
        single_step_button.pack(side="left", padx=110)

        # Nút "Run All"
        run_all_button = tk.Button(
            top_frame,
            text = "Run All",
            command = self.run_all,
            font = (fontName, 10, fontStyle),
            fg = "green",
        )
        run_all_button.pack(side="right", padx=110)

    def print_to_console(self, numb): # In thông tin ra màn hình đen
        text = self.cpu.get_text(numb)
        self.screen_console["text"] = "\n" + text + "\n"

    def close_window(self, numb = None):
        if numb != None:
            msg = messagebox.showinfo("Close", self.cpu.get_text(numb))
            if (msg):
                self.destroy()
                self.parent.deiconify()
        else:
            self.destroy()
            self.parent.deiconify()

    def create_main_screen(self): # Tạo phần hoạn động chính
        main_area = tk.Frame(self)
        main_area.pack(side = "top", fill = "both", expand = True)

        # Khung bên trái: Thông số thanh ghi
        frame_left = tk.Frame(main_area)
        frame_left.pack(side="left", fill="both")
        # Đường kẻ ngăn cách
        line1 = tk.Frame(main_area, width = 1, bg="gray")
        line1.pack(side="left", fill="both")
        # Bên trái: Thông số thanh ghi
        self.register_frame = tk.Frame(frame_left)
        self.register_frame.grid(row=1, column=1, padx=10, pady=5)
        self.register_label = tk.Label(self.register_frame, text="Registers", font=("Arial", 16))
        self.register_label.grid(row=0, column=0, columnspan=3)

        # In ra các thanh ghi
        self.register_labels = {}
        row_index = 1
        for reg in ['AX', 'BX', 'CX', 'DX']:
            tk.Label(self.register_frame, text=reg).grid(row=row_index, column=0)

            # Tạo Entry cho phần cao (H) và thấp (L)
            h_label = tk.Entry(self.register_frame, width=5)
            h_label.grid(row=row_index, column=1)
            l_label = tk.Entry(self.register_frame, width=5)
            l_label.grid(row=row_index, column=2)

            # Lấy giá trị từ lớp Register để hiển thị
            h_label.insert(0, getattr(self.cpu.registers, reg[0] + 'H'))
            l_label.insert(0, getattr(self.cpu.registers, reg[0] + 'L'))

            # Liên kết Entry với các thuộc tính của lớp Register
            h_label.bind("<FocusOut>", lambda e, r=reg: self.update_register_hl(r, 'H', e.widget.get()))
            l_label.bind("<FocusOut>", lambda e, r=reg: self.update_register_hl(r, 'L', e.widget.get()))

            # Lưu tham chiếu Entry
            self.register_labels[reg] = {'H': h_label, 'L': l_label}
            row_index += 1

        # Hiển thị các thanh ghi bổ sung 16-bit
        self.additional_registers = ['CS', 'IP', 'SS', 'SP', 'BP', 'SI', 'DI', 'DS', 'ES']
        for reg in self.additional_registers:
            tk.Label(self.register_frame, text=reg).grid(row=row_index, column=0)

            # Tạo Entry
            reg_entry = tk.Entry(self.register_frame, width=10)
            reg_entry.grid(row=row_index, column=1, columnspan=2)

            # Lấy giá trị từ lớp Register để hiển thị
            reg_entry.insert(0, getattr(self.cpu.registers, reg))

            # Liên kết Entry với thuộc tính của lớp Register
            reg_entry.bind("<FocusOut>", lambda e, r=reg: self.update_register_value(r, e.widget.get()))

            # Lưu tham chiếu Entry
            self.register_labels[reg] = reg_entry
            row_index += 1



        # Khung ở giữa: Hiển thị code ASM
        frame_middle = tk.Frame(main_area)
        frame_middle.pack(side="left", fill="both")

        # Ở giữa: Hiển thị code ASM
        label_code = ttk.Label(frame_middle, text="Code Here", font=("Arial", 16))
        label_code.pack(anchor="n")

        self.code_text = tk.Text(frame_middle, wrap="none", width=43, font = (fontName, 12, fontStyle))
        self.code_text.pack(side="left", fill="both", expand=True)


        # Khung bên phải: Thông số cờ (Flags)
        frame_right = tk.Frame(main_area)
        frame_right.pack(side="right", fill="both")
        # Đường kẻ ngăn cách
        line2 = tk.Frame(main_area, width = 1, bg="gray")
        line2.pack(side="right", fill="both")

        self.flag_frame = tk.Frame(frame_right)
        self.flag_frame.grid(row=1, column=1, padx=5, pady=5)
        self.flag_label = tk.Label(self.flag_frame, text="Flags", font=("Arial", 16))
        self.flag_label.grid(row=0, column=0, columnspan=3)

        self.flag_labels = {}
        row_index = 1
        self.lst_flags = ['CF', 'ZF', 'SF', 'OF', 'PF', 'AF', 'IF', 'DF']
        for flag in self.lst_flags:
            tk.Label(self.flag_frame, text=flag).grid(row=row_index, column=0)
            flag_entry = tk.Entry(self.flag_frame, width=5)
            flag_entry.grid(row=row_index, column=1, columnspan=2)
            self.flag_labels[flag] = flag_entry
            row_index += 1


        # Khung phía dưới: Màn hình đen (Screen)
        frame_bottom = tk.Frame(self, height = 100, bg="black")
        frame_bottom.pack(side="bottom", fill="both")

        # Phía dưới: Màn hình đen
        self.screen_console = tk.Label(frame_bottom, text="", font=("Consolas", 10), bg="black", fg="white", anchor = 'w')
        self.screen_console.pack(fill="both", expand=True)
    

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # Tên của cửa sổ
        self.title("RUN")
        # Icon app
        self.iconbitmap("asm.ico")

        # Khi đóng cửa sổ con, hiển thị lại cửa sổ chính
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Size của cửa sổ
        # self.geometry("600x700")
        # Không cho phép resize cửa sổ
        # self.resizable(width = False, height = False)

        global current_file_save
        self.cpu = CPU
        self.cpu.reset()

        # Định nghĩa khung bố cục
        # Vùng trên cùng chứa các nút chức năng
        self.create_top_buttons()

        # Tạo vùng chứa các thanh ghi, code, flag và console
        self.create_main_screen()


        # Thêm code vào khu vực code
        self.file =  open(current_file_save, "r")
        self.code_text.delete(1.0, "end")

        # In giá trị các thanh ghi
        self.display_register()
        self.display_flag()


        self.screen_console["text"] = "\n" + "Welcome!!!" + "\n"


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
        global current_file_save
        current_file_save = self.current_file

        self.withdraw() # Ẩn cửa sổ chính
        windowRun = run(self)
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
