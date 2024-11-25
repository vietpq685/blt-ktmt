import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Settings font
fontSize = 20
fontName = "Courier"
fontStyle = "bold"
fontOption = (fontName, fontSize, fontStyle)

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
        response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save before continuing?")
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
        file_path = filedialog.askopenfilename(filetypes=[("ASM Files", "*.asm"), ("All files", "*.*")])
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
            file_path = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("ASM Files", "*.asm")])
            if not file_path:
                return
        try:
            with open(file_path, "w") as file:
                content = self.code_area.get("1.0", "end-1c")
                file.write(content)
            self.current_file = file_path  # Lưu đường dẫn file đã lưu
            messagebox.showinfo("Save File", f"File has been saved as {os.path.basename(file_path)}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def run_code(self):
        """Chạy code (ở đây ta chỉ in nội dung code, nhưng có thể thêm logic chạy code)."""
        code = self.code_area.get("1.0", "end-1c")
        if code.strip():
            messagebox.showinfo("Run Code", "Code is running...\n" + code)
        else:
            messagebox.showwarning("Run Code", "No code to run.")

    def create_top_buttons(self):
        # Tạo các nút trên cùng: Open File, Run Code.
        top_frame = tk.Frame(self)
        top_frame.pack(side="top", fill="x")
        
        # Nút "Open" (Mở file)
        open_button = tk.Button(top_frame, text="New File", command=self.new_file, font = (fontName, 12, fontStyle))
        open_button.pack(side="left")

        # Nút "Open" (Mở file)
        open_button = tk.Button(top_frame, text="Open File", command=self.open_file, font = (fontName, 12, fontStyle))
        open_button.pack(side="left")

        # Nút "Save" (Lưu file)
        save_button = tk.Button(top_frame, text="Save File", command=self.save_file, font = (fontName, 12, fontStyle))
        save_button.pack(side="left")

        # Nút "Run" (Chạy code)
        run_button = tk.Button(top_frame, text="RUN", command=self.run_code, font = (fontName, 12, fontStyle), fg = 'green')
        run_button.pack(side="left")

    def update_line_numbers(self, event=None):    # Hàm tạo số thứ tự dòng
        def themCach(a):    # hàm tại khoảng cách để căn lề trái cho số thứ tự dòng
            return (' ' * (3 - (len(str(a))))) + str(a)
        
        # Lấy tổng số dòng hiện tại
        total_lines = int(self.code_area.index("end-1c").split(".")[0])
        # Tạo danh sách số thứ tự dòng
        line_numbers = "\n".join(map(themCach, range(1, total_lines + 1)))
        
        # Cập nhật số thứ tự trong Text line_numbers
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, "end")
        self.line_numbers.insert(1.0, line_numbers)
        self.line_numbers.config(state="disabled")

    def __init__(self):
        super().__init__()
        # Tên của cửa sổ
        self.title("CLemu6808")
        # Icon app
        self.iconbitmap("asm.ico")

        # Size của cửa sổ
        self.geometry("700x800")
        # Cho phép resize cửa sổ
        self.resizable(width=True, height=True)

        # Biến để lưu đường dẫn file hiện tại
        self.current_file = None

        # Vùng trên cùng chứa các nút chức năng
        self.create_top_buttons()


        # Khung chứa số thứ tự dòng
        self.line_numbers = tk.Text(self, width = 3, bg = "lightgray", state = "disabled", font = fontOption)
        self.line_numbers.pack(side = "left", fill = "y")


        # Vùng nhập Code
        self.code_area_frame = tk.Frame(self)
        self.code_area_frame.pack(side="right", fill="both", expand=True)

        # Scroolbar cho chiều dọc
        self.scrollbar_y = tk.Scrollbar(self.code_area_frame, orient="vertical")
        self.scrollbar_y.pack(side="right", fill="y")
        # Scroolbar cho chiều ngang
        self.scrollbar_x = tk.Scrollbar(self.code_area_frame, orient="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")

        # Vùng nhập mã code
        self.code_area = tk.Text(self.code_area_frame, wrap="none", undo=True, font = fontOption,yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.code_area.pack(side="left", fill="both", expand=True)
        self.code_area.bind("<KeyRelease>", self.update_line_numbers)

        # Cho phép sử dụng Scrollbar để di chuyển lên xuống và trái phải
        self.scrollbar_y.config( command = self.code_area.yview )
        self.scrollbar_x.config( command = self.code_area.xview )


        # Cập nhật số thứ tự ban đầu
        self.update_line_numbers()



# Run CLemu
if __name__ == "__main__":
    app = CLemu6808()
    app.mainloop()
