from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector


# ====== Kết nối MySQL======
def connect_db():
    """Thiết lập kết nối đến cơ sở dữ liệu MySQL."""
    try:
        # Sử dụng thông tin cấu hình KTX
        conn = mysql.connector.connect(
            host='localhost',
            user="qltkx",
            password="123456",
            database="qlktx"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi Kết Nối CSDL", f"Không thể kết nố i đến MySQL: {err}\nKiểm tra user, password và database ' {'qlktx'}'.")
        # Trả về None nếu kết nối thất bại
        return None


# ====== Hàm canh giữa cửa sổ ======
def center_window(win, w=700, h=500):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

def center_window(win, w=750, h=550): 
    """Căn giữa cửa sổ ứng dụng."""
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')


def clear_student_input():
    """Xóa trắng các ô nhập liệu cho Sinh viên và reset trạng thái."""
    global current_cccd_selected
    current_cccd_selected = None  # Reset trạng thái
    
    entry_cccd.delete(0, tk.END)
    entry_cccd.config(state='normal') # Cho phép nhập mới CCCD
    
    entry_name.delete(0, tk.END)
    gender_var.set("Nam")          # Mặc định giới tính là Nam
    # date_entry.set_date(date.today()) # Nếu có DateEntry
    entry_sdt.delete(0, tk.END)
    cbb_room.set("")               # Xóa lựa chọn Phòng
    
def load_student_data():
    """Tải dữ liệu Sinh viên từ DB vào Treeview."""
    # Xóa dữ liệu cũ
    for i in tree_students.get_children():
        tree_students.delete(i)
    
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            sql = """
                SELECT cccd, name, gender, dob, sdt, room_id 
                FROM students 
                ORDER BY room_id, name
            """
            cur.execute(sql)
            students = cur.fetchall()
            
            for cccd, name, gender, dob, sdt, room_id in students:
                # Đảm bảo thứ tự cột Treeview khớp: cccd, name, gender, dob, sdt, room_id
                row_data = (cccd, name, gender, dob, sdt, room_id)
                tree_students.insert("", tk.END, values=row_data)
        
        except Exception as e:
            messagebox.showerror("Lỗi Tải Dữ Liệu Sinh Viên", str(e))
        finally:
            if conn: conn.close()
            
def them_student():
    """Thêm một Sinh viên mới vào cơ sở dữ liệu."""
    cccd = entry_cccd.get().strip()
    name = entry_name.get().strip()
    gender = gender_var.get()
    dob = date_entry.get_date().strftime("%Y-%m-%d") # Lấy ngày sinh
    sdt = entry_sdt.get().strip()
    room_id = cbb_room.get()
   
    
    if not all([cccd, name, sdt, room_id]):
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ CCCD, Tên, SĐT và Phòng.")
        return
    
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
 
            sql = """
                INSERT INTO students (cccd, name, gender, dob, sdt, room_id) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (cccd, name, gender, dob, sdt, room_id))
            conn.commit()
            
            load_student_data()
            clear_student_input()
            messagebox.showinfo("Thành công", f"Đã thêm sinh viên: {name} (Phòng: {room_id})")
            
        except mysql.connector.Error as e:
            if e.errno == 1062: # Lỗi khóa chính (CCCD đã tồn tại)
                 messagebox.showerror("Lỗi Trùng Mã", f"CCCD '{cccd}' đã tồn tại.")
            else:
                 messagebox.showerror("Lỗi SQL", f"Không thể thêm sinh viên: {e}")
        finally:
            if conn: conn.close()

def sua_student_select(event=None):
    """Điền dữ liệu sinh viên được chọn vào form để Sửa."""
    global current_cccd_selected
    selected = tree_students.selection()
    if not selected: return
    
    # Lấy dữ liệu từ hàng được chọn
    values = tree_students.item(selected[0])["values"]
    
    clear_student_input() # Xóa trắng form trước
    
    
    # 1. Điền CCCD và vô hiệu hóa (khóa chính)
    current_cccd_selected = values[0]
    entry_cccd.insert(0, values[0])
    entry_cccd.config(state='disabled') 
    
    # 2. Điền các trường còn lại
    entry_name.insert(0, values[1])
    gender_var.set(values[2])
    date_entry.set_date(values[3]) # Gán ngày sinh
    entry_sdt.insert(0, values[4])
    cbb_room.set(values[5])
    
    # Giả định nút Lưu/Cập nhật được bật sau khi chọn

def luu_student():
    """Lưu (cập nhật) thông tin Sinh viên đã chỉnh sửa."""
    global current_cccd_selected
    
    if current_cccd_selected is None:
        messagebox.showwarning("Chưa chọn", "Hãy chọn sinh viên cần cập nhật trên danh sách.")
        return

    # Lấy dữ liệu mới từ form (CCCD lúc này là giá trị không đổi từ current_cccd_selected)
    cccd = current_cccd_selected # Lấy CCCD đã chọn
    name = entry_name.get().strip()
    gender = gender_var.get()
    dob = date_entry.get_date().strftime("%Y-%m-%d")
    sdt = entry_sdt.get().strip()
    room_id = cbb_room.get()
    
    if not all([cccd, name, sdt, room_id]):
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ thông tin.")
        return

    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            sql = """
                UPDATE students 
                SET name=%s, gender=%s, dob=%s, sdt=%s, room_id=%s 
                WHERE cccd=%s
            """
            cur.execute(sql, (name, gender, dob, sdt, room_id, cccd))
            conn.commit()
            
            load_student_data()
            clear_student_input()
            messagebox.showinfo("Thành công", f"Đã cập nhật sinh viên có CCCD: {cccd}")
            
        except Exception as e:
            messagebox.showerror("Lỗi Cập Nhật Sinh Viên", str(e))
        finally:
            if conn: conn.close()
            # Đảm bảo CCCD được bật lại sau khi Lưu xong
            entry_cccd.config(state='normal')

def xoa_student():
    """Xóa Sinh viên được chọn khỏi cơ sở dữ liệu."""
    selected = tree_students.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn sinh viên để xóa.")
        return
    
    # Lấy CCCD từ hàng được chọn
    cccd = tree_students.item(selected)["values"][0] 
    name = tree_students.item(selected)["values"][1]
    
    confirm = messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc muốn xóa sinh viên {name} (CCCD: {cccd}) không?")
    
    if confirm:
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            try:
                sql = "DELETE FROM students WHERE cccd=%s"
                cur.execute(sql, (cccd,))
                conn.commit()
                
                load_student_data()
                clear_student_input()
                messagebox.showinfo("Thành công", f"Đã xóa sinh viên có CCCD: {cccd}")
                
            except Exception as e:
                messagebox.showerror("Lỗi Xóa Sinh Viên", str(e))
            finally:
                if conn: conn.close()


# ====== Cửa sổ chính ======
root = tk.Tk()
root.title("Quản lý ký túc xá")
center_window(root, 700, 500)
root.resizable(False, False)



# ====== Tiêu đề ======
lbl_title = tk.Label(root, text="QUẢN LÝ SINH VIÊN KÝ TÚC XÁ", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)


# ====== Frame nhập thông tin ======
frame_info = tk.Frame(root)
frame_info.pack(pady=5, padx=10, fill="x")

tk.Button(frame_info, text="Thêm", width=8, command=them_student).grid(row=0, column=4, padx=5, pady=5, sticky="e")
tk.Button(frame_info, text="Lưu", width=8, command=luu_student).grid(row=1, column=4, padx=5, pady=5, sticky="e")
tk.Button(frame_info, text="Sửa", width=8, command=sua_student_select).grid(row=2, column=4, padx=5, pady=5, sticky="e")  
tk.Button(frame_info, text="Hủy", width=8, command=clear_student_input).grid(row=3, column=4, padx=5, pady=5, sticky="e")
tk.Button(frame_info, text="Xóa", width=8, command=xoa_student).grid(row=4, column=4, padx=5, pady=5, sticky="e")



# Hàng 0: Họ và Tên, Phòng
tk.Label(frame_info, text="Họ và Tên").grid(row=0, column=0, padx=5, pady=5, sticky="w")
# Đổi tên biến từ entry_tên -> entry_name (để dễ quản lý, không phải tên biến gốc)
entry_name = tk.Entry(frame_info, width=30) 
entry_name.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Phòng").grid(row=0, column=2, padx=5, pady=5, sticky="w")
# Đổi tên biến từ cbb_chucvu -> cbb_room (Phòng)
cbb_room = ttk.Combobox(frame_info, values=[
    "P01", "P02", "P03", "P04", "P05" # Các mã phòng
], width=20)
cbb_room.grid(row=0, column=3, padx=5, pady=5, sticky="w")

# Hàng 1: CCCD, Số điện thoại (Thay thế Họ lót, Tên)
tk.Label(frame_info, text="CCCD").grid(row=1, column=0, padx=5, pady=5, sticky="w")
# Đổi tên biến từ entry_cccd -> entry_cccd (Giữ nguyên)
entry_cccd = tk.Entry(frame_info, width=25)
entry_cccd.grid(row=1, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="SĐT").grid(row=1, column=2, padx=5, pady=5, sticky="w")
# Thay thế entry_ten -> entry_sdt (SĐT)
entry_sdt = tk.Entry(frame_info, width=15)
entry_sdt.grid(row=1, column=3, padx=5, pady=5, sticky="w")

# Hàng 2: Phái, Ngày sinh
tk.Label(frame_info, text="Phái").grid(row=2, column=0, padx=5, pady=5, sticky="w")
gender_var = tk.StringVar(value="Nam")
tk.Radiobutton(frame_info, 
               text="Nam", 
               variable=gender_var, 
               value="Nam").grid(row=2, column=1, padx=5, sticky="w")
tk.Radiobutton(frame_info, 
               text="Nữ", 
               variable=gender_var, 
               value="Nữ").grid(row=2, column=1, padx=60, sticky="w") 

tk.Label(frame_info, text="Ngày sinh").grid(row=2, column=2, padx=5, pady=5, sticky="w")
date_entry = DateEntry(frame_info, 
                       width=12, 
                       background="darkblue", 
                       foreground="white", 
                       date_pattern="yyyy-mm-dd")
date_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")

# ====== Bảng danh sách Sinh viên (Treeview) ======
lbl_ds = tk.Label(root, text="Danh sách Sinh viên đang ở", font=("Arial", 10, "bold"))
lbl_ds.pack(pady=5, anchor="w", padx=10)



# Định nghĩa lại các cột cho KTX
columns = ("cccd", "name", "gender", "dob", "sdt", "room_id")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)

# Cấu hình tiêu đề và kích thước cột
tree.heading("cccd", text="CCCD")
tree.column("cccd", width=100, anchor="center")
tree.heading("name", text="Họ và Tên")
tree.column("name", width=150)
tree.heading("gender", text="Phái")
tree.column("gender", width=70, anchor="center")
tree.heading("dob", text="Ngày sinh")
tree.column("dob", width=100, anchor="center")
tree.heading("sdt", text="SĐT")
tree.column("sdt", width=100, anchor="center")
tree.heading("room_id", text="Phòng")
tree.column("room_id", width=150)
tree.pack(padx=10, pady=5, fill="both")
# ====== Chức năng CRUD ======

def center_window(win, w=850, h=600): 
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

# ====== Cửa sổ chính ======
root = tk.Tk()
root.title("Quản lý ký túc xá")
center_window(root, 700, 500)
root.resizable(False, False)



# ====== Tiêu đề ======
lbl_title = tk.Label(root, text="QUẢN LÝ PHÒNG VÀ SINH VIÊN", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)


# --- Sử dụng Notebook (Tabs) để quản lý 2 nghiệp vụ chính ---
notebook = ttk.Notebook(root)
notebook.pack(pady=5, padx=10, expand=True, fill="both")

# --- Tabs ---
tab_rooms = ttk.Frame(notebook)
tab_students = ttk.Frame(notebook)

notebook.add(tab_rooms, text="1. Quản lý Phòng")
notebook.add(tab_students, text="2. Quản lý Sinh viên")


# ====================================================================
# A. TAB QUẢN LÝ PHÒNG (ROOMS)
# ====================================================================

# ====== Frame nhập thông tin Phòng ======
frame_room_info = tk.Frame(tab_rooms)
frame_room_info.pack(pady=10, padx=10, fill="x")

tk.Label(frame_room_info, text="Mã Phòng").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_room_id = tk.Entry(frame_room_info, width=15)
entry_room_id.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_room_info, text="Sức chứa").grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_capacity = tk.Entry(frame_room_info, width=10)
entry_capacity.grid(row=0, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_room_info, text="Loại Phòng").grid(row=1, column=0, padx=5, pady=5, sticky="w")
cbb_room_type = ttk.Combobox(frame_room_info, values=["Thông thường","Ưu tiên"], width=15)
cbb_room_type.grid(row=1, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_room_info, text="Giá Thuê (VNĐ)").grid(row=1, column=2, padx=5, pady=5, sticky="w")
entry_room_price = tk.Entry(frame_room_info, width=15)
entry_room_price.grid(row=1, column=3, padx=5, pady=5, sticky="w")

# ====== Bảng danh sách Phòng (Treeview) ======
lbl_ds_room = tk.Label(tab_rooms, text="Danh sách Phòng (và số người đang ở)", font=("Arial", 10, "bold"))
lbl_ds_room.pack(pady=5, anchor="w", padx=10)

room_columns = ("room_id", "type", "capacity", "price", "current_occupancy")
tree_rooms = ttk.Treeview(tab_rooms, columns=room_columns, show="headings", height=10)

for col in room_columns:
    tree_rooms.heading(col, text=col.replace('_', ' ').capitalize())
tree_rooms.column("room_id", width=80, anchor="center")
tree_rooms.column("type", width=100)
tree_rooms.column("capacity", width=80, anchor="center")
tree_rooms.column("price", width=120, anchor="e")
tree_rooms.column("current_occupancy", width=100, anchor="center")
tree_rooms.pack(padx=10, pady=5, fill="both", expand=True)

# ====== Chức năng CRUD Phòng (Tương đương các hàm trong mẫu cũ) ======
def update_room_cbb():
    """Tải danh sách các phòng còn trống và cập nhật Combobox cbb_room."""
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            
            cur.execute("SELECT room_id, COUNT(cccd) FROM students GROUP BY room_id")
            occupancy_data = dict(cur.fetchall())
            
            cur.execute("SELECT room_id, capacity FROM rooms ORDER BY room_id")
            rooms = cur.fetchall()
            
            available_rooms = []
            for room_id, capacity in rooms:
                current_occupancy = occupancy_data.get(room_id, 0)
                if current_occupancy < capacity:
                    available_rooms.append(room_id)

            cbb_room.config(values=available_rooms)
            
        except Exception as e:
            messagebox.showerror("Lỗi Tải Phòng", f"Không thể tải danh sách phòng: {e}")
        finally:
            if conn: conn.close()
def clear_room_input():
    entry_room_id.delete(0, tk.END)
    entry_room_id.config(state='normal')
    entry_capacity.delete(0, tk.END)
    cbb_room_type.set("")
    entry_room_price.delete(0, tk.END)

def load_room_data():
    for i in tree_rooms.get_children():
        tree_rooms.delete(i)
    
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT room_id,type,capacity, price FROM rooms ORDER BY room_id")
            rooms = cur.fetchall()
            
            # Đếm số lượng sinh viên (nghiệp vụ KTX)
            cur.execute("SELECT room_id, COUNT(student_id) FROM students GROUP BY room_id")
            occupancy_data = dict(cur.fetchall())
            
            for room_id, type, capacity, price in rooms:
                occupancy = occupancy_data.get(room_id, 0)
                row_data = (room_id, type, capacity, f'{price:,.0f}', occupancy) 
                tree_rooms.insert("", tk.END, values=row_data)
        except Exception as e:
            messagebox.showerror("Lỗi Tải Dữ Liệu Phòng", str(e))
        finally:
            if conn: conn.close()

def them_room():
    room_id = entry_room_id.get().strip().upper()
    room_type = cbb_room_type.get()
    capacity = entry_capacity.get().strip()
    price_str = entry_room_price.get().strip().replace(',', '')
    
    if not all([room_id, room_type, capacity, price_str]):
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ thông tin phòng.")
        return
    
    try:
        capacity = int(capacity)
        price = int(price_str)
        if capacity <= 0 or price < 0: raise ValueError
    except ValueError:
        messagebox.showerror("Lỗi dữ liệu", "Sức chứa và Giá thuê phải là số nguyên dương.")
        return
        
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            sql = "INSERT INTO rooms (room_id, type, capacity, price) VALUES (%s, %s, %s, %s)"
            cur.execute(sql, (room_id, room_type, capacity, price))
            conn.commit()
            load_room_data()
            clear_room_input()
        except mysql.connector.Error as e:
            if e.errno == 1062:
                 messagebox.showerror("Lỗi Trùng Mã", f"Mã phòng '{room_id}' đã tồn tại.")
            else:
                 messagebox.showerror("Lỗi SQL", f"Không thể thêm phòng: {e}")
        finally:
            if conn: conn.close()

def sua_room_select(event=None):
    selected = tree_rooms.selection()
    if not selected: return
    
    values = tree_rooms.item(selected[0])["values"]
    clear_room_input() 
    
    entry_room_id.insert(0, values[0])
    entry_room_id.config(state='disabled') 
    
    cbb_room_type.set(values[1])
    entry_capacity.insert(0, values[2])
    entry_room_price.insert(0, str(values[3]).replace(',', ''))
    
def luu_room():
    room_id = entry_room_id.get() 
    room_type = cbb_room_type.get()
    capacity = entry_capacity.get().strip()
    price_str = entry_room_price.get().strip().replace(',', '')

    if not all([room_id, room_type, capacity, price_str]):
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ thông tin phòng.")
        return
        
    try:
        capacity = int(capacity)
        price = int(price_str)
    except ValueError:
        messagebox.showerror("Lỗi dữ liệu", "Sức chứa và Giá thuê phải là số nguyên.")
        return

    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            sql = "UPDATE rooms SET type=%s, capacity=%s, price=%s WHERE room_id=%s"
            cur.execute(sql, (room_type, capacity, price, room_id))
            conn.commit()
            load_room_data()
            clear_room_input()
        except Exception as e:
            messagebox.showerror("Lỗi Cập Nhật Phòng", str(e))
        finally:
            if conn: conn.close()
            entry_room_id.config(state='normal') 

def xoa_room():
    selected = tree_rooms.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn phòng để xóa.")
        return
    
    room_id = tree_rooms.item(selected)["values"][0]
    
    # Kiểm tra nghiệp vụ: Phòng còn sinh viên không
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(student_id) FROM students WHERE room_id=%s", (room_id,))
        count = cur.fetchone()[0]
        conn.close()
        
        if count > 0:
            messagebox.showerror("Lỗi Xóa", f"Phòng {room_id} đang có {count} sinh viên. Không thể xóa.")
            return

    if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc muốn xóa Phòng: {room_id}?"):
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM rooms WHERE room_id=%s", (room_id,))
                conn.commit()
                load_room_data()
                clear_room_input()
            except Exception as e:
                messagebox.showerror("Lỗi Xóa", str(e))
            finally:
                if conn: conn.close()

# ====== Frame nút Phòng ======
frame_room_btn = tk.Frame(tab_rooms)
frame_room_btn.pack(pady=10)

tk.Button(frame_room_btn, text="Thêm", width=8, command=them_room).grid(row=0, column=0, padx=5)
tk.Button(frame_room_btn, text="Lưu", width=8, command=luu_room).grid(row=0, column=1, padx=5)
tk.Button(frame_room_btn, text="Sửa", width=8, command=sua_room_select).grid(row=0, column=2, padx=5)
tk.Button(frame_room_btn, text="Hủy", width=8, command=clear_room_input).grid(row=0, column=3, padx=5)
tk.Button(frame_room_btn, text="Xóa", width=8, command=xoa_room).grid(row=0, column=4, padx=5)

tree_rooms.bind('<<TreeviewSelect>>', sua_room_select)


# ====================================================================
# B. TAB QUẢN LÝ SINH VIÊN (STUDENTS)
# ====================================================================

# ====== Frame nhập thông tin Sinh viên ======

frame_stu_info = tk.Frame(tab_students)
frame_stu_info.pack(pady=5, padx=10, fill="x")

# Variables (Must be defined):
entry_student_id = tk.Entry(frame_stu_info, width=15)
entry_student_name = tk.Entry(frame_stu_info, width=30)
stu_gender_var = tk.StringVar(value="Nam")
date_entry_stu = DateEntry(frame_stu_info, width=12, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
entry_major = tk.Entry(frame_stu_info, width=30)
cbb_room_assign = ttk.Combobox(frame_stu_info, values=[], width=15) # Combobox phòng

tk.Label(frame_stu_info, text="Mã SV").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_student_id.grid(row=0, column=1, padx=5, pady=5, sticky="w")
# ... other student entries grid placement ...
tk.Label(frame_stu_info, text="Mã Phòng").grid(row=2, column=2, padx=5, pady=5, sticky="w")
cbb_room_assign.grid(row=2, column=3, padx=5, pady=5, sticky="w")

lbl_ds = tk.Label(tab_students, text="Danh sách Sinh Viên", font=("Arial", 10, "bold"))
lbl_ds.pack(pady=5, anchor="w", padx=10)

# Định nghĩa lại các cột cho KTX
stu_columns = ("cccd", "name", "gender", "dob", "sdt", "room_id")
tree_students = ttk.Treeview(tab_students, columns=stu_columns, show="headings", height=10)     
for col in stu_columns:
    tree_students.heading(col, text=col.replace('_', ' ').capitalize())
tree_students.column("cccd", width=100, anchor="center")
tree_students.column("name", width=150)
tree_students.column("gender", width=70, anchor="center")
tree_students.column("dob", width=100, anchor="center") 
tree_students.column("sdt", width=100, anchor="center")
tree_students.column("room_id", width=150)
tree_students.pack(padx=10, pady=5, fill="both", expand=True)


# Placeholder functions for Tab 2 to maintain structure:
def update_room_cbb():
    """Tải danh sách các phòng còn trống và cập nhật Combobox cbb_room_assign."""
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            
            cur.execute("SELECT room_id, COUNT(cccd) FROM students GROUP BY room_id")
            occupancy_data = dict(cur.fetchall())
            
            cur.execute("SELECT room_id, capacity FROM rooms ORDER BY room_id")
            rooms = cur.fetchall()
            
            available_rooms = []
            for room_id, capacity in rooms:
                current_occupancy = occupancy_data.get(room_id, 0)
                if current_occupancy < capacity:
                    available_rooms.append(room_id)

            cbb_room_assign.config(values=available_rooms)
            
        except Exception as e:
            messagebox.showerror("Lỗi Tải Phòng", f"Không thể tải danh sách phòng: {e}")
        finally:
            if conn: conn.close()

def clear_stu_input():
    """Xóa trắng các ô nhập liệu cho Sinh viên và reset trạng thái."""
    global current_cccd_selected
    current_cccd_selected = None 
    
    # Chỉ còn CCCD, Tên, SĐT
    entry_cccd.delete(0, tk.END)
    entry_cccd.config(state='normal')
    
    entry_student_name.delete(0, tk.END)
    entry_sdt.delete(0, tk.END) # Đã thêm entry_sdt_stu
    
    # Các trường khác
    stu_gender_var.set("Nam") 
    date_entry_stu.set_date(date.today()) 
    cbb_room_assign.set("")
    update_room_cbb() 

def load_stu_data():
    """Tải dữ liệu Sinh viên từ DB vào Treeview và cập nhật Combobox Phòng."""
    for i in tree_students.get_children():
        tree_students.delete(i)
    
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            # Cập nhật SQL: Xóa student_id và major
            # Giả định cấu trúc bảng students: cccd (PK), name, gender, dob, sdt, room_id
            sql = """
                SELECT cccd, name, gender, dob, sdt, room_id 
                FROM students 
                ORDER BY room_id, name
            """
            cur.execute(sql)
            students = cur.fetchall()
            
            for row_data in students:
                tree_students.insert("", tk.END, values=row_data)
                
            update_room_cbb() 
        
        except Exception as e:
            messagebox.showerror("Lỗi Tải Dữ Liệu Sinh Viên", str(e))
        finally:
            if conn: conn.close()

def them_stu():
    """Thêm một Sinh viên mới vào cơ sở dữ liệu."""
    cccd = entry_cccd.get().strip()
    name = entry_student_name.get().strip()
    gender = stu_gender_var.get()
    dob = date_entry_stu.get_date().strftime("%Y-%m-%d") 
    sdt = entry_sdt.get().strip() # Đã sửa thành entry_sdt_stu
    room_id = cbb_room_assign.get()
    
    if not all([cccd, name, sdt, room_id]):
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ CCCD, Tên, SĐT và Phòng.")
        return
    
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            # Cập nhật SQL: Xóa student_id và major
            sql = """
                INSERT INTO students (cccd, name, gender, dob, sdt, room_id) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (cccd, name, gender, dob, sdt, room_id)) 
            conn.commit()
            
            load_stu_data()
            load_room_data() 
            clear_stu_input()
            messagebox.showinfo("Thành công", f"Đã thêm sinh viên: {name} (Phòng: {room_id})")
            
        except mysql.connector.Error as e:
            if e.errno == 1062: 
                 messagebox.showerror("Lỗi Trùng Mã", "CCCD đã tồn tại.")
            else:
                 messagebox.showerror("Lỗi SQL", f"Không thể thêm sinh viên: {e}")
        finally:
            if conn: conn.close()

