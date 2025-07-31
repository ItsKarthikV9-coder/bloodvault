import customtkinter as ctk
import tkinter.messagebox as mbox
import threading
import pywhatkit
from main import get_db_connection
from donor_recipient import is_eligible  # Make sure this is accessible

def format_uae_phone(phone):
    phone = str(phone).strip()
    # Remove spaces, dashes, parentheses
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if phone.startswith("+971"):
        return phone
    if phone.startswith("0"):
        return "+971" + phone[1:]
    return "+971" + phone

class WhatsAppAlertsManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BloodVault™ - WhatsApp Alert System")
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
            text="📲 WhatsApp Alert System",
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
        ctk.CTkButton(self.sidebar, text="🚨 Emergency Alerts", command=self.build_alert_ui, **btn_opts).pack(pady=(16, 8))
        ctk.CTkButton(self.sidebar, text="⏰ Eligibility Reminders", command=self.build_reminder_ui, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="⬅️ Main Menu", command=self.return_to_main_menu, **btn_opts).pack(pady=(40, 8))

        # --- Content Area ---
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#444B56", corner_radius=18)  # Slightly lighter content background
        self.content.pack(side="left", fill="both", expand=True, padx=(0, 30), pady=18)

        # --- Info Panel ---
        self.tips = [
            "Welcome to the WhatsApp Alert System!",
            "🚨 Instantly notify eligible donors in emergencies.",
            "⏰ Remind donors when they become eligible again.",
            "📲 All alerts are sent via WhatsApp Web.",
            "❤️ BloodVault™ helps you save lives faster!"
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

        self.build_alert_ui()

    def clear_content(self):
        for widget in self.content.winfo_children():
            if widget != self.info_panel:
                widget.destroy()

    def rotate_tips(self):
        self.tip_index = (self.tip_index + 1) % len(self.tips)
        self.info_panel.configure(text=self.tips[self.tip_index])
        self.after(4000, self.rotate_tips)

    def build_alert_ui(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="Send Emergency WhatsApp Alerts", font=("Arial Black", 20, "bold"), text_color="#E74C3C").pack(pady=10)
        ctk.CTkLabel(self.content, text="Enter Blood Group for Emergency:", anchor="w").pack(pady=5, fill="x")
        group_entry = ctk.CTkEntry(self.content)
        group_entry.pack(pady=5, fill="x")
        ctk.CTkLabel(self.content, text="Enter City (optional):", anchor="w").pack(pady=5, fill="x")
        city_entry = ctk.CTkEntry(self.content)
        city_entry.pack(pady=5, fill="x")

        def send_alerts():
            group = group_entry.get().upper()
            city = city_entry.get()
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT name, phone, last_donation_date FROM donors WHERE blood_group=%s"
            params = [group]
            if city:
                query += " AND city=%s"
                params.append(city)
            cursor.execute(query, tuple(params))
            donors = cursor.fetchall()
            conn.close()
            eligible_donors = []
            for donor in donors:
                eligible, _ = is_eligible(donor['last_donation_date'])
                if eligible and donor['phone']:
                    eligible_donors.append(donor)
            if not eligible_donors:
                mbox.showinfo("No Eligible Donors", "No eligible donors found for this group/city.")
                return

            def send_whatsapp(phone, name):
                phone = format_uae_phone(phone)
                msg = f"Hi {name},\nUrgent need for {group} blood group in {city or 'your area'}! Please contact BloodVault™ if you can donate."
                try:
                    pywhatkit.sendwhatmsg_instantly(phone, msg, wait_time=10, tab_close=True)
                except Exception as e:
                    print(f"Failed to send to {phone}: {e}")

            for donor in eligible_donors:
                threading.Thread(target=send_whatsapp, args=(donor['phone'], donor['name'])).start()
            mbox.showinfo("WhatsApp Alerts", f"Sent alerts to {len(eligible_donors)} eligible donors.")

        ctk.CTkButton(self.content, text="Send Emergency Alerts", command=send_alerts).pack(pady=10, fill="x")

    def build_reminder_ui(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="Send Reminders to Donors Eligible Soon", font=("Arial Black", 20, "bold"), text_color="#E74C3C").pack(pady=10)
        def send_reminders():
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT name, phone, last_donation_date FROM donors
                WHERE last_donation_date IS NOT NULL
            """)
            donors = cursor.fetchall()
            conn.close()
            soon_eligible = []
            for donor in donors:
                last_date = donor['last_donation_date']
                if hasattr(last_date, "strftime"):
                    last_date_str = last_date.strftime('%Y-%m-%d')
                else:
                    last_date_str = str(last_date)
                eligible, days_left = is_eligible(last_date_str)
                if not eligible and 0 < days_left <= 7 and donor['phone']:
                    soon_eligible.append((donor, days_left))
            if not soon_eligible:
                mbox.showinfo("No Reminders", "No donors will become eligible in the next 7 days.")
                return
            def send_whatsapp_reminder(phone, name, days_left):
                phone = format_uae_phone(phone)
                msg = f"Hi {name},\nYou will be eligible to donate blood in {days_left} days! BloodVault™ thanks you for your support."
                try:
                    pywhatkit.sendwhatmsg_instantly(phone, msg, wait_time=10, tab_close=True)
                except Exception as e:
                    print(f"Failed to send to {phone}: {e}")
            for donor, days_left in soon_eligible:
                threading.Thread(target=send_whatsapp_reminder, args=(donor['phone'], donor['name'], days_left)).start()
            mbox.showinfo("Reminders Sent", f"Sent reminders to {len(soon_eligible)} donors.")

        ctk.CTkButton(self.content, text="Send Upcoming Eligibility Reminders", command=send_reminders).pack(pady=10, fill="x")

    def return_to_main_menu(self):
        self.destroy()
        from main import BloodVaultMainMenu
        app = BloodVaultMainMenu()
        app.mainloop()

def run_manager():
    app = WhatsAppAlertsManager()
    app.mainloop()
