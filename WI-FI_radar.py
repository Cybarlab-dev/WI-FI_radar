import tkinter as tk
import customtkinter as ctk
import math
import threading
import subprocess
import shutil
import queue
import hashlib
import time


# ==========================================
# CYBERLAB - WIFI RADAR V7
# ==========================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

SCAN_INTERVAL = 12000
PULSE_INTERVAL = 450
TRAFFIC_INTERVAL = 1000

BG = "#090D0B"
PANEL = "#121B16"
CARD = "#0D1511"
GREEN = "#39FF14"
ACCENT = "#00FFCC"
MUTED = "#9BAAA0"
BORDER = "#245B36"
WHITE = "#FFFFFF"


TRANSLATIONS = {
    "en": {
        "title": "CYBERLAB - Wi-Fi Radar",
        "subtitle": "NETWORK INSIGHTS & MONITORING",
        "scan": "Rescan Wi-Fi",
        "stop": "Stop Scan",
        "language": "العربية",
        "networks": "DETECTED NETWORKS",
        "radar": "WI-FI RADAR",
        "traffic": "NETWORK TRAFFIC",
        "topology": "NETWORK TOPOLOGY",
        "connection": "CONNECTION INFORMATION",
        "local_devices": "LOCAL NETWORK DEVICES",
        "device_count": "Known devices",
        "status_ready": "Ready to scan",
        "status_scanning": "Scanning Wi-Fi...",
        "status_done": "Scan completed",
        "status_stopped": "Automatic scanning stopped",
        "no_networks": "No networks found.",
        "no_devices": "No known local devices.",
        "no_nmcli": "nmcli is not installed.",
        "ssid": "Network",
        "mac": "MAC Address",
        "signal": "Signal",
        "security": "Security",
        "channel": "Channel",
        "frequency": "Frequency",
        "ip": "Local IP",
        "gateway": "Gateway",
        "dns": "DNS",
        "device_mac": "Device MAC",
        "unknown": "Unavailable",
        "hidden": "Hidden Network",
        "open": "Open",
        "selected": "SELECTED NETWORK",
        "not_selected": "No network selected",
        "click_hint": "Select a point on the radar",
        "self_device": "MY DEVICE",
        "neighbor": "KNOWN DEVICE",
        "device_ip": "Device IP",
        "device_state": "Neighbor state",
        "state_reachable": "Recent response",
        "state_stale": "Cached record",
        "state_delay": "Checking",
        "state_probe": "Verifying",
        "state_permanent": "Permanent",
        "state_noarp": "No ARP",
        "state_unknown": "Unknown",
        "traffic_rx": "Download",
        "traffic_tx": "Upload",
        "traffic_wait": "Collecting traffic data...",
        "traffic_note": "Total traffic on this computer",
        "scan_error": "Scan error: ",
        "selected_device": "SELECTED DEVICE",
        "click_device": "Select a device from the list",
        "router": "LOCAL NETWORK",
        "devices": "DEVICES",
        "no_connection": "Not connected to Wi-Fi",
        "topology_note": "Schematic view of known devices"
    },

    "ar": {
        "title": "سايبر لاب - رادار الواي فاي",
        "subtitle": "مراقبة الشبكة وحركة البيانات",
        "scan": "إعادة فحص Wi-Fi",
        "stop": "إيقاف الفحص",
        "language": "English",
        "networks": "الشبكات المكتشفة",
        "radar": "رادار الواي فاي",
        "traffic": "حركة بيانات الشبكة",
        "topology": "ترابط الشبكة",
        "connection": "معلومات الاتصال",
        "local_devices": "أجهزة الشبكة المحلية",
        "device_count": "الأجهزة المعروفة",
        "status_ready": "جاهز للفحص",
        "status_scanning": "جاري فحص Wi-Fi...",
        "status_done": "اكتمل الفحص",
        "status_stopped": "تم إيقاف الفحص الدوري",
        "no_networks": "لم يتم العثور على شبكات.",
        "no_devices": "لا توجد أجهزة محلية معروفة.",
        "no_nmcli": "أداة nmcli غير مثبتة.",
        "ssid": "اسم الشبكة",
        "mac": "عنوان MAC",
        "signal": "قوة الإشارة",
        "security": "الحماية",
        "channel": "القناة",
        "frequency": "التردد",
        "ip": "عنوان IP المحلي",
        "gateway": "البوابة",
        "dns": "DNS",
        "device_mac": "MAC الجهاز",
        "unknown": "غير متوفر",
        "hidden": "شبكة مخفية",
        "open": "مفتوحة",
        "selected": "الشبكة المحددة",
        "not_selected": "لم يتم تحديد شبكة",
        "click_hint": "اختر نقطة من الرادار",
        "self_device": "جهازي",
        "neighbor": "جهاز معروف",
        "device_ip": "عنوان IP",
        "device_state": "حالة سجل الشبكة",
        "state_reachable": "استجابة حديثة",
        "state_stale": "سجل مخزن",
        "state_delay": "قيد التحقق",
        "state_probe": "جارٍ التحقق",
        "state_permanent": "ثابت",
        "state_noarp": "بدون ARP",
        "state_unknown": "غير معروف",
        "traffic_rx": "تنزيل",
        "traffic_tx": "رفع",
        "traffic_wait": "جاري جمع بيانات الحركة...",
        "traffic_note": "إجمالي حركة البيانات على جهازك",
        "scan_error": "خطأ في الفحص: ",
        "selected_device": "الجهاز المحدد",
        "click_device": "اختر جهازاً من القائمة",
        "router": "الشبكة المحلية",
        "devices": "الأجهزة",
        "no_connection": "لا يوجد اتصال Wi-Fi",
        "topology_note": "رسم توضيحي للأجهزة المعروفة"
    }
}


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def split_nmcli_line(line):
    fields = []
    current = []
    escaped = False

    for char in line:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == ":":
            fields.append("".join(current))
            current = []
        else:
            current.append(char)

    if escaped:
        current.append("\\")

    fields.append("".join(current))
    return fields