def sua_stu_select(event=None):
    """Điền dữ liệu sinh viên được chọn vào form để Sửa."""
    global current_cccd_selected
    selected = tree_students.selection()
    if not selected: return
    
    # Thứ tự values mới: (cccd, name, gender, dob, sdt, room_id)
    values = tree_students.item(selected[0])["values"] 
    
    clear_stu_input() 
    
    # 1. Điền CCCD và vô hiệu hóa (CCCD được dùng làm khóa chính/điều kiện UPDATE)
    current_cccd_selected = values[0] 
    entry_cccd.insert(0, values[0])
    entry_cccd.config(state='disabled') 
    
    # 2. Điền các trường còn lại
    entry_student_name.insert(0, values[1])
    stu_gender_var.set(values[2])
    date_entry_stu.set_date(values[3]) 
    entry_sdt.insert(0, values[4]) # SĐT ở vị trí 4
    
    update_room_cbb()
    cbb_room_assign.set(values[5]) # Phòng ở vị trí 5

def luu_stu():
    """Lưu (cập nhật) thông tin Sinh viên đã chỉnh sửa (dùng CCCD làm điều kiện)."""
    global current_cccd_selected
    
    if current_cccd_selected is None:
        messagebox.showwarning("Chưa chọn", "Hãy chọn sinh viên cần cập nhật trên danh sách.")
        return

    cccd_to_update = current_cccd_selected 
    
    # Lấy dữ liệu mới từ form
    name = entry_student_name.get().strip()
    gender = stu_gender_var.get()
    dob = date_entry_stu.get_date().strftime("%Y-%m-%d")
    sdt = entry_sdt.get().strip()
    room_id = cbb_room_assign.get()
    
    if not all([name, sdt, room_id]):
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ thông tin.")
        return

    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            
            sql = """
                UPDATE students 
                SET name=%s, gender=%s, dob=%s, sdt=%s, room_id=%s 
                WHERE cccd=%s
            """
            cur.execute(sql, (name, gender, dob, sdt, room_id, cccd_to_update))
            conn.commit()
            
            load_stu_data()
            load_room_data() 
            clear_stu_input()
            messagebox.showinfo("Thành công", f"Đã cập nhật sinh viên có CCCD: {cccd_to_update}")
            
        except Exception as e:
            messagebox.showerror("Lỗi Cập Nhật Sinh Viên", str(e))
        finally:
            if conn: conn.close()
            entry_cccd.config(state='normal')
