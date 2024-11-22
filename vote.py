import pymysql
import tkinter as tk
from tkinter import messagebox, font as tkFont
from tkinter import ttk

DB_HOST = 'localhost'
DB_USER = 'svs'
DB_PASSWORD = 'Admin121#'
DB_NAME = 'vote_db'


def connect_db():
    """Establishes a connection to the database."""
    try:
        return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        return None

def register_user(student_id, student_name):
    """Registers a new user in the database."""
    if not student_id or not student_name:
        messagebox.showerror("Input Error", "Both Student ID and Name are required.")
        return

    conn = connect_db()
    if conn is None:
        return 

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE student_id=%s", (student_id,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Student ID already exists. Please choose a different ID.")
                return

            cursor.execute("INSERT INTO users (student_id, student_name, has_voted) VALUES (%s, %s, %s)", 
                           (student_id, student_name, False))
            conn.commit()
            messagebox.showinfo("Success", f"User with ID '{student_id}' registered successfully.")
    finally:
        conn.close()

def add_candidate(name):
    """Adds a candidate to the database."""
    if not name:
        messagebox.showerror("Input Error", "Candidate name is required.")
        return

    conn = connect_db()
    if conn is None:
        return  

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM candidates WHERE name=%s", (name,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Candidate already exists.")
                return

            cursor.execute("INSERT INTO candidates (name, vote_count) VALUES (%s, %s)", (name, 0))
            conn.commit()
            messagebox.showinfo("Success", f"Candidate '{name}' added successfully.")
    finally:
        conn.close()

def vote(student_id, candidate_name):
    """Records a vote for a candidate by a student."""
    if not student_id or not candidate_name:
        messagebox.showerror("Input Error", "Both Student ID and Candidate Name are required.")
        return

    conn = connect_db()
    if conn is None:
        return  

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT has_voted FROM users WHERE student_id=%s", (student_id,))
            user = cursor.fetchone()

            if user is None:
                messagebox.showerror("Error", "User not registered. Please register first.")
                return

            if user[0]:
                messagebox.showerror("Error", "You have already voted!")
                return

            cursor.execute("SELECT * FROM candidates WHERE name=%s", (candidate_name,))
            candidate = cursor.fetchone()

            if candidate is None:
                messagebox.showerror("Error", "Candidate does not exist.")
                return

            cursor.execute("UPDATE candidates SET vote_count = vote_count + 1 WHERE name=%s", (candidate_name,))
            cursor.execute("UPDATE users SET has_voted = %s WHERE student_id=%s", (True, student_id))
            conn.commit()
            messagebox.showinfo("Success", f"Vote cast successfully for '{candidate_name}'!")
    finally:
        conn.close()

def view_results():
    """Displays the voting results."""
    conn = connect_db()
    if conn is None:
        return  

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, vote_count FROM candidates")
            results = cursor.fetchall()

           
            clear_frame(main_content_frame)
          
            results_frame = tk.Frame(main_content_frame, bg="#f0f0f0")
            results_frame.pack(fill=tk.BOTH, expand=True)

            results_label = tk.Label(results_frame, text="Voting Results", font=("Helvetica", 14, "bold"), bg="#f0f0f0", fg="#333")
            results_label.pack(pady=10)

            
            columns = ("Candidate", "Votes")
            tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=8)
            tree.pack(pady=10, fill=tk.BOTH, expand=True)

      
            tree.heading("Candidate", text="Candidate", anchor=tk.W)
            tree.heading("Votes", text="Votes", anchor=tk.W)

            tree.column("Candidate", width=200, anchor=tk.W)
            tree.column("Votes", width=100, anchor=tk.CENTER)

         
            for row in results:
                tree.insert("", tk.END, values=row)

           
            scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

           
            style = ttk.Style()
            style.configure("Treeview", background="#EAEAEA", foreground="black", rowheight=25, fieldbackground="#EAEAEA")
            style.map("Treeview", background=[("selected", "#A4C8E1")])

    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        conn.close()

def fetch_candidates():
    """Fetches candidate names from the database."""
    conn = connect_db()
    if conn is None:
        return []  

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM candidates")
            candidates = cursor.fetchall()
            return [candidate[0] for candidate in candidates]
    finally:
        conn.close()
        
