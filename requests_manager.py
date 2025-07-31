import customtkinter as ctk
from main import get_db_connection
from datetime import datetime

class RequestManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BloodVault™ - Request Handling & Emergency Support")
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
            text="🚑 Request Handling & Emergency Support",
            font=("Arial Black", 36, "bold"),
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
        ctk.CTkButton(self.sidebar, text="🏥 Submit Request", command=self.submit_request, **btn_opts).pack(pady=(16, 8))
        ctk.CTkButton(self.sidebar, text="🤝 Match Donors", command=self.match_donors, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="🚨 Emergency Requests", command=self.emergency_requests, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="⬅️ Main Menu", command=self.return_to_main_menu, **btn_opts).pack(pady=(40, 8))

        # --- Content Area ---
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#444B56", corner_radius=18)  # Slightly lighter content background
        self.content.pack(side="left", fill="both", expand=True, padx=(0, 30), pady=18)

        # --- Info Panel ---
        self.tips = [
            "Welcome to Request Handling & Emergency Support!",
            "🏥 Hospitals can submit blood/plasma requests here.",
            "🤝 The system matches available donors and updates inventory.",
            "🚨 Emergency requests are handled with priority.",
            "❤️ BloodVault™ saves lives with smart matching!"
        ]
        self.tip_index = 0
        self.info_panel = ctk.CTkLabel(
            self.content,
            text=self.tips[self.tip_index],
            font=("Arial", 16, "italic"),
            text_color="#F1C40F",  # Warm yellow
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
            text_color="#E74C3C"
        )
        self.copyright.place(relx=0.5, rely=0.98, anchor="s")

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def rotate_tips(self):
        self.tip_index = (self.tip_index + 1) % len(self.tips)
        self.info_panel.configure(text=self.tips[self.tip_index])
        self.after(4000, self.rotate_tips)

    # --- Submit Request ---
    def submit_request(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🏥 Submit Blood/Plasma Request", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        form_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        form_frame.pack(pady=10, padx=30, fill="x", expand=True)

        fields = {}
        def make_input(label_text):
            ctk.CTkLabel(form_frame, text=label_text, anchor="w").pack(pady=2, fill="x")
            entry = ctk.CTkEntry(form_frame)
            entry.pack(pady=5, fill="x")
            fields[label_text] = entry

        make_input("Hospital Name")
        make_input("Contact Number")
        make_input("Blood Group (e.g. A+)")
        make_input("Type (Blood/Plasma)")
        make_input("Volume (ml)")
        make_input("Urgency (Normal/Emergency)")

        def save_request():
            try:
                hospital = fields["Hospital Name"].get()
                contact = fields["Contact Number"].get()
                blood_group = fields["Blood Group (e.g. A+)"].get().upper()
                req_type = fields["Type (Blood/Plasma)"].get().capitalize()
                volume = int(fields["Volume (ml)"].get())
                urgency = fields["Urgency (Normal/Emergency)"].get().capitalize()
                status = "Pending"
                req_time = datetime.now()
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO requests (hospital_name, contact, blood_group, type, volume_ml, urgency, status, request_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (hospital, contact, blood_group, req_type, volume, urgency, status, req_time))
                conn.commit()
                conn.close()
                ctk.CTkLabel(self.content, text="✅ Request submitted!", text_color="#00FF00").pack(pady=10)
            except Exception as e:
                ctk.CTkLabel(self.content, text=f"Error: {e}", text_color="#FF0000").pack(pady=10)

        ctk.CTkButton(form_frame, text="Submit Request", command=save_request).pack(pady=20, fill="x")

    # --- Match Donors ---
    def match_donors(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🤝 Match Donors to Requests", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM requests WHERE status='Pending' ORDER BY urgency DESC, request_time ASC
        """)
        requests = cursor.fetchall()
        if not requests:
            ctk.CTkLabel(self.content, text="No pending requests.", text_color="#FFF").pack(pady=10)
            conn.close()
            return

        for req in requests:
            req_frame = ctk.CTkFrame(self.content, fg_color="#36393F", corner_radius=10)
            req_frame.pack(pady=10, padx=10, fill="x")
            info = (f"Request #{req['id']} | {req['hospital_name']} | {req['blood_group']} | "
                    f"{req['type']} | {req['volume_ml']}ml | Urgency: {req['urgency']}")
            ctk.CTkLabel(req_frame, text=info, font=("Arial", 14, "bold"), text_color="#F1C40F").pack(anchor="w", padx=10, pady=5)

            def make_match_func(req=req):
                def match():
                    conn2 = get_db_connection()
                    cursor2 = conn2.cursor(dictionary=True)
                    cursor2.execute("""
                        SELECT * FROM blood_inventory
                        WHERE blood_group=%s AND type=%s AND status='Available' AND expiry_date >= CURDATE()
                        ORDER BY expiry_date ASC
                    """, (req['blood_group'], req['type']))
                    units = cursor2.fetchall()
                    total_available = sum(u['volume_ml'] for u in units)
                    if total_available >= req['volume_ml']:
                        vol_needed = req['volume_ml']
                        for unit in units:
                            if vol_needed <= 0:
                                break
                            if unit['volume_ml'] <= vol_needed:
                                cursor2.execute("UPDATE blood_inventory SET status='Used' WHERE id=%s", (unit['id'],))
                                vol_needed -= unit['volume_ml']
                            else:
                                cursor2.execute("UPDATE blood_inventory SET volume_ml=volume_ml-%s WHERE id=%s", (vol_needed, unit['id']))
                                cursor2.execute("""
                                    INSERT INTO blood_inventory (type, blood_group, volume_ml, expiry_date, status)
                                    VALUES (%s, %s, %s, %s, 'Used')
                                """, (unit['type'], unit['blood_group'], vol_needed, unit['expiry_date']))
                                vol_needed = 0
                        cursor2.execute("UPDATE requests SET status='Fulfilled' WHERE id=%s", (req['id'],))
                        conn2.commit()
                        ctk.CTkLabel(req_frame, text="✅ Request Fulfilled & Inventory Updated!", text_color="#00FF00").pack(pady=5)
                    else:
                        ctk.CTkLabel(req_frame, text="❌ Not enough stock to fulfill this request.", text_color="#FF0000").pack(pady=5)
                    conn2.close()
                return match

            ctk.CTkButton(req_frame, text="Match & Fulfill", command=make_match_func()).pack(pady=5, padx=10, fill="x")
        conn.close()

    # --- Emergency Requests ---
    def emergency_requests(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🚨 Emergency Requests", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM requests WHERE urgency='Emergency' AND status='Pending' ORDER BY request_time ASC
        """)
        emergencies = cursor.fetchall()
        if not emergencies:
            ctk.CTkLabel(self.content, text="No emergency requests.", text_color="#FFF").pack(pady=10)
            conn.close()
            return

        for req in emergencies:
            req_frame = ctk.CTkFrame(self.content, fg_color="#36393F", corner_radius=10)
            req_frame.pack(pady=10, padx=10, fill="x")
            info = (f"Emergency #{req['id']} | {req['hospital_name']} | {req['blood_group']} | "
                    f"{req['type']} | {req['volume_ml']}ml | {req['request_time']}")
            ctk.CTkLabel(req_frame, text=info, font=("Arial", 14, "bold"), text_color="#F1C40F").pack(anchor="w", padx=10, pady=5)

            def make_emergency_func(req=req):
                def handle():
                    conn2 = get_db_connection()
                    cursor2 = conn2.cursor(dictionary=True)
                    cursor2.execute("""
                        SELECT * FROM blood_inventory
                        WHERE blood_group=%s AND type=%s AND status='Available' AND expiry_date >= CURDATE()
                        ORDER BY expiry_date ASC
                    """, (req['blood_group'], req['type']))
                    units = cursor2.fetchall()
                    total_available = sum(u['volume_ml'] for u in units)
                    if total_available >= req['volume_ml']:
                        vol_needed = req['volume_ml']
                        for unit in units:
                            if vol_needed <= 0:
                                break
                            if unit['volume_ml'] <= vol_needed:
                                cursor2.execute("UPDATE blood_inventory SET status='Used' WHERE id=%s", (unit['id'],))
                                vol_needed -= unit['volume_ml']
                            else:
                                cursor2.execute("UPDATE blood_inventory SET volume_ml=volume_ml-%s WHERE id=%s", (vol_needed, unit['id']))
                                cursor2.execute("""
                                    INSERT INTO blood_inventory (type, blood_group, volume_ml, expiry_date, status)
                                    VALUES (%s, %s, %s, %s, 'Used')
                                """, (unit['type'], unit['blood_group'], vol_needed, unit['expiry_date']))
                                vol_needed = 0
                        cursor2.execute("UPDATE requests SET status='Fulfilled' WHERE id=%s", (req['id'],))
                        conn2.commit()
                        ctk.CTkLabel(req_frame, text="✅ Emergency Fulfilled!", text_color="#00FF00").pack(pady=5)
                    else:
                        ctk.CTkLabel(req_frame, text="❌ Not enough stock for this emergency.", text_color="#FF0000").pack(pady=5)
                    conn2.close()
                return handle

            ctk.CTkButton(req_frame, text="Handle Emergency", command=make_emergency_func()).pack(pady=5, padx=10, fill="x")
        conn.close()

    def return_to_main_menu(self):
        self.destroy()
        from main import BloodVaultMainMenu
        app = BloodVaultMainMenu()
        app.mainloop()

def run_manager():
    app = RequestManager()
    app.mainloop()
