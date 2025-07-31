import customtkinter as ctk
from datetime import datetime, timedelta
from main import get_db_connection

class InventoryManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BloodVault™ - Inventory Management")
        self.geometry("1050x700")
        ctk.set_appearance_mode("dark")
        self.configure(bg="#2C2F33")  # Dark gray background

        # --- Shadow and Main Frame ---
        self.shadow = ctk.CTkFrame(self, corner_radius=32, fg_color="#36393F")  # Medium dark gray
        self.shadow.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)

        self.main_frame = ctk.CTkFrame(self, corner_radius=24, fg_color="#444B56", border_width=2, border_color="#E74C3C")  # Softer red border
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.90, relheight=0.90)

        # --- Title ---
        self.label = ctk.CTkLabel(
            self.main_frame,
            text="🩸 Blood & Plasma Inventory",
            font=("Arial Black", 38, "bold"),
            text_color="#E74C3C"  # Softer red
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
            "fg_color": "#E74C3C",  # Softer red buttons
            "hover_color": "#FF6B6B",  # Softer hover red
            "text_color": "#FFF",
            "anchor": "w"
        }
        ctk.CTkButton(self.sidebar, text="📦 Track Stock", command=self.show_track_stock, **btn_opts).pack(pady=(16, 8))
        ctk.CTkButton(self.sidebar, text="✏️ Add/Update Stock", command=self.show_update_stock, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="⏰ Expiry Alerts", command=self.show_expiry_alerts, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="🧬 Platelet Tracking", command=self.show_platelet_tracking, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="🔍 Search Availability", command=self.show_search_availability, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="⬅️ Main Menu", command=self.return_to_main_menu, **btn_opts).pack(pady=(40, 8))

        # --- Content Area ---
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#444B56", corner_radius=18)  # Slightly lighter content background
        self.content.pack(side="left", fill="both", expand=True, padx=(0, 30), pady=18)

        # --- Info Panel ---
        self.info_panel = ctk.CTkLabel(
            self.content,
            text="Welcome to Inventory Management!\nSelect an option from the left.",
            font=("Arial", 16, "italic"),
            text_color="#F1C40F",  # Warm yellow
            fg_color="#36393F",
            corner_radius=12,
            width=500,
            height=60
        )
        self.info_panel.pack(pady=(30, 10))

        # --- Copyright ---
        self.copyright = ctk.CTkLabel(
            self.main_frame,
            text="© 2025 Karthik Vinod. All rights reserved.",
            font=("Arial", 12),
            text_color="#E74C3C"
        )
        self.copyright.place(relx=0.5, rely=0.98, anchor="s")

    # --- Navigation Functions ---
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_track_stock(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="📦 Track Stock", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT type, blood_group, SUM(volume_ml) as total_volume, COUNT(*) as units
            FROM blood_inventory
            WHERE status='Available' AND expiry_date >= CURDATE()
            GROUP BY type, blood_group
            ORDER BY type, blood_group
        """)
        rows = cursor.fetchall()
        if not rows:
            ctk.CTkLabel(self.content, text="No stock available.", font=("Arial", 16), text_color="#FFF").pack(pady=10)
        else:
            for row in rows:
                ctk.CTkLabel(self.content, text=f"{row['type']} {row['blood_group']}: {row['units']} units, {row['total_volume']} ml", font=("Arial", 15), text_color="#FFF").pack(pady=4)
        conn.close()

    def show_update_stock(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="✏️ Add/Update Stock", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)

        # Input fields
        fields = {}
        for label in ["Type (Blood/Plasma/Platelet)", "Blood Group (e.g. A+)", "Volume (ml)", "Expiry Date (YYYY-MM-DD)", "Donor ID (optional)"]:
            ctk.CTkLabel(self.content, text=label, font=("Arial", 14)).pack(pady=2)
            entry = ctk.CTkEntry(self.content, width=220)
            entry.pack(pady=2)
            fields[label] = entry

        def save_stock():
            try:
                type_ = fields["Type (Blood/Plasma/Platelet)"].get().capitalize()
                blood_group = fields["Blood Group (e.g. A+)"].get().upper()
                volume = int(fields["Volume (ml)"].get())
                expiry = fields["Expiry Date (YYYY-MM-DD)"].get()
                donor_id = fields["Donor ID (optional)"].get()
                donor_id = int(donor_id) if donor_id else None
            except Exception as e:
                ctk.CTkLabel(self.content, text=f"Invalid input: {e}", font=("Arial", 15), text_color="#FF6B6B").pack(pady=10)
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            sql = """
                INSERT INTO blood_inventory (type, blood_group, volume_ml, expiry_date, donor_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (type_, blood_group, volume, expiry, donor_id))
            conn.commit()
            conn.close()
            ctk.CTkLabel(self.content, text="Stock added successfully!", font=("Arial", 15), text_color="#F1C40F").pack(pady=10)

        ctk.CTkButton(self.content, text="Save", command=save_stock, fg_color="#E74C3C", text_color="#FFF", corner_radius=10, width=120, height=36).pack(pady=12)

    def show_expiry_alerts(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="⏰ Expiry Alerts", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        alert_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT id, type, blood_group, volume_ml, expiry_date
            FROM blood_inventory
            WHERE status='Available' AND expiry_date <= %s
            ORDER BY expiry_date
        """, (alert_date,))
        rows = cursor.fetchall()
        if not rows:
            ctk.CTkLabel(self.content, text="No units expiring soon.", font=("Arial", 16), text_color="#FFF").pack(pady=10)
        else:
            for row in rows:
                ctk.CTkLabel(self.content, text=f"ID {row['id']}: {row['type']} {row['blood_group']} - {row['volume_ml']}ml, expires on {row['expiry_date']}", font=("Arial", 15), text_color="#FFF").pack(pady=4)
        conn.close()

    def show_platelet_tracking(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🧬 Platelet Tracking", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, blood_group, volume_ml, expiry_date, status
            FROM blood_inventory
            WHERE type='Platelet'
            ORDER BY expiry_date
        """)
        rows = cursor.fetchall()
        if not rows:
            ctk.CTkLabel(self.content, text="No platelets in inventory.", font=("Arial", 16), text_color="#FFF").pack(pady=10)
        else:
            for row in rows:
                ctk.CTkLabel(self.content, text=f"ID {row['id']}: {row['blood_group']} - {row['volume_ml']}ml, expires on {row['expiry_date']}, status: {row['status']}", font=("Arial", 15), text_color="#FFF").pack(pady=4)
        conn.close()

    def show_search_availability(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🔍 Search Availability", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)

        fields = {}
        for label in ["Type (Blood/Plasma/Platelet)", "Blood Group (e.g. A+)"]:
            ctk.CTkLabel(self.content, text=label, font=("Arial", 14)).pack(pady=2)
            entry = ctk.CTkEntry(self.content, width=220)
            entry.pack(pady=2)
            fields[label] = entry

        result_box = ctk.CTkTextbox(self.content, width=500, height=180)
        result_box.pack(pady=10)

        def do_search():
            type_ = fields["Type (Blood/Plasma/Platelet)"].get().capitalize()
            blood_group = fields["Blood Group (e.g. A+)"].get().upper()
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, volume_ml, expiry_date
                FROM blood_inventory
                WHERE type=%s AND blood_group=%s AND status='Available' AND expiry_date >= CURDATE()
                ORDER BY expiry_date
            """, (type_, blood_group))
            rows = cursor.fetchall()
            result_box.delete("1.0", "end")
            if not rows:
                result_box.insert("end", "No available units.")
            else:
                for row in rows:
                    result_box.insert("end", f"ID {row['id']}: {row['volume_ml']}ml, expires on {row['expiry_date']}\n")
            conn.close()

        ctk.CTkButton(self.content, text="Search", command=do_search, fg_color="#E74C3C", text_color="#FFF", corner_radius=10, width=120, height=36).pack(pady=8)

    def return_to_main_menu(self):
        self.destroy()
        from main import BloodVaultMainMenu
        app = BloodVaultMainMenu()
        app.mainloop()

def run_manager():
    app = InventoryManager()
    app.mainloop()
