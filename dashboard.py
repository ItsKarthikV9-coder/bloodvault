import customtkinter as ctk
from main import get_db_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime

class DashboardManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BloodVault™ - Smart Visual Dashboard")
        self.geometry("1050x700")
        ctk.set_appearance_mode("dark")
        self.configure(bg="#2C2F33")  # softer dark bg

        # --- Shadow and Main Frame ---
        self.shadow = ctk.CTkFrame(self, corner_radius=32, fg_color="#444B56")  # softer shadow
        self.shadow.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)

        self.main_frame = ctk.CTkFrame(self, corner_radius=24, fg_color="#36393F", border_width=2, border_color="#E74C3C")  # muted red border
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.90, relheight=0.90)

        # --- Title ---
        self.label = ctk.CTkLabel(
            self.main_frame,
            text="📊 Smart Visual Dashboard",
            font=("Arial Black", 36, "bold"),
            text_color="#E74C3C"  # softer red text
        )
        self.label.pack(pady=(32, 8))

        # --- Glowing Divider ---
        divider = ctk.CTkLabel(self.main_frame, text="", fg_color="#E74C3C", height=3, width=700, corner_radius=2)
        divider.pack(pady=(8, 18))

        # --- Sidebar Navigation ---
        self.sidebar = ctk.CTkFrame(self.main_frame, fg_color="#444B56", corner_radius=18, width=200)  # softer sidebar bg
        self.sidebar.pack(side="left", fill="y", padx=(30, 18), pady=18)

        btn_opts = {
            "width": 180, "height": 40, "corner_radius": 12,
            "font": ("Arial", 15, "bold"),
            "fg_color": "#E74C3C",
            "hover_color": "#FF6B6B",  # lighter hover color
            "text_color": "#FFF",
            "anchor": "w"
        }
        ctk.CTkButton(self.sidebar, text="🍩 Blood Group Distribution", command=self.show_donut_chart, **btn_opts).pack(pady=(16, 8))
        ctk.CTkButton(self.sidebar, text="📊 Requests vs Availability", command=self.show_bar_graph, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="📈 Donation Trends", command=self.show_line_chart, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="🥧 Upcoming Expiries", command=self.show_pie_chart, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="🌡️ Donor Activity Heatmap", command=self.show_heatmap, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="⬅️ Main Menu", command=self.return_to_main_menu, **btn_opts).pack(pady=(40, 8))

        # --- Content Area ---
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#36393F", corner_radius=18)  # softer content bg
        self.content.pack(side="left", fill="both", expand=True, padx=(0, 30), pady=18)

        # --- Info Panel ---
        self.tips = [
            "Welcome to the Smart Visual Dashboard!",
            "🍩 See blood group distribution in your bank.",
            "📊 Compare requests vs available stock.",
            "📈 Track donation trends over time.",
            "🥧 Monitor upcoming expiries.",
            "🌡️ Visualize donor activity by day/time."
        ]
        self.tip_index = 0
        self.info_panel = ctk.CTkLabel(
            self.content,
            text=self.tips[self.tip_index],
            font=("Arial", 16, "italic"),
            text_color="#F1C40F",  # warm yellow
            fg_color="#444B56",    # info panel bg softer
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
            text_color="#B03A2E"  # muted red-brown
        )
        self.copyright.place(relx=0.5, rely=0.98, anchor="s")

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def rotate_tips(self):
        self.tip_index = (self.tip_index + 1) % len(self.tips)
        self.info_panel.configure(text=self.tips[self.tip_index])
        self.after(4000, self.rotate_tips)

    # --- Donut Chart: Blood Group Distribution ---
    def show_donut_chart(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🍩 Blood Group Distribution", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT blood_group, COUNT(*) FROM donors GROUP BY blood_group
        """)
        data = cursor.fetchall()
        conn.close()
        if not data:
            ctk.CTkLabel(self.content, text="No donor data available.", text_color="#FFF").pack(pady=10)
            return
        labels = [row[0] for row in data]
        sizes = [row[1] for row in data]
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85,
                                          colors=plt.cm.Reds(np.linspace(0.5, 1, len(sizes))))
        centre_circle = plt.Circle((0,0),0.70,fc='#36393F')
        fig.gca().add_artist(centre_circle)
        ax.axis('equal')
        ax.set_title("Blood Group Distribution")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # --- Bar Graph: Requests vs Availability ---
    def show_bar_graph(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="📊 Requests vs Availability", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor()
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        # Requests
        cursor.execute("""
            SELECT blood_group, COUNT(*) FROM requests GROUP BY blood_group
        """)
        req_data = dict(cursor.fetchall())
        # Availability
        cursor.execute("""
            SELECT blood_group, SUM(volume_ml) FROM blood_inventory
            WHERE status='Available' AND expiry_date >= CURDATE()
            GROUP BY blood_group
        """)
        avail_data = dict(cursor.fetchall())
        conn.close()
        reqs = [req_data.get(bg, 0) for bg in blood_groups]
        avails = [avail_data.get(bg, 0) for bg in blood_groups]
        x = np.arange(len(blood_groups))
        width = 0.35
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.bar(x - width/2, reqs, width, label='Requests', color='#E74C3C')
        ax.bar(x + width/2, avails, width, label='Available (ml)', color='#4CAF50')  # softer green
        ax.set_xticks(x)
        ax.set_xticklabels(blood_groups)
        ax.set_ylabel("Count / Volume (ml)")
        ax.set_title("Requests vs Availability")
        ax.legend()
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # --- Line Chart: Donation Trends ---
    def show_line_chart(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="📈 Donation Trends", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(donation_date), COUNT(*) FROM donation_history
            GROUP BY DATE(donation_date)
            ORDER BY DATE(donation_date)
        """)
        data = cursor.fetchall()
        conn.close()
        if not data:
            ctk.CTkLabel(self.content, text="No donation history data.", text_color="#FFF").pack(pady=10)
            return
        dates = [row[0] for row in data]
        counts = [row[1] for row in data]
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.plot(dates, counts, marker='o', color='#E74C3C')
        ax.set_xlabel("Date")
        ax.set_ylabel("Donations")
        ax.set_title("Donation Trends Over Time")
        fig.autofmt_xdate()
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # --- Pie Chart: Upcoming Expiries ---
    def show_pie_chart(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🥧 Upcoming Expiries (Next 30 Days)", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT blood_group, COUNT(*) FROM blood_inventory
            WHERE status='Available' AND expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            GROUP BY blood_group
        """)
        data = cursor.fetchall()
        conn.close()
        if not data:
            ctk.CTkLabel(self.content, text="No upcoming expiries.", text_color="#FFF").pack(pady=10)
            return
        labels = [row[0] for row in data]
        sizes = [row[1] for row in data]
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Oranges(np.linspace(0.5, 1, len(sizes))))
        ax.set_title("Upcoming Expiries by Blood Group")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # --- Heatmap: Donor Activity by Day/Time ---
    def show_heatmap(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🌡️ Donor Activity Heatmap", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor()
        # Get hour and weekday for each donation
        cursor.execute("""
            SELECT DAYOFWEEK(donation_date), HOUR(donation_date), COUNT(*)
            FROM donation_history
            GROUP BY DAYOFWEEK(donation_date), HOUR(donation_date)
        """)
        data = cursor.fetchall()
        conn.close()
        # Prepare heatmap matrix
        heatmap = np.zeros((7, 24))
        for day, hour, count in data:
            heatmap[day-1, hour] = count
        fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
        im = ax.imshow(heatmap, aspect='auto', cmap='inferno')
        ax.set_yticks(np.arange(7))
        ax.set_yticklabels(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
        ax.set_xticks(np.arange(0, 24, 2))
        ax.set_xticklabels([str(h) for h in range(0, 24, 2)])
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Day of Week")
        ax.set_title("Donor Activity Heatmap")
        fig.colorbar(im, ax=ax)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def return_to_main_menu(self):
        self.destroy()
        from main import BloodVaultMainMenu
        app = BloodVaultMainMenu()
        app.mainloop()

def run_manager():
    app = DashboardManager()
    app.mainloop()