def fetch_students():
    """Fetches student names from the database."""
    conn = connect_db()
    if conn is None:
        return []  

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT student_name FROM users")
            students = cursor.fetchall()
            return [student[0] for student in students]
    finally:
        conn.close()

def fetch_student_ids():
    """Fetches student IDs from the database."""
    conn = connect_db()
    if conn is None:
        return []  

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT student_id FROM users")
            student_ids = cursor.fetchall()
            return [student_id[0] for student_id in student_ids]
    finally:
        conn.close()

def create_gui():
    """Sets up the main GUI window."""
    root = tk.Tk()
    root.title("Student Voting System")
    root.geometry("600x400")
    root.configure(bg="#f0f0f0")

    custom_font = tkFont.Font(family="Helvetica", size=12)

    menu_bar = tk.Menu(root)
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Student Voting System v1.0"))
    menu_bar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menu_bar)

    side_menu_frame = tk.Frame(root, bg="#D9EAD3", width=150)
    side_menu_frame.pack(side=tk.LEFT, fill=tk.Y)

    global main_content_frame
    main_content_frame = tk.Frame(root, bg="#f0f0f0")
    main_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    title_label = tk.Label(main_content_frame, text="--- Student Voting System ---", font=("Helvetica", 16, "bold"), bg="#f0f0f0", fg="#333")
    title_label.pack(pady=10)

    tk.Button(side_menu_frame, text="User Registration", command=lambda: show_registration(main_content_frame), bg="#A4C8E1").pack(fill=tk.X, padx=5, pady=5)
    tk.Button(side_menu_frame, text="Add Candidate", command=lambda: show_add_candidate(main_content_frame), bg="#A4C8E1").pack(fill=tk.X, padx=5, pady=5)
    tk.Button(side_menu_frame, text="Vote", command=lambda: show_vote(main_content_frame), bg="#A4C8E1").pack(fill=tk.X, padx=5, pady=5)
    tk.Button(side_menu_frame, text="View Results", command=view_results, bg="#A4C8E1").pack(fill=tk.X, padx=5, pady=5)
    tk.Button(side_menu_frame, text="Exit", command=root.quit, bg="#A4C8E1").pack(fill=tk.X, padx=5, pady=5)

    root.mainloop()

def show_registration(frame):
    """Displays the registration interface."""
    clear_frame(frame)
    tk.Label(frame, text="User Registration", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=5)

    tk.Label(frame, text="Student ID:", bg="#f0f0f0").pack(pady=5)
    student_id_entry = tk.Entry(frame)
    student_id_entry.pack(pady=5)

    tk.Label(frame, text="Student Name:", bg="#f0f0f0").pack(pady=5)
    student_name_entry = tk.Entry(frame)
    student_name_entry.pack(pady=5)

    register_button = tk.Button(frame, text="Register", command=lambda: register_user(student_id_entry.get(), student_name_entry.get()), bg="#A4C8E1")
    register_button.pack(pady=20)
def show_add_candidate(frame):
    """Displays the candidate addition interface."""
    clear_frame(frame)
    tk.Label(frame, text="Add Candidate", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=5)

    tk.Label(frame, text="Candidate Name:", bg="#f0f0f0").pack(pady=5)
    student_names = fetch_students() 
    student_name_combo = ttk.Combobox(frame, values=student_names)
    student_name_combo.pack(pady=5)
           

    add_button = tk.Button(frame, text="Add Candidate", command=lambda: add_candidate(student_name_combo.get()), bg="#A4C8E1")
    add_button.pack(pady=20)


def show_vote(frame):
    """Displays the voting interface."""
    clear_frame(frame)
    tk.Label(frame, text="Vote for Candidate", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=5)

    tk.Label(frame, text="Student ID:", bg="#f0f0f0").pack(pady=5)
    student_id_entry = tk.Entry(frame)
    student_id_entry.pack(pady=5)

    tk.Label(frame, text="Candidates:", bg="#f0f0f0").pack(pady=5)
    candidate_name_combo = ttk.Combobox(frame, values=fetch_candidates())
    candidate_name_combo.pack(pady=5)

    vote_button = tk.Button(frame, text="Vote", command=lambda: vote(student_id_entry.get(), candidate_name_combo.get()), bg="#A4C8E1")
    vote_button.pack(pady=20)

def clear_frame(frame):
    """Clears the contents of a frame."""
    for widget in frame.winfo_children():
        widget.destroy()


if __name__ == "__main__":
    create_gui()
