import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter.messagebox as mbox
import pandas as pd
from main import get_db_connection

class ReportsManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BloodVault™ - Reports & Export Tools")
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
            text="📄 Reports & Export Tools",
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
        ctk.CTkButton(self.sidebar, text="🩸 Donation Reports", command=self.show_donation_reports, **btn_opts).pack(pady=(16, 8))
        ctk.CTkButton(self.sidebar, text="🏥 Stock Usage Reports", command=self.show_stock_reports, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="📦 Inventory History", command=self.show_inventory_history, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="⬅️ Main Menu", command=self.return_to_main_menu, **btn_opts).pack(pady=(40, 8))

        # --- Content Area ---
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#444B56", corner_radius=18)  # Slightly lighter content background
        self.content.pack(side="left", fill="both", expand=True, padx=(0, 30), pady=18)

        # --- Info Panel ---
        self.tips = [
            "Welcome to Reports & Export Tools!",
            "🩸 Generate donation and stock usage reports.",
            "📦 Export data as CSV for analysis or printing.",
            "❤️ BloodVault™ keeps your records organized!"
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
            if widget != self.info_panel:
                widget.destroy()

    def rotate_tips(self):
        self.tip_index = (self.tip_index + 1) % len(self.tips)
        self.info_panel.configure(text=self.tips[self.tip_index])
        self.after(4000, self.rotate_tips)

    def show_donation_reports(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🩸 Donation Reports", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        df = pd.read_sql("""
            SELECT d.name, d.blood_group, h.donation_date, h.volume_ml
            FROM donation_history h
            JOIN donors d ON h.donor_id = d.donor_id
            ORDER BY h.donation_date DESC
        """, conn)
        conn.close()
        if df.empty:
            ctk.CTkLabel(self.content, text="No donation history found.", text_color="#FFF").pack(pady=10)
            return
        text = df.to_string(index=False)
        box = ctk.CTkTextbox(self.content, width=800, height=350)
        box.pack(pady=10)
        box.insert("end", text)
        ctk.CTkButton(self.content, text="Export as CSV", command=lambda: self.export_csv(df, "donation_reports")).pack(pady=10, fill="x")

    def show_stock_reports(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🏥 Stock Usage Reports", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        df = pd.read_sql("""
            SELECT blood_group, type, SUM(volume_ml) as total_used
            FROM blood_inventory
            WHERE status='Used'
            GROUP BY blood_group, type
            ORDER BY blood_group
        """, conn)
        conn.close()
        if df.empty:
            ctk.CTkLabel(self.content, text="No stock usage data found.", text_color="#FFF").pack(pady=10)
            return
        text = df.to_string(index=False)
        box = ctk.CTkTextbox(self.content, width=800, height=350)
        box.pack(pady=10)
        box.insert("end", text)
        ctk.CTkButton(self.content, text="Export as CSV", command=lambda: self.export_csv(df, "stock_usage_reports")).pack(pady=10, fill="x")

    def show_inventory_history(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="📦 Inventory History", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        df = pd.read_sql("""
            SELECT id, blood_group, type, volume_ml, status, expiry_date
            FROM blood_inventory
            ORDER BY expiry_date ASC
        """, conn)
        conn.close()
        if df.empty:
            ctk.CTkLabel(self.content, text="No inventory data found.", text_color="#FFF").pack(pady=10)
            return
        text = df.to_string(index=False)
        box = ctk.CTkTextbox(self.content, width=800, height=350)
        box.pack(pady=10)
        box.insert("end", text)
        ctk.CTkButton(self.content, text="Export as CSV", command=lambda: self.export_csv(df, "inventory_history")).pack(pady=10, fill="x")

    def export_csv(self, df, default_name):
        file = fd.asksaveasfilename(defaultextension=".csv", initialfile=f"{default_name}.csv",
                                    filetypes=[("CSV files", "*.csv")])
        if file:
            df.to_csv(file, index=False)
            mbox.showinfo("Exported", f"Data exported to {file}")

    def return_to_main_menu(self):
        self.destroy()
        from main import BloodVaultMainMenu
        app = BloodVaultMainMenu()
        app.mainloop()

def run_manager():
    app = ReportsManager()
    app.mainloop()
