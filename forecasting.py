import customtkinter as ctk
from main import get_db_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression

class ForecastingManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BloodVault™ - AI-Powered Demand Forecasting")
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
            text="📈 AI-Powered Demand Forecasting",
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
        ctk.CTkButton(self.sidebar, text="🔮 Predict Demand", command=self.predict_demand, **btn_opts).pack(pady=(16, 8))
        ctk.CTkButton(self.sidebar, text="📊 View Forecast Graphs", command=self.view_forecast_graphs, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="⬅️ Main Menu", command=self.return_to_main_menu, **btn_opts).pack(pady=(40, 8))

        # --- Content Area ---
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#444B56", corner_radius=18)  # Slightly lighter bg for content
        self.content.pack(side="left", fill="both", expand=True, padx=(0, 30), pady=18)

        # --- Info Panel ---
        self.tips = [
            "Welcome to AI-Powered Demand Forecasting!",
            "🔮 Predict upcoming blood type demands using machine learning.",
            "📊 Visualize trends and plan inventory proactively.",
            "🩸 Trained on historical donation and request data.",
            "❤️ BloodVault™ helps you stay ahead of demand!"
        ]
        self.tip_index = 0
        self.info_panel = ctk.CTkLabel(
            self.content,
            text=self.tips[self.tip_index],
            font=("Arial", 16, "italic"),
            text_color="#F1C40F",  # Warm yellow for info
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

    # --- Predict Demand ---
    def predict_demand(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🔮 Predict Blood Demand", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)

        group_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        group_frame.pack(pady=10, padx=30, fill="x", expand=True)
        ctk.CTkLabel(group_frame, text="Select Blood Group:", anchor="w").pack(pady=2, fill="x")
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        group_var = ctk.StringVar(value="A+")
        group_menu = ctk.CTkOptionMenu(group_frame, variable=group_var, values=blood_groups)
        group_menu.pack(pady=5, fill="x")

        def run_forecast():
            group = group_var.get()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT YEAR(request_time), WEEK(request_time), COUNT(*) 
                FROM requests 
                WHERE blood_group=%s
                GROUP BY YEAR(request_time), WEEK(request_time)
                ORDER BY YEAR(request_time), WEEK(request_time)
            """, (group,))
            data = cursor.fetchall()
            conn.close()
            if len(data) < 2:
                ctk.CTkLabel(self.content, text="Not enough data for prediction.", text_color="#FF4C6D").pack(pady=10)
                return
            X = np.array([i for i in range(len(data))]).reshape(-1, 1)
            y = np.array([row[2] for row in data])
            model = LinearRegression()
            model.fit(X, y)
            next_week = np.array([[len(data)]])
            prediction = max(0, int(model.predict(next_week)[0]))  # no negative predictions
            ctk.CTkLabel(self.content, text=f"Predicted demand for {group} next week: {prediction} units", font=("Arial", 18, "bold"), text_color="#7CFC00").pack(pady=20)  # Softer green

            fig, ax = plt.subplots(figsize=(5,3), dpi=100)
            ax.plot([row[2] for row in data], marker='o', label="Historical", color="#E74C3C")
            ax.plot(len(data), prediction, marker='*', color='#FF6B6B', label="Forecast")
            ax.set_title(f"Weekly Demand for {group}")
            ax.set_xlabel("Week")
            ax.set_ylabel("Requests")
            ax.legend()
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

        ctk.CTkButton(group_frame, text="Predict", command=run_forecast).pack(pady=10, fill="x")

    # --- View Forecast Graphs ---
    def view_forecast_graphs(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="📊 Forecast Graphs", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor()
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        fig, ax = plt.subplots(figsize=(7,4), dpi=100)

        colors = ["#E74C3C", "#FF6B6B", "#C0392B", "#D35400", "#F39C12", "#F1C40F", "#27AE60", "#2ECC71"]  # warm reds to greens

        for i, group in enumerate(blood_groups):
            cursor.execute("""
                SELECT YEAR(request_time), WEEK(request_time), COUNT(*) 
                FROM requests 
                WHERE blood_group=%s
                GROUP BY YEAR(request_time), WEEK(request_time)
                ORDER BY YEAR(request_time), WEEK(request_time)
            """, (group,))
            data = cursor.fetchall()
            if len(data) > 1:
                ax.plot([row[2] for row in data], marker='o', label=group, color=colors[i])
        conn.close()

        ax.set_title("Weekly Demand Trends by Blood Group")
        ax.set_xlabel("Week")
        ax.set_ylabel("Requests")
        ax.legend()
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
    app = ForecastingManager()
    app.mainloop()
