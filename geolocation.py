import customtkinter as ctk
from main import get_db_connection
import geocoder
import folium
import webbrowser
from math import radians, cos, sin, asin, sqrt

class GeolocationManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BloodVault™ - Geolocation Integration")
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
            text="📍 Geolocation Integration",
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
        ctk.CTkButton(self.sidebar, text="📡 Detect My Location", command=self.detect_location, **btn_opts).pack(pady=(16, 8))
        ctk.CTkButton(self.sidebar, text="🗺️ Show Donors on Map", command=self.show_donors_map, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="📍 Sort Donors by Proximity", command=self.sort_donors_by_proximity, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="🚨 Emergency Donor Match", command=self.emergency_donor_match, **btn_opts).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="⬅️ Main Menu", command=self.return_to_main_menu, **btn_opts).pack(pady=(40, 8))

        # --- Content Area ---
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#444B56", corner_radius=18)  # Slightly lighter content background
        self.content.pack(side="left", fill="both", expand=True, padx=(0, 30), pady=18)

        # --- Info Panel ---
        self.tips = [
            "Welcome to Geolocation Integration!",
            "📡 Auto-detect your location via IP.",
            "🗺️ Visualize donors and hospitals on an interactive map.",
            "📍 Sort donors by proximity for emergencies.",
            "❤️ Real-time location-based donor matching."
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

        self.my_location = None  # (lat, lng)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def rotate_tips(self):
        self.tip_index = (self.tip_index + 1) % len(self.tips)
        self.info_panel.configure(text=self.tips[self.tip_index])
        self.after(4000, self.rotate_tips)

    # --- Detect My Location ---
    def detect_location(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="📡 Detect My Location", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        try:
            g = geocoder.ip('me')
            if g.ok:
                lat, lng = g.latlng
                self.my_location = (lat, lng)
                ctk.CTkLabel(self.content, text=f"Latitude: {lat:.4f}\nLongitude: {lng:.4f}", text_color="#7CFC00").pack(pady=10)  # Softer green
            else:
                ctk.CTkLabel(self.content, text="Could not detect location.", text_color="#FF6B6B").pack(pady=10)
        except Exception as e:
            ctk.CTkLabel(self.content, text=f"Error: {e}", text_color="#FF6B6B").pack(pady=10)
            print(f"Error detecting location: {e}")

    # --- Show Donors on Map ---
    def show_donors_map(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🗺️ Show Donors on Map", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, latitude, longitude, blood_group FROM donors WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
        donors = cursor.fetchall()
        conn.close()
        if not donors:
            ctk.CTkLabel(self.content, text="No donor locations available.", text_color="#FFF").pack(pady=10)
            return
        if self.my_location:
            map_center = self.my_location
        else:
            map_center = (donors[0]['latitude'], donors[0]['longitude'])
        m = folium.Map(location=map_center, zoom_start=7)
        for donor in donors:
            folium.Marker(
                location=(donor['latitude'], donor['longitude']),
                popup=f"{donor['name']} ({donor['blood_group']})",
                icon=folium.Icon(color="red", icon="tint", prefix="fa")
            ).add_to(m)
        if self.my_location:
            folium.Marker(
                location=self.my_location,
                popup="You are here",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(m)
        map_file = "donors_map.html"
        m.save(map_file)
        webbrowser.open(map_file)
        ctk.CTkLabel(self.content, text="Map opened in your browser.", text_color="#7CFC00").pack(pady=10)

    # --- Sort Donors by Proximity ---
    def sort_donors_by_proximity(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="📍 Sort Donors by Proximity", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        if not self.my_location:
            ctk.CTkLabel(self.content, text="Detect your location first!", text_color="#FF6B6B").pack(pady=10)
            return
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, phone, city, latitude, longitude, blood_group FROM donors WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
        donors = cursor.fetchall()
        conn.close()
        if not donors:
            ctk.CTkLabel(self.content, text="No donor locations available.", text_color="#FFF").pack(pady=10)
            return
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            return R * c
        lat1, lon1 = self.my_location
        for donor in donors:
            donor['distance'] = haversine(lat1, lon1, donor['latitude'], donor['longitude'])
        donors.sort(key=lambda d: d['distance'])
        result_box = ctk.CTkTextbox(self.content, width=500, height=350)
        result_box.pack(pady=10)
        for donor in donors[:20]:
            result_box.insert("end", f"{donor['name']} ({donor['blood_group']}) - {donor['city']}, {donor['distance']:.2f} km\nPhone: {donor['phone']}\n\n")

    # --- Emergency Donor Match ---
    def emergency_donor_match(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🚨 Emergency Donor Match", font=("Arial Black", 22, "bold"), text_color="#E74C3C").pack(pady=18)
        if not self.my_location:
            ctk.CTkLabel(self.content, text="Detect your location first!", text_color="#FF6B6B").pack(pady=10)
            return
        ctk.CTkLabel(self.content, text="Enter Blood Group Needed:", anchor="w").pack(pady=5, fill="x")
        group_entry = ctk.CTkEntry(self.content)
        group_entry.pack(pady=5, fill="x")
        def find_match():
            group = group_entry.get().upper()
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name, phone, city, latitude, longitude FROM donors WHERE blood_group=%s AND latitude IS NOT NULL AND longitude IS NOT NULL", (group,))
            donors = cursor.fetchall()
            conn.close()
            if not donors:
                ctk.CTkLabel(self.content, text="No matching donors found.", text_color="#FFF").pack(pady=10)
                return
            lat1, lon1 = self.my_location
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371
                dlat = radians(lat2 - lat1)
                dlon = radians(lon2 - lon1)
                a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                return R * c
            for donor in donors:
                donor['distance'] = haversine(lat1, lon1, donor['latitude'], donor['longitude'])
            donors.sort(key=lambda d: d['distance'])
            result_box = ctk.CTkTextbox(self.content, width=500, height=350)
            result_box.pack(pady=10)
            for donor in donors[:10]:
                result_box.insert("end", f"{donor['name']} - {donor['city']}, {donor['distance']:.2f} km\nPhone: {donor['phone']}\n\n")
        ctk.CTkButton(self.content, text="Find Nearest Donors", command=find_match).pack(pady=10, fill="x")

    def return_to_main_menu(self):
        self.destroy()
        from main import BloodVaultMainMenu
        app = BloodVaultMainMenu()
        app.mainloop()

def run_manager():
    app = GeolocationManager()
    app.mainloop()