def run_command(command, timeout=20):
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False
    )


def stable_hash(value):
    result = hashlib.sha256(
        value.encode("utf-8", errors="replace")
    ).hexdigest()

    return int(result[:8], 16)


def read_network_counters():
    rx_total = 0
    tx_total = 0

    try:
        with open("/proc/net/dev", "r") as file:
            lines = file.readlines()[2:]

        for line in lines:
            if ":" not in line:
                continue

            interface, data = line.split(":", 1)

            if interface.strip() == "lo":
                continue

            values = data.split()

            if len(values) >= 9:
                rx_total += int(values[0])
                tx_total += int(values[8])

    except (OSError, ValueError):
        pass

    return rx_total, tx_total


def format_speed(value):
    if value < 1024:
        return f"{value:.0f} B/s"

    if value < 1024 * 1024:
        return f"{value / 1024:.1f} KB/s"

    return f"{value / (1024 * 1024):.2f} MB/s"


# ==========================================
# MAIN APPLICATION
# ==========================================

class WifiRadarApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.current_lang = "en"

        self.title(self.t("title"))
        self.geometry("1450x900")
        self.minsize(1050, 720)
        self.configure(fg_color=BG)

        self.auto_scan_enabled = False
        self.scan_in_progress = False
        self.scan_generation = 0
        self.next_scan_job = None
        self.closed = False

        self.angle = 0
        self.pulse_phase = 0

        self.detected_networks = []
        self.device_info = {}
        self.local_devices = []

        self.selected_network = None
        self.selected_local_device = None

        self.result_queue = queue.Queue()

        self.traffic_history_rx = [0] * 40
        self.traffic_history_tx = [0] * 40

        self.last_rx, self.last_tx = read_network_counters()
        self.last_traffic_time = time.time()

        self.center_x = 0
        self.center_y = 0
        self.radius = 0

        self.create_layout()

        self.status_label.configure(
            text=self.t("status_ready")
        )

        self.after(100, self.process_queue)
        self.after(30, self.animate_radar)
        self.after(PULSE_INTERVAL, self.animate_pulse)
        self.after(TRAFFIC_INTERVAL, self.update_traffic)
        self.after(900, self.start_scan)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ======================================
    # TRANSLATIONS
    # ======================================

    def t(self, key):
        return TRANSLATIONS[self.current_lang][key]

    def toggle_language(self):
        self.current_lang = (
            "ar" if self.current_lang == "en" else "en"
        )

        self.update_language()

    def update_language(self):
        self.title(self.t("title"))

        self.lang_btn.configure(text=self.t("language"))
        self.start_btn.configure(text=self.t("scan"))
        self.stop_btn.configure(text=self.t("stop"))

        self.networks_title.configure(text=self.t("networks"))
        self.radar_title.configure(text=self.t("radar"))
        self.traffic_title.configure(text=self.t("traffic"))
        self.topology_title.configure(text=self.t("topology"))
        self.connection_title.configure(text=self.t("connection"))
        self.local_title.configure(text=self.t("local_devices"))

        self.traffic_note.configure(text=self.t("traffic_note"))
        self.topology_note.configure(text=self.t("topology_note"))

        self.render_networks()
        self.render_local_devices()
        self.render_information()
        self.draw_topology()
        self.draw_traffic_graph()

    # ======================================
    # MAIN LAYOUT
    # ======================================

    def create_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=245)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.create_sidebar()
        self.create_dashboard()
        self.create_connection_panel()

    # ======================================
    # SIDEBAR
    # ======================================

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=245,
            corner_radius=12,
            fg_color=PANEL,
            border_color=BORDER,
            border_width=1
        )

        self.sidebar.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=12,
            pady=12,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="⚡ CYBERLAB",
            text_color=GREEN,
            font=ctk.CTkFont(size=23, weight="bold")
        ).pack(pady=(22, 3))

        ctk.CTkLabel(
            self.sidebar,
            text="WI-FI RADAR SYSTEM",
            text_color=MUTED,
            font=ctk.CTkFont(size=10)
        ).pack(pady=(0, 20))

        self.lang_btn = ctk.CTkButton(
            self.sidebar,
            text=self.t("language"),
            command=self.toggle_language,
            fg_color="#1B2920",
            hover_color="#294633",
            text_color=ACCENT
        )
        self.lang_btn.pack(fill="x", padx=15, pady=4)

        self.start_btn = ctk.CTkButton(
            self.sidebar,
            text=self.t("scan"),
            command=self.start_scan,
            fg_color=ACCENT,
            hover_color="#00BFA0",
            text_color="#000000",
            font=ctk.CTkFont(weight="bold")
        )
        self.start_btn.pack(fill="x", padx=15, pady=5)

        self.stop_btn = ctk.CTkButton(
            self.sidebar,
            text=self.t("stop"),
            command=self.stop_scan,
            fg_color="#B83250",
            hover_color="#8D2038",
            text_color=WHITE,
            state="disabled"
        )
        self.stop_btn.pack(fill="x", padx=15, pady=4)

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="",
            text_color=GREEN,
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=12)

        self.networks_title = ctk.CTkLabel(
            self.sidebar,
            text=self.t("networks"),
            text_color=ACCENT,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.networks_title.pack(
            anchor="w",
            padx=15,
            pady=(8, 5)
        )

        self.results_box = ctk.CTkTextbox(
            self.sidebar,
            height=175,
            fg_color=CARD,
            text_color=ACCENT,
            font=ctk.CTkFont(size=10, family="Consolas")
        )
        self.results_box.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.local_title = ctk.CTkLabel(
            self.sidebar,
            text=self.t("local_devices"),
            text_color=ACCENT,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.local_title.pack(
            anchor="w",
            padx=15,
            pady=(12, 3)
        )

        self.device_count_label = ctk.CTkLabel(
            self.sidebar,
            text=f"{self.t('device_count')}: 0",
            text_color=MUTED,
            font=ctk.CTkFont(size=10)
        )
        self.device_count_label.pack(
            anchor="w",
            padx=15,
            pady=4
        )

        self.devices_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color=CARD,
            corner_radius=8
        )
        self.devices_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(3, 10)
        )

    # ======================================
    # DASHBOARD
    # ======================================

    def create_dashboard(self):

        self.dashboard = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0
        )

        self.dashboard.grid(
            row=0,
            column=1,
            padx=(0, 12),
            pady=(12, 5),
            sticky="nsew"
        )

        for column in range(3):
            self.dashboard.grid_columnconfigure(
                column,
                weight=1
            )

        self.dashboard.grid_rowconfigure(0, weight=1)

        self.create_traffic_panel()
        self.create_radar_panel()
        self.create_topology_panel()

    # ======================================
    # TRAFFIC PANEL
    # ======================================

    def create_traffic_panel(self):

        self.traffic_frame = ctk.CTkFrame(
            self.dashboard,
            fg_color=PANEL,
            border_color=BORDER,
            border_width=1,
            corner_radius=12
        )

        self.traffic_frame.grid(
            row=0,
            column=0,
            padx=(0, 5),
            sticky="nsew"
        )

        self.traffic_title = ctk.CTkLabel(
            self.traffic_frame,
            text=self.t("traffic"),
            text_color=GREEN,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.traffic_title.pack(pady=10)

        self.traffic_canvas = tk.Canvas(
            self.traffic_frame,
            bg=CARD,
            highlightthickness=0,
            height=260
        )
        self.traffic_canvas.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        self.traffic_info = ctk.CTkLabel(
            self.traffic_frame,
            text=self.t("traffic_wait"),
            text_color=MUTED,
            font=ctk.CTkFont(size=10)
        )
        self.traffic_info.pack(pady=(0, 3))

        self.traffic_note = ctk.CTkLabel(
            self.traffic_frame,
            text=self.t("traffic_note"),
            text_color=MUTED,
            font=ctk.CTkFont(size=9)
        )
        self.traffic_note.pack(pady=(0, 10))

    # ======================================
    # RADAR PANEL
    # ======================================

    def create_radar_panel(self):

        self.radar_frame = ctk.CTkFrame(
            self.dashboard,
            fg_color=PANEL,
            border_color=BORDER,
            border_width=1,
            corner_radius=12
        )

        self.radar_frame.grid(
            row=0,
            column=1,
            padx=5,
            sticky="nsew"
        )

        self.radar_title = ctk.CTkLabel(
            self.radar_frame,
            text=self.t("radar"),
            text_color=GREEN,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.radar_title.pack(pady=10)

        self.canvas = tk.Canvas(
            self.radar_frame,
            bg=CARD,
            highlightthickness=0
        )
        self.canvas.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 8)
        )

        self.canvas.bind(
            "<Configure>",
            self.draw_radar_grid
        )

        self.canvas.bind(
            "<Button-1>",
            self.select_radar_point
        )

    # ======================================
    # TOPOLOGY PANEL
    # ======================================

    def create_topology_panel(self):

        self.topology_frame = ctk.CTkFrame(
            self.dashboard,
            fg_color=PANEL,
            border_color=BORDER,
            border_width=1,
            corner_radius=12
        )

        self.topology_frame.grid(
            row=0,
            column=2,
            padx=(5, 0),
            sticky="nsew"
        )

        self.topology_title = ctk.CTkLabel(
            self.topology_frame,
            text=self.t("topology"),
            text_color=GREEN,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.topology_title.pack(pady=10)

        self.topology_canvas = tk.Canvas(
            self.topology_frame,
            bg=CARD,
            highlightthickness=0
        )
        self.topology_canvas.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        self.topology_note = ctk.CTkLabel(
            self.topology_frame,
            text=self.t("topology_note"),
            text_color=MUTED,
            font=ctk.CTkFont(size=9)
        )
        self.topology_note.pack(pady=(0, 8))

        self.topology_canvas.bind(
            "<Configure>",
            lambda event: self.draw_topology()
        )

    # ======================================
    # CONNECTION PANEL
    # ======================================

    def create_connection_panel(self):

        self.connection_frame = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            border_color=BORDER,
            border_width=1,
            corner_radius=12
        )

        self.connection_frame.grid(
            row=1,
            column=1,
            padx=(0, 12),
            pady=(5, 12),
            sticky="nsew"
        )

        self.connection_title = ctk.CTkLabel(
            self.connection_frame,
            text=self.t("connection"),
            text_color=GREEN,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.connection_title.pack(pady=(8, 3))

        self.device_box = ctk.CTkTextbox(
            self.connection_frame,
            height=155,
            fg_color=CARD,
            text_color=WHITE,
            font=ctk.CTkFont(size=11, family="Consolas")
        )
        self.device_box.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(3, 10)
        )

        self.render_information()

    # ======================================
    # RADAR GRID
    # ======================================

    def draw_radar_grid(self, event=None):

        self.canvas.delete("grid")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        self.center_x = width // 2
        self.center_y = height // 2

        self.radius = max(
            20,
            min(self.center_x, self.center_y) - 25
        )

        for number in range(1, 5):

            radius = self.radius * number / 4

            self.canvas.create_oval(
                self.center_x - radius,
                self.center_y - radius,
                self.center_x + radius,
                self.center_y + radius,
                outline=BORDER,
                tags="grid"
            )

        self.canvas.create_line(
            self.center_x - self.radius,
            self.center_y,
            self.center_x + self.radius,
            self.center_y,
            fill=BORDER,
            tags="grid"
        )

        self.canvas.create_line(
            self.center_x,
            self.center_y - self.radius,
            self.center_x,
            self.center_y + self.radius,
            fill=BORDER,
            tags="grid"
        )

        self.assign_radar_positions()
        self.draw_targets()

    def assign_radar_positions(self):

        if self.radius <= 20:
            return

        for net in self.detected_networks:

            hashed = stable_hash(net["bssid"].lower())
            angle = math.radians(hashed % 360)

            signal = max(0, min(100, net["signal"]))

            distance = self.radius * (1 - signal / 100)
            distance = max(
                22,
                min(distance, self.radius - 12)
            )

            x = self.center_x + distance * math.cos(angle)
            y = self.center_y + distance * math.sin(angle)

            net["coords"] = (x, y)

    def get_signal_color(self, signal):

        if signal >= 70:
            return GREEN

        if signal >= 40:
            return "#FFCC00"

        return "#FF4455"

    def draw_targets(self):

        self.canvas.delete("targets")

        if self.radius <= 20:
            return

        pulse = 3 + self.pulse_phase

        for net in self.detected_networks:

            if "coords" not in net:
                continue

            x, y = net["coords"]
            color = self.get_signal_color(net["signal"])

            selected = (
                self.selected_network is not None
                and self.selected_network["bssid"] == net["bssid"]
            )

            self.canvas.create_oval(
                x - 8 - pulse,
                y - 8 - pulse,
                x + 8 + pulse,
                y + 8 + pulse,
                outline=color,
                tags="targets"
            )

            if selected:
                self.canvas.create_oval(
                    x - 14,
                    y - 14,
                    x + 14,
                    y + 14,
                    outline=WHITE,
                    width=2,
                    tags="targets"
                )

            self.canvas.create_oval(
                x - 6,
                y - 6,
                x + 6,
                y + 6,
                fill=color,
                outline=WHITE,
                tags="targets"
            )

            name = net["ssid"]

            if name == "<Hidden Network>":
                name = self.t("hidden")

            if len(name) > 12:
                name = name[:10] + ".."

            self.canvas.create_text(
                x + 10,
                y - 10,
                text=name,
                fill=WHITE,
                anchor="w",
                font=("Consolas", 8),
                tags="targets"
            )

    def select_radar_point(self, event):

        nearest = None
        nearest_distance = float("inf")

        for net in self.detected_networks:

            if "coords" not in net:
                continue

            x, y = net["coords"]

            distance = math.sqrt(
                (event.x - x) ** 2
                + (event.y - y) ** 2
            )

            if distance < nearest_distance:
                nearest_distance = distance
                nearest = net

        if nearest is not None and nearest_distance <= 25:
            self.selected_network = nearest
            self.render_networks()
            self.render_information()
            self.draw_targets()

    # ======================================
    # RADAR ANIMATION
    # ======================================

    def animate_radar(self):

        if self.closed:
            return

        self.canvas.delete("sweep")

        if self.radius > 20:

            angle = math.radians(self.angle)

            end_x = (
                self.center_x
                + self.radius * math.cos(angle)
            )

            end_y = (
                self.center_y
                + self.radius * math.sin(angle)
            )

            self.canvas.create_line(
                self.center_x,
                self.center_y,
                end_x,
                end_y,
                fill=ACCENT,
                width=2,
                tags="sweep"
            )

        self.angle = (self.angle + 3) % 360

        self.after(30, self.animate_radar)

    def animate_pulse(self):

        if self.closed:
            return

        self.pulse_phase = (self.pulse_phase + 1) % 6

        self.draw_targets()

        self.after(
            PULSE_INTERVAL,
            self.animate_pulse
        )

    # ======================================
    # TRAFFIC MONITOR
    # ======================================

    def update_traffic(self):

        if self.closed:
            return

        current_rx, current_tx = read_network_counters()

        now = time.time()
        elapsed = max(
            0.1,
            now - self.last_traffic_time
        )

        rx_speed = max(
            0,
            (current_rx - self.last_rx) / elapsed
        )

        tx_speed = max(
            0,
            (current_tx - self.last_tx) / elapsed
        )

        self.last_rx = current_rx
        self.last_tx = current_tx
        self.last_traffic_time = now

        self.traffic_history_rx.append(rx_speed)
        self.traffic_history_tx.append(tx_speed)

        self.traffic_history_rx = self.traffic_history_rx[-40:]
        self.traffic_history_tx = self.traffic_history_tx[-40:]

        self.traffic_info.configure(
            text=(
                f"{self.t('traffic_rx')}: {format_speed(rx_speed)}"
                f"     |     "
                f"{self.t('traffic_tx')}: {format_speed(tx_speed)}"
            )
        )

        self.draw_traffic_graph()

        self.after(
            TRAFFIC_INTERVAL,
            self.update_traffic
        )

    def draw_traffic_graph(self):

        if not hasattr(self, "traffic_canvas"):
            return

        canvas = self.traffic_canvas
        canvas.delete("all")

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 30 or height < 30:
            return

        padding = 25
        graph_width = width - padding * 2
        graph_height = height - padding * 2

        for index in range(5):

            y = padding + graph_height * index / 4

            canvas.create_line(
                padding,
                y,
                width - padding,
                y,
                fill=BORDER
            )

        maximum = max(
            max(self.traffic_history_rx),
            max(self.traffic_history_tx),
            1024
        )

        def draw_line(values, color):

            points = []

            for index, value in enumerate(values):

                x = padding + (
                    index / max(1, len(values) - 1)
                ) * graph_width

                y = (
                    height - padding
                    - (value / maximum) * graph_height
                )

                points.extend([x, y])

            if len(points) >= 4:
                canvas.create_line(
                    *points,
                    fill=color,
                    width=2,
                    smooth=True
                )

        draw_line(self.traffic_history_rx, GREEN)
        draw_line(self.traffic_history_tx, ACCENT)

        canvas.create_text(
            padding,
            10,
            text=self.t("traffic_rx"),
            fill=GREEN,
            anchor="w",
            font=("Consolas", 8)
        )

        canvas.create_text(
            padding + 85,
            10,
            text=self.t("traffic_tx"),
            fill=ACCENT,
            anchor="w",
            font=("Consolas", 8)
        )

    # ======================================
    # NETWORK TOPOLOGY
    # ======================================

    def draw_topology(self):

        if not hasattr(self, "topology_canvas"):
            return

        canvas = self.topology_canvas
        canvas.delete("all")

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 50 or height < 50:
            return

        center_x = width / 2
        center_y = height / 2

        canvas.create_oval(
            center_x - 27,
            center_y - 27,
            center_x + 27,
            center_y + 27,
            fill="#17452C",
            outline=ACCENT,
            width=2
        )

        canvas.create_text(
            center_x,
            center_y,
            text="LOCAL",
            fill=WHITE,
            font=("Consolas", 8, "bold")
        )

        devices = self.local_devices[:12]

        if not devices:

            canvas.create_text(
                center_x,
                center_y + 65,
                text=self.t("no_devices"),
                fill=MUTED,
                font=("Consolas", 9)
            )

            return

        count = len(devices)

        for index, device in enumerate(devices):

            angle = (
                (2 * math.pi * index / count)
                - math.pi / 2
            )

            distance_x = width * 0.36
            distance_y = height * 0.34

            x = center_x + math.cos(angle) * distance_x
            y = center_y + math.sin(angle) * distance_y

            color = GREEN if device["is_self"] else ACCENT

            canvas.create_line(
                center_x,
                center_y,
                x,
                y,
                fill="#477A52",
                width=1
            )

            canvas.create_oval(
                x - 13,
                y - 13,
                x + 13,
                y + 13,
                fill="#173326",
                outline=color,
                width=2
            )

            canvas.create_text(
                x,
                y,
                text="PC" if device["is_self"] else "●",
                fill=WHITE,
                font=("Consolas", 8)
            )

            canvas.create_text(
                x,
                y + 22,
                text=device["ip"],
                fill=WHITE,
                font=("Consolas", 7)
            )

        if len(self.local_devices) > 12:

            canvas.create_text(
                center_x,
                height - 12,
                text=(
                    f"+ {len(self.local_devices) - 12} "
                    f"{self.t('devices')}"
                ),
                fill=MUTED,
                font=("Consolas", 8)
            )

    # ======================================
    # DEVICE STATUS
    # ======================================

    def get_device_status(self, state):

        status_map = {
            "REACHABLE": ("state_reachable", GREEN),
            "STALE": ("state_stale", "#FFCC00"),
            "DELAY": ("state_delay", "#00CCFF"),
            "PROBE": ("state_probe", ACCENT),
            "PERMANENT": ("state_permanent", "#AAAAAA"),
            "NOARP": ("state_noarp", "#AAAAAA")
        }

        key, color = status_map.get(
            state.upper(),
            ("state_unknown", MUTED)
        )

        return self.t(key), color

    # ======================================
    # LOCAL DEVICES
    # ======================================

    def get_local_devices(self, device_info):

        devices = []

        if not shutil.which("ip"):
            return devices

        try:

            result = run_command(
                ["ip", "-4", "neigh", "show"],
                timeout=10
            )

            if result.returncode == 0:

                for line in result.stdout.splitlines():

                    parts = line.split()

                    if len(parts) < 2:
                        continue

                    device_ip = parts[0]

                    if "lladdr" not in parts:
                        continue

                    mac_index = parts.index("lladdr") + 1

                    if mac_index >= len(parts):
                        continue

                    mac = parts[mac_index].lower()
                    state = parts[-1].upper()

                    if state in ("FAILED", "INCOMPLETE"):
                        continue

                    devices.append({
                        "ip": device_ip,
                        "mac": mac,
                        "state": state,
                        "is_self": False
                    })

            own_ip = device_info.get(
                "ip", ""
            ).split("/")[0]

            own_mac = device_info.get(
                "device_mac", ""
            )

            if own_ip and own_mac:

                devices.insert(0, {
                    "ip": own_ip,
                    "mac": own_mac.lower(),
                    "state": "THIS DEVICE",
                    "is_self": True
                })

            unique = []
            seen = set()

            for device in devices:

                if device["mac"] in seen:
                    continue

                seen.add(device["mac"])
                unique.append(device)

            return unique

        except Exception:
            return devices

    def render_local_devices(self):

        for widget in self.devices_frame.winfo_children():
            widget.destroy()

        self.device_count_label.configure(
            text=(
                f"{self.t('device_count')}: "
                f"{len(self.local_devices)}"
            )
        )

        if not self.local_devices:

            ctk.CTkLabel(
                self.devices_frame,
                text=self.t("no_devices"),
                text_color=MUTED
            ).pack(pady=10)

            self.draw_topology()
            return

        for device in self.local_devices:

            if device["is_self"]:
                icon = "💻"
                title = self.t("self_device")
                state_text = title
                state_color = GREEN

            else:
                icon = "📡"
                title = self.t("neighbor")

                state_text, state_color = (
                    self.get_device_status(device["state"])
                )

            selected = (
                self.selected_local_device is not None
                and self.selected_local_device["mac"] == device["mac"]
            )

            button = ctk.CTkButton(
                self.devices_frame,
                text=(
                    f"{icon}  {title}\n"
                    f"IP: {device['ip']}\n"
                    f"MAC: {device['mac']}\n"
                    f"● {state_text}"
                ),
                command=lambda item=device: (
                    self.select_local_device(item)
                ),
                fg_color="#17402A" if selected else "#18251C",
                hover_color="#245B36",
                text_color=WHITE,
                border_color=(
                    ACCENT if selected else state_color
                ),
                border_width=1,
                anchor="w",
                height=82,
                corner_radius=8,
                font=ctk.CTkFont(
                    size=10,
                    family="Consolas"
                )
            )

            button.pack(
                fill="x",
                padx=3,
                pady=4
            )

        self.draw_topology()

    def select_local_device(self, device):

        self.selected_local_device = device

        self.render_local_devices()
        self.render_information()

    # ======================================
    # DEVICE INFORMATION
    # ======================================

    def render_information(self):

        self.device_box.configure(state="normal")
        self.device_box.delete("1.0", tk.END)

        info = self.device_info

        labels = [
            ("ip", "ip"),
            ("gateway", "gateway"),
            ("dns", "dns"),
            ("device_mac", "device_mac")
        ]

        for key, data_key in labels:

            value = info.get(data_key) or self.t("unknown")

            self.device_box.insert(
                tk.END,
                f"{self.t(key)}: {value}\n"
            )

        self.device_box.insert(
            tk.END,
            "\n----------------------------------------\n"
        )

        self.device_box.insert(
            tk.END,
            f"{self.t('selected')}\n"
        )

        if self.selected_network:

            net = self.selected_network

            ssid = net["ssid"]

            if ssid == "<Hidden Network>":
                ssid = self.t("hidden")

            security = net["security"]

            if security == "Open":
                security = self.t("open")

            details = [
                ("ssid", ssid),
                ("mac", net["bssid"]),
                ("signal", f"{net['signal']}%"),
                ("security", security),
                ("channel", net["channel"]),
                ("frequency", net["frequency"])
            ]

            for key, value in details:

                self.device_box.insert(
                    tk.END,
                    f"{self.t(key)}: {value}\n"
                )

        else:

            self.device_box.insert(
                tk.END,
                self.t("not_selected") + "\n"
            )

            self.device_box.insert(
                tk.END,
                self.t("click_hint") + "\n"
            )

        self.device_box.insert(
            tk.END,
            "\n----------------------------------------\n"
        )

        self.device_box.insert(
            tk.END,
            f"{self.t('selected_device')}\n"
        )

        if self.selected_local_device:

            device = self.selected_local_device

            name = (
                self.t("self_device")
                if device["is_self"]
                else self.t("neighbor")
            )

            self.device_box.insert(
                tk.END,
                f"{name}\n"
            )

            self.device_box.insert(
                tk.END,
                f"{self.t('device_ip')}: {device['ip']}\n"
            )

            self.device_box.insert(
                tk.END,
                f"{self.t('mac')}: {device['mac']}\n"
            )

            if device["is_self"]:
                state_text = self.t("self_device")

            else:
                state_text, _ = self.get_device_status(
                    device["state"]
                )

            self.device_box.insert(
                tk.END,
                f"{self.t('device_state')}: {state_text}\n"
            )

        else:

            self.device_box.insert(
                tk.END,
                self.t("click_device") + "\n"
            )

        self.device_box.configure(state="disabled")

    # ======================================
    # NETWORK INFORMATION
    # ======================================

    def get_device_info(self):

        info = {
            "ip": "",
            "gateway": "",
            "dns": "",
            "device_mac": ""
        }

        try:

            result = run_command([
                "nmcli",
                "--terse",
                "--escape",
                "yes",
                "--fields",
                "DEVICE,TYPE,STATE",
                "device",
                "status"
            ])

            if result.returncode != 0:
                return info

            wifi_device = None

            for line in result.stdout.splitlines():

                fields = split_nmcli_line(line)

                if len(fields) < 3:
                    continue

                if (
                    fields[1].strip() == "wifi"
                    and fields[2].strip().startswith("connected")
                ):
                    wifi_device = fields[0].strip()
                    break

            if not wifi_device:
                return info

            details = run_command([
                "nmcli",
                "--terse",
                "--escape",
                "yes",
                "--fields",
                "GENERAL.HWADDR,IP4.ADDRESS,IP4.GATEWAY,IP4.DNS",
                "device",
                "show",
                wifi_device
            ])

            if details.returncode != 0:
                return info

            dns_values = []

            for line in details.stdout.splitlines():

                fields = split_nmcli_line(line)

                if len(fields) < 2:
                    continue

                key = fields[0].strip()
                value = ":".join(fields[1:]).strip()

                if key == "GENERAL.HWADDR":
                    info["device_mac"] = value

                elif key.startswith("IP4.ADDRESS"):
                    info["ip"] = value

                elif key.startswith("IP4.GATEWAY"):
                    info["gateway"] = value

                elif key.startswith("IP4.DNS") and value:
                    dns_values.append(value)

            info["dns"] = ", ".join(dns_values)

        except Exception:
            pass

        return info

    # ======================================
    # SCAN WORKER
    # ======================================

    def scan_worker(self, generation):

        try:

            if not shutil.which("nmcli"):

                self.result_queue.put(
                    ("error", generation, "nmcli")
                )
                return

            command = [
                "nmcli",
                "--terse",
                "--escape",
                "yes",
                "--fields",
                "SSID,BSSID,SIGNAL,SECURITY,CHAN,FREQ",
                "device",
                "wifi",
                "list",
                "--rescan",
                "yes"
            ]

            result = run_command(
                command,
                timeout=30
            )

            if result.returncode != 0:

                message = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "Unknown nmcli error"
                )

                self.result_queue.put(
                    ("error", generation, message)
                )
                return

            networks = []

            for line in result.stdout.splitlines():

                if not line.strip():
                    continue

                parts = split_nmcli_line(line)

                if len(parts) < 6:
                    continue

                try:
                    signal = int(parts[-4].strip())
                except ValueError:
                    signal = 0

                security = parts[-3].strip()

                if not security or security == "--":
                    security = "Open"

                networks.append({
                    "ssid": (
                        parts[0].strip()
                        or "<Hidden Network>"
                    ),
                    "bssid": parts[1].strip(),
                    "signal": signal,
                    "security": security,
                    "channel": parts[-2].strip(),
                    "frequency": parts[-1].strip()
                })

            device_info = self.get_device_info()

            local_devices = self.get_local_devices(
                device_info
            )

            self.result_queue.put((
                "success",
                generation,
                networks,
                device_info,
                local_devices
            ))

        except subprocess.TimeoutExpired:

            self.result_queue.put((
                "error",
                generation,
                "Scan timed out"
            ))

        except Exception as error:

            self.result_queue.put((
                "error",
                generation,
                str(error)
            ))

    # ======================================
    # START SCAN
    # ======================================

    def start_scan(self):

        if self.closed:
            return

        self.auto_scan_enabled = True

        if self.next_scan_job is not None:

            self.after_cancel(self.next_scan_job)
            self.next_scan_job = None

        if self.scan_in_progress:
            return

        self.scan_in_progress = True

        self.scan_generation += 1
        generation = self.scan_generation

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        self.status_label.configure(
            text=self.t("status_scanning")
        )

        worker = threading.Thread(
            target=self.scan_worker,
            args=(generation,),
            daemon=True
        )

        worker.start()

    # ======================================
    # STOP SCAN
    # ======================================

    def stop_scan(self):

        self.auto_scan_enabled = False

        if self.next_scan_job is not None:

            self.after_cancel(self.next_scan_job)
            self.next_scan_job = None

        self.scan_generation += 1
        self.scan_in_progress = False

        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

        self.status_label.configure(
            text=self.t("status_stopped")
        )

    # ======================================
    # SCHEDULE NEXT SCAN
    # ======================================

    def schedule_next_scan(self):

        if not self.auto_scan_enabled:
            return

        if self.next_scan_job is not None:
            self.after_cancel(self.next_scan_job)

        self.next_scan_job = self.after(
            SCAN_INTERVAL,
            self.start_scan
        )

    # ======================================
    # PROCESS QUEUE
    # ======================================

    def process_queue(self):

        if self.closed:
            return

        try:

            while True:

                message = self.result_queue.get_nowait()

                event_type = message[0]
                generation = message[1]

                if generation != self.scan_generation:
                    continue

                self.scan_in_progress = False

                self.start_btn.configure(state="normal")

                if self.auto_scan_enabled:
                    self.stop_btn.configure(state="normal")
                else:
                    self.stop_btn.configure(state="disabled")

                if event_type == "success":

                    networks = message[2]
                    self.device_info = message[3]
                    self.local_devices = message[4]

                    self.detected_networks = networks

                    if self.selected_network:

                        old_mac = self.selected_network["bssid"]

                        self.selected_network = next(
                            (
                                net for net in networks
                                if net["bssid"] == old_mac
                            ),
                            None
                        )

                    if self.selected_local_device:

                        old_mac = self.selected_local_device["mac"]

                        self.selected_local_device = next(
                            (
                                device
                                for device in self.local_devices
                                if device["mac"] == old_mac
                            ),
                            None
                        )

                    if self.selected_local_device is None:

                        self.selected_local_device = next(
                            (
                                device
                                for device in self.local_devices
                                if device["is_self"]
                            ),
                            None
                        )

                    self.assign_radar_positions()

                    self.render_networks()
                    self.render_local_devices()
                    self.render_information()

                    self.draw_targets()
                    self.draw_topology()

                    self.status_label.configure(
                        text=self.t("status_done")
                    )

                    self.schedule_next_scan()

                elif event_type == "error":

                    error = message[2]

                    if error == "nmcli":
                        display_error = self.t("no_nmcli")
                    else:
                        display_error = (
                            self.t("scan_error") + str(error)
                        )

                    self.results_box.delete("1.0", tk.END)
                    self.results_box.insert(
                        tk.END,
                        display_error
                    )

                    self.status_label.configure(
                        text=self.t("status_ready")
                    )

                    self.schedule_next_scan()

        except queue.Empty:
            pass

        self.after(100, self.process_queue)

    # ======================================
    # RENDER NETWORK LIST
    # ======================================

    def render_networks(self):

        self.results_box.delete("1.0", tk.END)

        if not self.detected_networks:

            self.results_box.insert(
                tk.END,
                self.t("no_networks") + "\n"
            )
            return

        for net in self.detected_networks:

            ssid = net["ssid"]

            if ssid == "<Hidden Network>":
                ssid = self.t("hidden")

            security = net["security"]

            if security == "Open":
                security = self.t("open")

            selected = ""

            if (
                self.selected_network
                and self.selected_network["bssid"] == net["bssid"]
            ):
                selected = "  < SELECTED >"

            self.results_box.insert(
                tk.END,
                "--------------------------\n"
                f"{self.t('ssid')}: {ssid}{selected}\n"
                f"{self.t('signal')}: {net['signal']}%\n"
                f"{self.t('security')}: {security}\n"
                f"{self.t('channel')}: {net['channel']}\n"
            )

        self.results_box.see("1.0")

    # ======================================
    # CLOSE APPLICATION
    # ======================================

    def on_close(self):

        self.closed = True
        self.auto_scan_enabled = False
        self.scan_generation += 1

        if self.next_scan_job is not None:

            try:
                self.after_cancel(self.next_scan_job)
            except tk.TclError:
                pass

        self.destroy()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app = WifiRadarApp()
    app.mainloop()