def xoa_stu():
    """Xóa Sinh viên được chọn khỏi cơ sở dữ liệu."""
    selected = tree_students.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn sinh viên để xóa.")
        return
    
    cccd = tree_students.item(selected)["values"][0] 
    name = tree_students.item(selected)["values"][1]
    
    confirm = messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc muốn xóa sinh viên {name} (CCCD: {cccd}) không?")
    
    if confirm:
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            try:
                sql = "DELETE FROM students WHERE cccd=%s"
                cur.execute(sql, (cccd,))
                conn.commit()
                
                load_stu_data()
                load_room_data() 
                clear_stu_input()
                messagebox.showinfo("Thành công", f"Đã xóa sinh viên có CCCD: {cccd}")
                
            except Exception as e:
                messagebox.showerror("Lỗi Xóa Sinh Viên", str(e))
            finally:
                if conn: conn.close
# ====== Frame nút Sinh viên ======
frame_stu_btn = tk.Frame(tab_students)
frame_stu_btn.pack(pady=10)

tk.Button(frame_stu_btn, text="Thêm", width=8, command=them_stu).grid(row=0, column=0, padx=5)
tk.Button(frame_stu_btn, text="Lưu", width=8, command=luu_stu).grid(row=0, column=1, padx=5)
tk.Button(frame_stu_btn, text="Sửa", width=8, command=sua_stu_select).grid(row=0, column=2, padx=5)
tk.Button(frame_stu_btn, text="Hủy", width=8, command=clear_stu_input).grid(row=0, column=3, padx=5)
tk.Button(frame_stu_btn, text="Xóa", width=8, command=xoa_stu).grid(row=0, column=4, padx=5)
tk.Button(frame_stu_btn, text="Thoát", width=8, command=root.quit).grid(row=0, column=5, padx=5)

tree_students.bind('<<TreeviewSelect>>', sua_stu_select)
# *--- END TAB 2 (Skeletal structure) ---*


# ====== Load dữ liệu ban đầu ======
def load_all_data():
        load_room_data()
        load_stu_data()

load_all_data()

# ====== Vòng lặp chính của giao diện ======
root.mainloop()