import customtkinter as ctk
from tkcalendar import DateEntry

from datetime import datetime
import tkinter.messagebox as mbox
import geocoder
from main import get_db_connection

# --- Eligibility Checker (90-day rule) ---
def is_eligible(last_donation_date):
    if not last_donation_date:
        return True, 0
    if isinstance(last_donation_date, str):
        last_date = datetime.strptime(last_donation_date, "%Y-%m-%d")
    else:
        last_date = last_donation_date
    # Ensure last_date is a date object
    if hasattr(last_date, "date"):
        last_date = last_date.date()
    days_since = (datetime.now().date() - last_date).days
    return days_since >= 90, max(0, 90 - days_since)

# --- Main GUI Class ---

class BloodVaultManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BloodVault™ - Donor & Recipient Management")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height-50}+0+0")
        ctk.set_appearance_mode("dark")
        self.configure(bg="#2C2F33")  # Dark gray background

        # --- Shadow and Main Frame ---
        self.shadow = ctk.CTkFrame(self, corner_radius=32, fg_color="#36393F")  # Slightly lighter gray
        self.shadow.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)

        self.main_frame = ctk.CTkFrame(self, corner_radius=24, fg_color="#444B56", border_width=2, border_color="#E74C3C")  # Soft red border
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.90, relheight=0.90)

        # --- Title ---
        self.label = ctk.CTkLabel(
            self.main_frame,
            text="🩸 Donor & Recipient Management",
            font=("Arial Black", 38, "bold"),
            text_color="#E74C3C"  # Soft red text
        )
        self.label.pack(pady=(32, 8))

        # --- Glowing Divider ---
        divider = ctk.CTkLabel(self.main_frame, text="", fg_color="#E74C3C", height=3, width=700, corner_radius=2)
        divider.pack(pady=(8, 18))

        # --- Sidebar Navigation ---
        self.sidebar = ctk.CTkFrame(self.main_frame, fg_color="#36393F", corner_radius=18, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(30, 18), pady=18)

        btn_opts = {
            "width": 180, "height": 40, "corner_radius": 12,
            "font": ("Arial", 15, "bold"),
            "fg_color": "#E74C3C",  # Soft red buttons
            "hover_color": "#FF6B6B",  # Softer hover red
            "text_color": "#FFF",
            "anchor": "w"
        }
        ctk.CTkButton(self.sidebar, text="➕ Add Donor", command=self.add_record, **btn_opts).pack(pady=(16, 8))
        ctk.CTkButton(self.sidebar, text="✏️ Update Donor", command=self.update_record, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="🔍 Search Donor", command=self.search_record, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="🗑️ Delete Donor", command=self.delete_record, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="📜 Donation History", command=self.show_history, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="🩸 Check Eligibility", command=self.check_eligibility, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="😎 Face Login", command=self.face_login, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="⬅️ Main Menu", command=self.return_to_main_menu, **btn_opts).pack(pady=(40, 8))

        # --- Content Area ---
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#444B56", corner_radius=18)
        self.content.pack(side="left", fill="both", expand=True, padx=(0, 30), pady=18)

        # --- Info Panel ---
        self.tips = [
            "Welcome to Donor & Recipient Management!\nAdd, update, or search donors easily.",
            "💡 Tip: Use the sidebar to access all donor features.",
            "🩸 Keep donor records up to date for better matching.",
            "🔒 All your data is securely managed.",
            "❤️ Thank you for being a lifesaver!"
        ]
        self.tip_index = 0
        self.info_panel = ctk.CTkLabel(
            self.content,
            text=self.tips[self.tip_index],
            font=("Arial", 16, "italic"),
            text_color="#F1C40F",  # Warm yellow for info panel text
            fg_color="#36393F",
            corner_radius=12,
            width=500,
            height=60
        )
        self.info_panel.pack(pady=(30, 10))
        self.rotate_tips()

        # --- Copyright ---
        self.copyright = ctk.CTkLabel(
            self.main_frame,
            text="© Karthik Vinod. All rights reserved.",
            font=("Arial", 12),
            text_color="#E74C3C"  # Soft red
        )
        self.copyright.place(relx=0.5, rely=0.98, anchor="s")

        self.face_click_count = 0

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # --- Info Panel Rotator ---
    def rotate_tips(self):
        self.tip_index = (self.tip_index + 1) % len(self.tips)
        self.info_panel.configure(text=self.tips[self.tip_index])
        self.after(4000, self.rotate_tips)

    # --- Add Donor Form ---
    def add_record(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="➕ Add Donor", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)

        # --- Form Frame for wrapping ---
        form_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        form_frame.pack(pady=10, padx=30, fill="x", expand=True)

        fields = {}
        def make_input(label_text):
            ctk.CTkLabel(form_frame, text=label_text, anchor="w").pack(pady=2, fill="x")
            entry = ctk.CTkEntry(form_frame)
            entry.pack(pady=5, fill="x")
            fields[label_text] = entry

        make_input("Name")
        make_input("Age")
        make_input("Gender (M/F/O)")
        ctk.CTkLabel(form_frame, text="Blood Group", anchor="w").pack(pady=2, fill="x")
        blood_group_var = ctk.StringVar(value="A+")
        blood_dropdown = ctk.CTkOptionMenu(form_frame, variable=blood_group_var, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        blood_dropdown.pack(pady=5, fill="x")
        make_input("Phone")
        make_input("Email")
        make_input("City")

        ctk.CTkLabel(form_frame, text="Last Donation Date", anchor="w").pack(pady=10, fill="x")
        date_picker = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        date_picker.pack(pady=5, fill="x")

        def save_donor():
            try:
                name = fields["Name"].get()
                age = int(fields["Age"].get())
                gender = fields["Gender (M/F/O)"].get()
                blood_group = blood_group_var.get()
                phone = fields["Phone"].get()
                email = fields["Email"].get()
                city = fields["City"].get()
                last_donation = date_picker.get_date().strftime("%Y-%m-%d")
                lat, lng = None, None
                try:
                    g = geocoder.ip('me')
                    lat, lng = g.latlng
                except:
                    pass
                conn = get_db_connection()
                cursor = conn.cursor()
                sql = """
                    INSERT INTO donors 
                    (name, age, gender, blood_group, phone, email, city, latitude, longitude, last_donation_date, registration_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (name, age, gender, blood_group, phone, email, city, lat, lng, last_donation, datetime.today())
                cursor.execute(sql, values)
                conn.commit()
                conn.close()
                mbox.showinfo("Success", "✅ Donor added successfully!")
                self.clear_content()
            except Exception as e:
                mbox.showerror("Error", str(e))

        ctk.CTkButton(form_frame, text="Save", command=save_donor).pack(pady=20, fill="x")

    # --- Update Donor ---
    def update_record(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="✏️ Update Donor", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        ctk.CTkLabel(self.content, text="Enter Donor ID to Update:").pack(pady=5)
        id_entry = ctk.CTkEntry(self.content)
        id_entry.pack(pady=5)
        fields = {}
        def fetch_and_update():
            donor_id = id_entry.get()
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM donors WHERE donor_id=%s", (donor_id,))
            donor = cursor.fetchone()
            if not donor:
                mbox.showerror("Error", "Donor not found!")
                conn.close()
                return
            for field in ["name", "age", "gender", "blood_group", "phone", "email", "city"]:
                ctk.CTkLabel(self.content, text=f"{field.capitalize()}:").pack(pady=2)
                entry = ctk.CTkEntry(self.content)
                entry.insert(0, str(donor[field]))
                entry.pack(pady=2)
                fields[field] = entry
            def save_update():
                try:
                    sql = """
                        UPDATE donors SET name=%s, age=%s, gender=%s, blood_group=%s, phone=%s, email=%s, city=%s
                        WHERE donor_id=%s
                    """
                    values = (
                        fields["name"].get(),
                        int(fields["age"].get()),
                        fields["gender"].get(),
                        fields["blood_group"].get(),
                        fields["phone"].get(),
                        fields["email"].get(),
                        fields["city"].get(),
                        donor_id
                    )
                    cursor.execute(sql, values)
                    conn.commit()
                    mbox.showinfo("Success", "✅ Donor updated!")
                    self.clear_content()
                except Exception as e:
                    mbox.showerror("Error", str(e))
                finally:
                    conn.close()
            ctk.CTkButton(self.content, text="Save Update", command=save_update).pack(pady=10)
        ctk.CTkButton(self.content, text="Fetch Donor", command=fetch_and_update).pack(pady=10)

    # --- Search Donor ---
    def search_record(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🔍 Search Donor", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        ctk.CTkLabel(self.content, text="Search by Name or Blood Group:").pack(pady=5)
        query_entry = ctk.CTkEntry(self.content)
        query_entry.pack(pady=5)
        result_box = ctk.CTkTextbox(self.content, width=350, height=200)
        result_box.pack(pady=10)
        def do_search():
            query = query_entry.get()
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM donors WHERE name LIKE %s OR blood_group LIKE %s",
                (f"%{query}%", f"%{query}%")
            )
            results = cursor.fetchall()
            result_box.delete("1.0", "end")
            if results:
                for donor in results:
                    result_box.insert("end", f"ID: {donor['donor_id']}, Name: {donor['name']}, Blood: {donor['blood_group']}\n")
            else:
                result_box.insert("end", "No donors found.")
            conn.close()
        ctk.CTkButton(self.content, text="Search", command=do_search).pack(pady=10)

    # --- Delete Donor ---
    def delete_record(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🗑️ Delete Donor", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        ctk.CTkLabel(self.content, text="Enter Donor ID to Delete:").pack(pady=5)
        id_entry = ctk.CTkEntry(self.content)
        id_entry.pack(pady=5)
        def do_delete():
            donor_id = id_entry.get()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM donors WHERE donor_id=%s", (donor_id,))
            conn.commit()
            conn.close()
            mbox.showinfo("Deleted", "🗑️ Donor deleted (if ID existed).")
            self.clear_content()
        ctk.CTkButton(self.content, text="Delete", command=do_delete).pack(pady=10)

    # --- Donation History ---
    def show_history(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="📜 Donation History", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        ctk.CTkLabel(self.content, text="Enter Donor ID:").pack(pady=5)
        id_entry = ctk.CTkEntry(self.content)
        id_entry.pack(pady=5)
        result_box = ctk.CTkTextbox(self.content, width=450, height=250)
        result_box.pack(pady=10)
        def fetch_history():
            donor_id = id_entry.get()
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM donation_history WHERE donor_id=%s ORDER BY donation_date DESC",
                (donor_id,)
            )
            history = cursor.fetchall()
            result_box.delete("1.0", "end")
            if history:
                for record in history:
                    result_box.insert("end", f"Date: {record['donation_date']}, Volume: {record['volume_ml']}ml\n")
            else:
                result_box.insert("end", "No donation history found.")
            conn.close()
        ctk.CTkButton(self.content, text="Show History", command=fetch_history).pack(pady=10)

    # --- Eligibility Checker ---
    def check_eligibility(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🩸 Check Eligibility", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        ctk.CTkLabel(self.content, text="Select last donation date:").pack(pady=10)
        date_picker = DateEntry(self.content, date_pattern='yyyy-mm-dd')
        date_picker.pack(pady=10)
        def check():
            last_date = date_picker.get_date().strftime("%Y-%m-%d")
            eligible, days_left = is_eligible(last_date)
            if eligible:
                msg = "✅ Eligible for donation!"
            else:
                msg = f"❌ Not eligible (wait {days_left} more days)"
            mbox.showinfo("Eligibility", msg)
        ctk.CTkButton(self.content, text="Check", command=check).pack(pady=10)

    # --- Face Recognition Login (Easter Egg) ---
    def face_login(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="😎 Easter Egg", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        self.face_click_count += 1
        if self.face_click_count == 5:
            mbox.showinfo("Easter Egg!", "🎉 You found the BloodVault secret!\nStay awesome, lifesaver! 🩸")
            self.face_click_count = 0
        else:
            mbox.showinfo("Easter Egg", "Try clicking this 5 times for a surprise!")

    def return_to_main_menu(self):
        self.destroy()
        from main import BloodVaultMainMenu
        app = BloodVaultMainMenu()
        app.mainloop()

# --- Entry Point ---
def run_manager():
    app = BloodVaultManager()
    app.mainloop()
