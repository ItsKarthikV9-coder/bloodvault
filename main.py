import customtkinter as ctk
import tkinter.messagebox as mbox
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="karthik@2024",
        database="bloodvault"
    )

class BloodVaultMainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height-50}+0+0")
        self.title("BloodVault™ - Main Menu")
        
        ctk.set_appearance_mode("dark")
        self.configure(bg="#2C2F33")  # softer dark background

        # --- Main Frame with Shadow ---
        self.shadow = ctk.CTkFrame(self, corner_radius=32, fg_color="#444B56")  # softer shadow color
        self.shadow.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)

        self.main_frame = ctk.CTkFrame(self, corner_radius=24, fg_color="#36393F", border_width=2, border_color="#E74C3C")  # muted red border
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.90, relheight=0.90)

        # --- Title ---
        self.label = ctk.CTkLabel(
            self.main_frame,
            text="🩸 BloodVault™",
            font=("Arial Black", 42, "bold"),
            text_color="#E74C3C"  # softer red text
        )
        self.label.pack(pady=(32, 8))

        # --- Glowing Divider ---
        divider = ctk.CTkLabel(self.main_frame, text="", fg_color="#E74C3C", height=3, width=700, corner_radius=2)
        divider.pack(pady=(8, 18))

        # --- Menu Buttons ---
        btn_opts = {
            "width": 350, "height": 48, "corner_radius": 16,
            "font": ("Arial", 18, "bold"),
            "fg_color": "#E74C3C",
            "hover_color": "#FF6B6B",  # lighter hover color
            "text_color": "#FFF"
        }
        menu_items = [
            ("👤 Donor & Recipient Management", self.launch_donor_recipient),
            ("🧪 Blood & Plasma Inventory", self.launch_inventory),
            ("🚑 Request Handling", self.launch_requests),
            ("📈 Demand Forecasting", self.launch_forecast),
            ("📊 Visual Dashboard", self.launch_dashboard),
            ("📍 Geolocation Services", self.launch_geo),
            ("💬 WhatsApp Alerts", self.launch_alerts),
            ("📝 Reports & Export", self.launch_reports),
            ("❌ Exit", self.quit)
        ]
        for text, cmd in menu_items:
            ctk.CTkButton(self.main_frame, text=text, command=cmd, **btn_opts).pack(pady=8)

        # --- Rotating Tips/Info Panel ---
        self.tips = [
            "Welcome to BloodVault™!\nYour all-in-one smart blood bank management system.",
            "💡 Tip: Keep your donor records updated for faster matching.",
            "🩸 BloodVault™ uses AI to forecast demand and save lives.",
            "🔒 Your data is encrypted and secure.",
            "❤️ Thank you for supporting the gift of life!"
        ]
        self.tip_index = 0
        self.info_panel = ctk.CTkLabel(
            self.main_frame,
            text=self.tips[self.tip_index],
            font=("Arial", 16, "italic"),
            text_color="#F1C40F",  # warm yellow text for tips
            fg_color="#444B56",    # dark but softer background for info panel
            corner_radius=12,
            width=600,
            height=50
        )
        self.info_panel.pack(pady=(30, 10))
        self.rotate_tips()

        # --- Copyright ---
        self.copyright = ctk.CTkLabel(
            self.main_frame,
            text="© Karthik Vinod. All rights reserved.",
            font=("Arial", 12),
            text_color="#B03A2E"  # muted red-brown text
        )
        self.copyright.pack(side="bottom", pady=10)

    def launch_donor_recipient(self):
        from donor_recipient import run_manager
        self.destroy()
        run_manager()

    def launch_inventory(self):
        from inventory import run_manager
        self.destroy()
        run_manager()

    def launch_requests(self):
        from requests_manager import run_manager
        self.destroy()
        run_manager()

    def launch_forecast(self):
        from forecasting import run_manager
        self.destroy()
        run_manager()

    def launch_dashboard(self):
        from dashboard import run_manager
        self.destroy()
        run_manager()

    def launch_geo(self):
        from geolocation import run_manager
        self.destroy()
        run_manager()

    def launch_alerts(self):
        from whatsapp_alerts import run_manager
        self.destroy()
        run_manager()

    def launch_reports(self):
        from reports import run_manager
        self.destroy()
        run_manager()

    def rotate_tips(self):
        self.tip_index = (self.tip_index + 1) % len(self.tips)
        self.info_panel.configure(text=self.tips[self.tip_index])
        self.after(4000, self.rotate_tips)


if __name__ == "__main__":
    app = BloodVaultMainMenu()
    app.mainloop()
