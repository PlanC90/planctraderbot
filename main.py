import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from datetime import datetime
import json
import os
import requests
import math
from decimal import Decimal, ROUND_DOWN
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Rate limiter için basit sınıf
class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = threading.Lock()
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                # Eski çağrıları temizle
                self.calls = [call_time for call_time in self.calls if now - call_time < self.period]
                
                # Rate limit kontrolü
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.period - (now - self.calls[0])
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    self.calls = []
                
                self.calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper

# Optimized requests session with retry logic
def create_session_with_retries():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
# Simple tooltip helper for labels
class Tooltip:
    def __init__(self, widget, text_provider):
        self.widget = widget
        self.text_provider = text_provider
        self.tip = None
        try:
            widget.bind('<Enter>', self.show)
            widget.bind('<Leave>', self.hide)
        except Exception:
            pass
    def show(self, event=None):
        try:
            text = self.text_provider() if callable(self.text_provider) else str(self.text_provider)
            if not text:
                return
            x = self.widget.winfo_rootx() + 16
            y = self.widget.winfo_rooty() + 20
            self.tip = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            lbl = tk.Label(tw, text=text, bg='#111827', fg='#e5e7eb', relief='solid', borderwidth=1, justify='left', padx=6, pady=4, wraplength=280)
            lbl.pack()
        except Exception:
            pass
    def hide(self, event=None):
        try:
            if self.tip:
                self.tip.destroy()
                self.tip = None
        except Exception:
            pass
# i18n
try:
    from locales.langs import LANGS, TRANSLATIONS, get_text
except Exception:
    LANGS, TRANSLATIONS = [], {}
    def get_text(lang, key):
        return key
# license verify
try:
    from licenses.verify import verify_license, PUBLIC_KEY_B64
except Exception:
    verify_license = None
    PUBLIC_KEY_B64 = ""

# updater
try:
    from updater import SoftwareUpdater, UpdateDialog
except Exception:
    SoftwareUpdater = None
    UpdateDialog = None

from core.config import load_config_all, save_config_env
from api.clients import make_client
from services.account import AccountService
from services.market import MarketService
from services.news import NewsService

class BinanceFuturesBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Binance Futures Trading Bot")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")
        
        # API Client
        self.client = None
        self.account_service = None
        self.market_service = MarketService()
        self.news_service = NewsService()
        self.api_key = ""
        self.api_secret = ""
        
        # Optimized requests session
        self.session = create_session_with_retries()
        
        # Trading variables
        self.current_symbol = "BTCUSDT"  # Varsayılan, settings'ten yüklenecek
        self.current_price = 0.0
        self.balance = 0.0
        self.positions = {}
        self.price_history = []
        self.time_history = []
        
        # Çoklu coin için değişkenler
        self.selected_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']  # Varsayılan coinler
        self.symbol_prices = {}     # Her coin için fiyat bilgisi
        self.symbol_changes = {}    # Her coin için değişim bilgisi
        self.symbol_momentum = {}   # Her coin için momentum durumu
        self.latest_prices = {}
        self.latest_changes = {}
        self.coin_stop_losses = {}  # Her coin için özel stop loss yüzdesi (örn: {'BTCUSDT': 5.0})
        self._last_selected_cards_update_ts = 0.0
        self._last_card_values = {}  # Son değerleri sakla
        self._ui_update_queue = []  # UI güncelleme kuyruğu
        self._ui_update_scheduled = False  # UI güncelleme zamanlanmış mı
        # API response önbellekleri
        self._cache_account = {'ts': 0.0, 'data': None}
        self._cache_positions = {'ts': 0.0, 'data': None}
        # Log UI batching kaldırıldı
        # Trades cache (to avoid heavy fetch every cycle)
        self._last_trades_fetch_ts = 0.0
        self._last_trades_cache = []
        # Income cache
        self._last_income_fetch_ts = 0.0
        self._last_income_cache = []
        
        # Geriye dönük uyumluluk için
        self.symbol_var = tk.StringVar(value="BTCUSDT")  # Eski kodlarla uyumluluk için
        
        # Environment and mode
        self.env_var = tk.StringVar(value="Test")  # Test veya Gerçek
        self.market_interval_var = tk.StringVar(value="30")  # saniye (min: 30 - API limit)
        # Language
        default_lang = 'tr - Türkçe'  # Combo box formatında başlangıç değeri
        self.lang_var = tk.StringVar(value=default_lang)
        self.current_language = default_lang.split(' - ')[0]  # Dil kodunu sakla (thread-safe)
        # License
        self.license_var = tk.StringVar(value="")
        self.license_valid = False
        self.license_activation_date = None  # Aktivasyon tarihi (timestamp)
        
        # Market breadth tracking (CoinPaprika + Binance)
        self.market_thread = None
        self.market_thread_running = False
        
        # Summary auto-update (every 5 seconds)
        self.summary_thread = None
        self.summary_thread_running = False
        self.prev_rising_count = None
        self.prev_falling_count = None
        self.prev_diff = None  # Bir önceki diff değeri (ardışık +2/+2 kontrolü için)
        self.prev_symbol_change = None
        self.top100_symbols = []
        self.top100_last_fetch = 0  # epoch seconds
        self.market_interval_seconds = 30
        
        # Momentum kaybı koruması
        self.last_market_trend = None  # 'up', 'down', 'neutral'
        self.trading_paused = False  # Momentum kaybı olduğunda True
        self.positive_momentum_count = 0  # Üst üste pozitif artış sayacı
        # momentum_loss_threshold artık UI'dan alınacak (self.momentum_threshold_var)
        
        # Log system kaldırıldı
        
        # Update notification
        self.update_available = False
        self.update_warning_label = None
        
        # Auto trade control
        self.auto_trade_enabled = False
        self.last_auto_action_time = 0
        # self.neutral_close_pct_var = tk.StringVar(value="2")  # Kaldırıldı
        # self.auto_percent_var = tk.StringVar(value="0")  # Kaldırıldı
        
        # Market trend latch (3-coin rule)
        self.market_up_latched = False
        self.market_up_baseline = 0
        # Symmetric state: 'up' | 'down' | None
        self.market_trend_state = None
        
        # Kapatma kontrolü için sayaç (açık pozisyon uyarısı)
        self.close_attempt_count = 0
        
        # Price update thread
        self.price_thread = None
        self.price_thread_running = False
        
        self.setup_ui()
        self.load_config()
        # Settings file
        self.settings_path = "ayarlar.txt"
        self.last_saved_settings = {}
        self.load_settings_file()
        # Settings yüklendikten sonra current_symbol'u güncelle
        self.current_symbol = self.symbol_var.get()
        
        # API bağlantısını otomatik olarak başlat (eğer API anahtarları varsa)
        self.root.after(2000, self.auto_connect_api)  # 2 saniye gecikme ile
        
        # Uygulama açıldığında hemen bilgileri güncelle
        self.root.after(500, self.initial_ui_update)  # 0.5 saniye gecikme ile
        
        
        # Program kapatılırken ayarları kaydet
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Interval sayısal cache'i güncelle
        try:
            self.market_interval_seconds = int(self.market_interval_var.get())
        except Exception:
            self.market_interval_seconds = 30
        # Start market monitor always for status updates
        self.start_market_monitor()
        
        # Haber akışını başlat
        self.start_news_monitor()
        # İlk sembol listesini yükle
        self.update_symbol_list()
        # Kaydedilmiş seçimleri yükle
        self.root.after(1000, self.restore_symbol_selections)  # 1 saniye gecikme ile
        # Otomatik güncelleme kontrolü (program yüklendikten sonra)
        self.auto_check_updates_on_startup()
    
    def auto_connect_api(self):
        """API anahtarları varsa otomatik olarak bağlantı kur"""
        try:
            # API anahtarlarını kontrol et
            if self.api_key and self.api_secret:
                self.log_message("API anahtarları bulundu, otomatik bağlantı kuruluyor...")
                # Mevcut connect_api fonksiyonunu çağır
                self.connect_api()
            else:
                self.log_message("API anahtarları bulunamadı, manuel bağlantı gerekli")
        except Exception as e:
            self.log_message(f"Otomatik API bağlantı hatası: {e}")
    
    def initial_ui_update(self):
        """Uygulama açıldığında hemen UI'yi güncelle"""
        try:
            # Test modu durumunu hemen güncelle
            self.update_test_mode_status()
            
            # Oto trade durumunu hemen güncelle
            self.update_auto_trade_status()
            
            # Coin listesini hemen güncelle
            self.log_message("Coin listesi yükleniyor...")
            self.update_symbol_list()
            
            # Seçilen coinlerin kutucuklarını hemen oluştur ve güncelle
            if hasattr(self, 'selected_coins_container'):
                self.log_message(f"📦 Başlangıçta coin kartları oluşturuluyor: {len(self.selected_symbols)} coin")
                self.update_selected_count_label()
                self.setup_selected_coins_cards()
                self.update_selected_coins_cards()
            
            # Özet kutucuklarını hemen güncelle (eğer API bağlıysa)
            if hasattr(self, 'client') and self.client:
                self.update_summary_cards()
            
            self.log_message("İlk UI güncellemesi tamamlandı")
            
        except Exception as e:
            self.log_message(f"İlk UI güncelleme hatası: {e}")
        
    def setup_ui(self):
        # Ana stil konfigürasyonu
        style = ttk.Style()
        style.theme_use('clam')
        # Dark palette
        style.configure('Dark.TFrame', background='#111827')
        style.configure('Dark.TLabelframe', background='#111827', foreground='#e5e7eb')
        style.configure('Dark.TLabelframe.Label', background='#111827', foreground='#9ca3af', font=('Segoe UI', 10, 'bold'))
        style.configure('TLabel', background='#111827', foreground='#e5e7eb', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=12, relief='raised', borderwidth=2)
        style.map('TButton', relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), padding=12, foreground='#ffffff', 
                       background='#2563eb', relief='raised', borderwidth=2)
        style.map('Accent.TButton', background=[('active', '#1d4ed8'), ('pressed', '#1e40af')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        # Modern button style for "Lisans Al" - With shadow
        style.configure('Modern.TButton', font=('Segoe UI', 10, 'bold'), padding=12, foreground='#ffffff', 
                       background='#7c3aed', relief='raised', borderwidth=2)
        style.map('Modern.TButton', background=[('active', '#6d28d9'), ('pressed', '#5b21b6')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        # Auto trade on/off styles - Modern with shadows
        style.configure('AutoOn.TButton', font=('Segoe UI', 10, 'bold'), padding=12, foreground='#111827', 
                       background='#22c55e', relief='raised', borderwidth=2)
        style.map('AutoOn.TButton', background=[('active', '#16a34a'), ('pressed', '#15803d')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        style.configure('AutoOff.TButton', font=('Segoe UI', 10, 'bold'), padding=12, foreground='#ffffff', 
                       background='#6b7280', relief='raised', borderwidth=2)
        style.map('AutoOff.TButton', background=[('active', '#4b5563'), ('pressed', '#374151')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        style.configure('TEntry', font=('Segoe UI', 10))
        style.configure('TCombobox', fieldbackground='#1f2937', background='#1f2937', foreground='#e5e7eb')
        # Light combobox for system light dropdowns
        style.configure('Light.TCombobox', fieldbackground='#f3f4f6', background='#f3f4f6', foreground='#111827')
        style.map('Light.TCombobox', fieldbackground=[('readonly', '#f3f4f6'), ('!disabled', '#f3f4f6')],
                                      foreground=[('readonly', '#111827'), ('!disabled', '#111827')])
        # Modern black theme
        style.theme_use('clam')
        BG = '#0a0a0a'
        CARD = '#101214'
        SUBTLE = '#0e0f11'
        FG = '#e5e7eb'
        MUTED = '#9ca3af'
        ACCENT = '#10b981'
        DANGER = '#ef4444'
        
        style.configure('.', background=BG, foreground=FG, fieldbackground=SUBTLE)
        
        # Treeview
        style.configure('Dark.Treeview', background=SUBTLE, fieldbackground=SUBTLE, foreground=FG, rowheight=26, borderwidth=0)
        style.configure('Treeview.Heading', background=CARD, foreground=MUTED, relief='flat', padding=8)
        style.map('Treeview.Heading', background=[('active', SUBTLE)])
        style.map('Dark.Treeview', background=[('selected', '#1f2937')], foreground=[('selected', '#ffffff')])
        
        # Cards
        style.configure('Card.TLabelframe', background=CARD, foreground=FG, borderwidth=0, padding=10)
        style.configure('Card.TLabelframe.Label', background=CARD, foreground=MUTED, font=('Segoe UI', 10, 'bold'))
        
        # Inputs
        style.configure('TEntry', fieldbackground=SUBTLE, foreground=FG, insertcolor=FG, borderwidth=0)
        style.configure('TCombobox', fieldbackground=SUBTLE, foreground=FG, arrowcolor=MUTED, borderwidth=0)
        
        # Buttons - Modern with shadows
        style.configure('TButton', background='#18181b', foreground=FG, padding=12, 
                       relief='raised', borderwidth=2, font=('Segoe UI', 10, 'bold'))
        style.map('TButton', background=[('active', '#202024'), ('pressed', '#27272a')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure('Accent.TButton', background=ACCENT, foreground=BG, padding=12, 
                       relief='raised', borderwidth=2, font=('Segoe UI', 10, 'bold'))
        style.map('Accent.TButton', background=[('active', '#059669'), ('pressed', '#047857')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure('Danger.TButton', background=DANGER, foreground='#ffffff', padding=12, 
                       relief='raised', borderwidth=2, font=('Segoe UI', 10, 'bold'))
        style.map('Danger.TButton', background=[('active', '#dc2626'), ('pressed', '#b91c1c')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure('Secondary.TButton', background='#26272b', foreground=FG, padding=12, 
                       relief='raised', borderwidth=2, font=('Segoe UI', 10, 'bold'))
        style.map('Secondary.TButton', background=[('active', '#2e3035'), ('pressed', '#1f2937')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        # Modern colored buttons for toolbar
        style.configure('Warning.TButton', background='#f59e0b', foreground='#ffffff', padding=12, 
                       relief='raised', borderwidth=2, font=('Segoe UI', 10, 'bold'))
        style.map('Warning.TButton', background=[('active', '#d97706'), ('pressed', '#b45309')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure('Save.TButton', background='#06b6d4', foreground='#ffffff', padding=12, 
                       relief='raised', borderwidth=2, font=('Segoe UI', 10, 'bold'))
        style.map('Save.TButton', background=[('active', '#0891b2'), ('pressed', '#0e7490')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure('Refresh.TButton', background='#8b5cf6', foreground='#ffffff', padding=12, 
                       relief='raised', borderwidth=2, font=('Segoe UI', 10, 'bold'))
        style.map('Refresh.TButton', background=[('active', '#7c3aed'), ('pressed', '#6d28d9')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure('Summary.TButton', background='#14b8a6', foreground='#ffffff', padding=12, 
                       relief='raised', borderwidth=2, font=('Segoe UI', 10, 'bold'))
        style.map('Summary.TButton', background=[('active', '#0d9488'), ('pressed', '#0f766e')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure('Update.TButton', background='#6366f1', foreground='#ffffff', padding=12, 
                       relief='raised', borderwidth=2, font=('Segoe UI', 10, 'bold'))
        style.map('Update.TButton', background=[('active', '#4f46e5'), ('pressed', '#4338ca')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        # Badges
        style.configure('Badge.Green.TLabel', background=ACCENT, foreground=BG, padding=8, font=('Segoe UI Semibold', 12))
        style.configure('Badge.Red.TLabel', background=DANGER, foreground='#ffffff', padding=8, font=('Segoe UI Semibold', 12))
        style.configure('Badge.Neutral.TLabel', background='#1f2937', foreground=FG, padding=8, font=('Segoe UI Semibold', 12))
        
        # Connect Button Styles - Modern with shadows
        style.configure('Connect.Disconnected.TButton', 
                       background='#dc2626', activebackground='#b91c1c', 
                       foreground='white', font=('Segoe UI', 11, 'bold'),
                       relief='raised', borderwidth=2, padding=12, focuscolor='none')
        style.map('Connect.Disconnected.TButton', 
                 background=[('active', '#b91c1c'), ('pressed', '#991b1b')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        style.configure('Connect.Connected.TButton', 
                       background='#16a34a', activebackground='#15803d', 
                       foreground='white', font=('Segoe UI', 11, 'bold'),
                       relief='raised', borderwidth=2, padding=12, focuscolor='none')
        style.map('Connect.Connected.TButton', 
                 background=[('active', '#15803d'), ('pressed', '#166534')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        # Scrollbars
        style.configure('Vertical.TScrollbar', background=CARD, troughcolor=SUBTLE, arrowcolor=MUTED, bordercolor=CARD)
        style.configure('Horizontal.TScrollbar', background=CARD, troughcolor=SUBTLE, arrowcolor=MUTED, bordercolor=CARD)
        
        # Banner label defaults
        style.configure('Banner.Title.TLabel', background=BG, foreground=FG, font=('Segoe UI', 14, 'bold'))
        
        # Header styles
        style.configure('Header.TFrame', background=BG)
        style.configure('Header.TLabel', background=BG, foreground=FG, font=('Segoe UI Semibold', 12))
        style.configure('Header.TButton', font=('Segoe UI', 10), padding=6)
        self.root.configure(bg=BG)
        
        # Ana container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sol panel - API ve Hesap Bilgileri (scrollable)
        left_container = ttk.Frame(main_frame, style='Dark.TFrame')
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_canvas = tk.Canvas(left_container, background='#111827', highlightthickness=0, width=300)
        left_scroll = ttk.Scrollbar(left_container, orient=tk.VERTICAL, command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scroll.set)
        left_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        left_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        left_frame = ttk.Frame(left_canvas, style='Dark.TFrame')
        left_window = left_canvas.create_window((0, 0), window=left_frame, anchor='nw')
        # Resize and scrollregion bindings
        def _on_frame_config(event):
            left_canvas.configure(scrollregion=left_canvas.bbox('all'))
        left_frame.bind('<Configure>', _on_frame_config)
        def _on_canvas_config(event):
            left_canvas.itemconfigure(left_window, width=event.width)
        left_canvas.bind('<Configure>', _on_canvas_config)
        # Mouse wheel scroll sadece sol panel için (Windows)
        def _on_left_mousewheel(event):
            left_canvas.yview_scroll(-int(event.delta/120), 'units')
        # Sadece sol panel ve içeriği için mouse wheel
        left_canvas.bind('<MouseWheel>', _on_left_mousewheel)
        left_frame.bind('<MouseWheel>', _on_left_mousewheel)
        # Sol panel widget'larına da bind et
        def bind_mousewheel_to_children(widget):
            try:
                widget.bind('<MouseWheel>', _on_left_mousewheel)
                for child in widget.winfo_children():
                    bind_mousewheel_to_children(child)
            except Exception:
                pass
        # Sol panel tüm widget'larına uygula
        self.root.after(100, lambda: bind_mousewheel_to_children(left_frame))
        
        # API Ayarları
        self.api_frame = ttk.LabelFrame(left_frame, text="🔑 API", padding=10, style='Dark.TLabelframe')
        self.api_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.env_label_lbl = ttk.Label(self.api_frame, text=f"🌐 {self.tr('env_label')}")
        self.env_label_lbl.pack(anchor=tk.W)
        env_combo = ttk.Combobox(self.api_frame, textvariable=self.env_var, values=[self.tr('env_test'), self.tr('env_live')], state="readonly", style='Light.TCombobox')
        env_combo.pack(fill=tk.X, pady=(0, 5))
        env_combo.bind('<<ComboboxSelected>>', self.on_env_change)
        # Başlangıç değerini ayarla
        self.env_var.set(self.tr('env_test'))
        
        # Dil / Language
        self.language_label = ttk.Label(self.api_frame, text=f"🌍 {self.tr('language_label')}")
        self.language_label.pack(anchor=tk.W)
        lang_values = [f"{code} - {name}" for code, name in getattr(self, 'langs_list', getattr(__import__('builtins'), 'list', list))(LANGS) ] if LANGS else ["tr - Turkish", "en - English"]
        self.lang_combo = ttk.Combobox(self.api_frame, textvariable=self.lang_var, values=lang_values, state="readonly", style='Light.TCombobox')
        self.lang_combo.pack(fill=tk.X, pady=(0, 5))
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        self.api_key_lbl = ttk.Label(self.api_frame, text=f"🗝️ {self.tr('api_key')}")
        self.api_key_lbl.pack(anchor=tk.W)
        self.api_key_entry = ttk.Entry(self.api_frame, width=30, show="*")
        self.api_key_entry.pack(fill=tk.X, pady=(0, 5))
        # API alanlarından çıkınca otomatik kaydet
        try:
            self.api_key_entry.bind('<FocusOut>', lambda e: self.save_config())
        except Exception:
            pass
        
        self.api_secret_lbl = ttk.Label(self.api_frame, text=f"🔒 {self.tr('api_secret')}")
        self.api_secret_lbl.pack(anchor=tk.W)
        self.api_secret_entry = ttk.Entry(self.api_frame, width=30, show="*")
        self.api_secret_entry.pack(fill=tk.X, pady=(0, 10))
        try:
            self.api_secret_entry.bind('<FocusOut>', lambda e: self.save_config())
        except Exception:
            pass
        
        # License area
        self.lic_frame = ttk.LabelFrame(left_frame, text=f"🔐 {self.tr('license')}", padding=10, style='Dark.TLabelframe')
        self.lic_frame.pack(fill=tk.X, pady=(0, 10))
        self.license_code_label = ttk.Label(self.lic_frame, text=self.tr('license_code'))
        self.license_code_label.pack(anchor=tk.W)
        self.license_entry = ttk.Entry(self.lic_frame, textvariable=self.license_var, show='*')
        self.license_entry.pack(fill=tk.X, pady=(0, 6))
        self.license_status_lbl = ttk.Label(self.lic_frame, text=self.tr('license_status_unlicensed'), foreground="#f87171")
        self.license_status_lbl.pack(anchor=tk.W)
        btns = ttk.Frame(self.lic_frame)
        btns.pack(fill=tk.X, pady=(6,0))
        btns.columnconfigure(0, weight=1, uniform='license_btns')
        btns.columnconfigure(1, weight=1, uniform='license_btns')
        
        btn_ipady = 3  # Ana butonlarla aynı yükseklik
        
        self.activate_btn = ttk.Button(btns, text=f"✔ {self.tr('activate')}", command=self.activate_license, style='Accent.TButton')
        self.activate_btn.grid(row=0, column=0, sticky='nsew', padx=(0, 2), pady=2, ipady=btn_ipady)
        # Modern "Lisans Al" butonu
        self.get_license_btn = ttk.Button(btns, text=f"🛒 {self.tr('get_license_btn_text')}", command=self.open_license_site, style='Modern.TButton')
        self.get_license_btn.grid(row=0, column=1, sticky='nsew', padx=(2, 0), pady=2, ipady=btn_ipady)
        
        # API Connect butonu - pack kullandığı için ipady direkt ekliyoruz
        self.connect_btn = ttk.Button(self.api_frame, text=f"🔌 {self.tr('connect_btn_text')}", command=self.connect_api, style='Connect.Disconnected.TButton')
        self.connect_btn.pack(fill=tk.BOTH, expand=True, pady=2, ipady=btn_ipady)
        
        # Haber API Token kaldırıldı - Sabit token kullanılıyor
        
        # Hesap Bilgileri - KALDIRILDI (UI'da gösterilmiyor, sadece backend değişkenler)
        # Balance ve connection için dummy değişkenler (hata önlemek için)
        self.balance_label = None
        self.connection_label = None
        
        # Çoklu Symbol seçimi
        self.symbol_frame = ttk.LabelFrame(left_frame, text=f"🔁 {self.tr('multi_coin_selection')}", padding=10, style='Dark.TLabelframe')
        self.symbol_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Seçili coinleri göster
        self.selected_count_label = ttk.Label(self.symbol_frame, text=self.tr('selected_count').format(count=0))
        self.selected_count_label.pack(anchor=tk.W)
        
        # Arama + Listbox için frame
        list_frame = ttk.Frame(self.symbol_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Arama kutusu
        search_row = ttk.Frame(list_frame)
        search_row.pack(fill=tk.X, pady=(0, 6))
        self.search_lbl = ttk.Label(search_row, text=self.tr('search_label'))
        self.search_lbl.pack(side=tk.LEFT)
        self.symbol_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.symbol_search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6,0))
        search_entry.bind('<KeyRelease>', lambda e: self.filter_symbol_list())
        
        # Multi-select listbox
        self.symbol_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=8,
                                       bg='#1f2937', fg='#e5e7eb', selectbackground='#3b82f6')
        symbol_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.symbol_listbox.yview)
        self.symbol_listbox.configure(yscrollcommand=symbol_scrollbar.set)
        
        self.symbol_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        symbol_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Seçim değişimi için bind
        self.symbol_listbox.bind('<<ListboxSelect>>', self.on_symbol_selection_change)
        
        # Butonlar
        btn_frame = ttk.Frame(self.symbol_frame)
        btn_frame.pack(fill=tk.X, pady=(6, 0))
        
        # Grid layout ile butonları yerleştir (ana butonlarla aynı sistem)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        btn_ipady = 3  # Ana butonlarla aynı yükseklik
        
        self.select_all_btn = ttk.Button(btn_frame, text=self.tr('add_selected'), command=self.add_selected_symbols, style='Accent.TButton')
        self.select_all_btn.grid(row=0, column=0, sticky='nsew', padx=(0, 2), pady=2, ipady=btn_ipady)
        
        self.clear_selection_btn = ttk.Button(btn_frame, text=self.tr('remove_selected'), command=self.remove_selected_symbols, style='Danger.TButton')
        self.clear_selection_btn.grid(row=0, column=1, sticky='nsew', padx=(2, 0), pady=2, ipady=btn_ipady)
        
        
        # Trading Panel
        self.trading_frame = ttk.LabelFrame(left_frame, text=f"🛠️ {self.tr('trading')}", padding=10, style='Dark.TLabelframe')
        self.trading_frame.pack(fill=tk.X, pady=(0, 10))
        
        
        # Position Size
        ps_row = ttk.Frame(self.trading_frame)
        ps_row.pack(fill=tk.X)
        self.pos_size_lbl = ttk.Label(ps_row, text=f"💰 {self.tr('balance_percent_label')}")
        self.pos_size_lbl.pack(side=tk.LEFT, anchor=tk.W)
        self._add_help_icon(ps_row, 'help_balance_percent')
        self.balance_percent_var = tk.StringVar(value="10")
        self.balance_percent_entry = ttk.Entry(self.trading_frame, textvariable=self.balance_percent_var)
        self.balance_percent_entry.pack(fill=tk.X, pady=(0, 5))
        self.balance_percent_entry.bind('<FocusOut>', self.on_balance_percent_change)
        self.balance_percent_entry.bind('<Return>', self.on_balance_percent_change)
        
        # Leverage
        lev_row = ttk.Frame(self.trading_frame)
        lev_row.pack(fill=tk.X)
        self.lev_lbl = ttk.Label(lev_row, text=f"📈 {self.tr('leverage_label')}")
        self.lev_lbl.pack(side=tk.LEFT, anchor=tk.W)
        self._add_help_icon(lev_row, 'help_leverage')
        self.leverage_var = tk.StringVar(value="1")
        leverage_combo = ttk.Combobox(self.trading_frame, textvariable=self.leverage_var,
                                     values=["1", "2", "3", "5", "10", "20"], state="readonly", style='Light.TCombobox')
        leverage_combo.pack(fill=tk.X, pady=(0, 10))
        leverage_combo.bind('<<ComboboxSelected>>', self.on_leverage_change)
        
        # Otomatik kontrol süresi
        int_row = ttk.Frame(self.trading_frame)
        int_row.pack(fill=tk.X)
        self.market_int_lbl = ttk.Label(int_row, text=f"⏱️ {self.tr('market_interval_sec')}")
        self.market_int_lbl.pack(side=tk.LEFT, anchor=tk.W)
        self._add_help_icon(int_row, 'help_market_interval')
        self.interval_entry = ttk.Entry(self.trading_frame, textvariable=self.market_interval_var)
        self.interval_entry.pack(fill=tk.X, pady=(0, 10))
        self.interval_entry.bind('<FocusOut>', self.on_interval_change)
        self.interval_entry.bind('<Return>', self.on_interval_change)
        
        # Risk Yönetimi Ayarları
        target_frame = ttk.Frame(self.trading_frame)
        target_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Zarar Durdur (%)
        sl_row = ttk.Frame(target_frame)
        sl_row.pack(fill=tk.X)
        self.stop_lbl = ttk.Label(sl_row, text=f"🛑 {self.tr('stop_loss_pct_label')}")
        self.stop_lbl.pack(side=tk.LEFT, anchor=tk.W)
        self._add_help_icon(sl_row, 'help_stop_loss_pct')
        self.stop_loss_pct_var = tk.StringVar(value="0")
        self.stop_entry = ttk.Entry(target_frame, textvariable=self.stop_loss_pct_var)
        self.stop_entry.pack(fill=tk.X)
        self.stop_entry.bind('<FocusOut>', self.on_target_change)
        self.stop_entry.bind('<Return>', self.on_target_change)
        
        # Kar Al (%)
        tp_row = ttk.Frame(target_frame)
        tp_row.pack(fill=tk.X)
        self.take_profit_lbl = ttk.Label(tp_row, text=f"✅ {self.tr('take_profit_pct_label')}")
        self.take_profit_lbl.pack(side=tk.LEFT, anchor=tk.W)
        self._add_help_icon(tp_row, 'help_take_profit_pct')
        self.take_profit_pct_var = tk.StringVar(value="0")
        self.take_profit_entry = ttk.Entry(target_frame, textvariable=self.take_profit_pct_var)
        self.take_profit_entry.pack(fill=tk.X)
        self.take_profit_entry.bind('<FocusOut>', self.on_target_change)
        self.take_profit_entry.bind('<Return>', self.on_target_change)
        
        # Piyasa Trend Eşiği (Yeni)
        market_threshold_row = ttk.Frame(target_frame)
        market_threshold_row.pack(fill=tk.X, pady=(8, 0))
        self.market_threshold_lbl = ttk.Label(market_threshold_row, text=f"📊 {self.tr('market_threshold_label')}")
        self.market_threshold_lbl.pack(side=tk.LEFT, anchor=tk.W)
        self._add_help_icon(market_threshold_row, 'help_market_threshold')
        self.market_threshold_var = tk.StringVar(value="55")
        self.market_threshold_entry = ttk.Entry(target_frame, textvariable=self.market_threshold_var)
        self.market_threshold_entry.pack(fill=tk.X)
        self.market_threshold_entry.bind('<FocusOut>', self.on_market_threshold_change)
        self.market_threshold_entry.bind('<Return>', self.on_market_threshold_change)
        
        # Momentum Kaybı Eşiği
        momentum_row = ttk.Frame(target_frame)
        momentum_row.pack(fill=tk.X, pady=(8, 0))
        self.momentum_lbl = ttk.Label(momentum_row, text=f"⚡ {self.tr('momentum_threshold_label')}")
        self.momentum_lbl.pack(side=tk.LEFT, anchor=tk.W)
        self._add_help_icon(momentum_row, 'help_momentum_threshold')
        # Bekleyen momentum threshold değeri varsa kullan, yoksa varsayılan 3
        momentum_value = getattr(self, '_pending_momentum_threshold', '3')
        self.momentum_threshold_var = tk.StringVar(value=momentum_value)
        self.momentum_entry = ttk.Entry(target_frame, textvariable=self.momentum_threshold_var)
        self.momentum_entry.pack(fill=tk.X)
        self.momentum_entry.bind('<FocusOut>', self.on_momentum_change)
        self.momentum_entry.bind('<Return>', self.on_momentum_change)
        
        # Oto trade durum etiketi
        self.auto_status_label = ttk.Label(self.trading_frame, text=self.tr('auto_off'))
        self.auto_status_label.pack(anchor=tk.W, pady=(6,6))
        
        # Ayarları Kaydet Butonu
        save_btn_frame = ttk.Frame(target_frame)
        save_btn_frame.pack(fill=tk.X, pady=(12, 0))
        self.save_settings_btn_bottom = ttk.Button(save_btn_frame, text=f"💾 {self.tr('save_settings_btn')}", command=self.manual_save_settings, style='Save.TButton')
        self.save_settings_btn_bottom.pack(fill=tk.X)
        
        # Default Ayarlar Butonu
        default_btn_frame = ttk.Frame(target_frame)
        default_btn_frame.pack(fill=tk.X, pady=(8, 0))
        self.default_settings_btn = ttk.Button(default_btn_frame, text=f"🔄 {self.tr('default_settings_btn')}", command=self.reset_to_default_settings, style='Warning.TButton')
        self.default_settings_btn.pack(fill=tk.X)
        
        
        
        # Sağ panel - Grafik ve Pozisyonlar (scrollable)
        right_container = ttk.Frame(main_frame, style='Dark.TFrame')
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_canvas = tk.Canvas(right_container, background='#111827', highlightthickness=0)
        right_scroll = ttk.Scrollbar(right_container, orient=tk.VERTICAL, command=right_canvas.yview)
        right_canvas.configure(yscrollcommand=right_scroll.set)
        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame = ttk.Frame(right_canvas, style='Dark.TFrame')
        right_window = right_canvas.create_window((0, 0), window=right_frame, anchor='nw')
        # Resize and scrollregion bindings
        def _on_right_frame_config(event):
            right_canvas.configure(scrollregion=right_canvas.bbox('all'))
        right_frame.bind('<Configure>', _on_right_frame_config)
        def _on_right_canvas_config(event):
            right_canvas.itemconfigure(right_window, width=event.width)
        right_canvas.bind('<Configure>', _on_right_canvas_config)
        
        # Sağ panel için mouse wheel scroll (Windows)
        def _on_right_mousewheel(event):
            right_canvas.yview_scroll(-int(event.delta/120), 'units')
        # Sağ panel ve içeriği için mouse wheel
        right_canvas.bind('<MouseWheel>', _on_right_mousewheel)
        right_frame.bind('<MouseWheel>', _on_right_mousewheel)
        # Sağ panel widget'larına da bind et
        def bind_right_mousewheel_to_children(widget):
            try:
                widget.bind('<MouseWheel>', _on_right_mousewheel)
                for child in widget.winfo_children():
                    bind_right_mousewheel_to_children(child)
            except Exception:
                pass
        # Sağ panel tüm widget'larına uygula
        self.root.after(100, lambda: bind_right_mousewheel_to_children(right_frame))
        
        # Durum Banner'ı (sadece piyasa durumu)
        self.status_banner = tk.Frame(right_frame, bg='#111111')
        self.status_banner.pack(fill=tk.X, pady=(0, 8))
        self._banner_inner = tk.Frame(self.status_banner, bg=self.status_banner['bg'])
        self._banner_inner.pack(fill=tk.X, padx=12, pady=12)
        
        # Sol taraf: Logo + TRADER BOT AI
        logo_frame = tk.Frame(self._banner_inner, bg='#111111')
        logo_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Logo'yu yükle ve göster
        try:
            from PIL import Image, ImageTk
            logo_img = Image.open('assets/logo.png')
            # Logo boyutunu ayarla (yükseklik 50px)
            logo_height = 50
            aspect_ratio = logo_img.width / logo_img.height
            logo_width = int(logo_height * aspect_ratio)
            logo_img = logo_img.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            
            logo_label = tk.Label(logo_frame, image=self.logo_photo, bg='#111111')
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            print(f"Logo yükleme hatası: {e}")
        
        # TRADER BOT AI yazısı
        trader_text = tk.Label(logo_frame, text=self.tr('trader_bot_ai'), 
                              font=('Segoe UI', 18, 'bold'), 
                              bg='#111111', fg='#10b981')
        trader_text.pack(side=tk.LEFT)
        
        # Ortalanmış merkez grup
        self._banner_center = tk.Frame(self._banner_inner, bg=self.status_banner['bg'])
        self._banner_center.pack(anchor='center')
        
        # Piyasa durumu metni (sabit boyut)
        self.market_status_label = tk.Label(self._banner_center, text=self.tr('market_neutral_text'), font=('Segoe UI', 16, 'bold'), bg='#111111', fg='white', padx=20, pady=12, relief='raised', borderwidth=1, width=20)
        self.market_status_label.pack(side=tk.LEFT)
        
        # Sağ üst köşe bilgi paneli
        self.info_panel = tk.Frame(self._banner_center, bg='#111111')
        self.info_panel.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Oto Trade durumu
        self.auto_trade_status = tk.Label(self.info_panel, text=self.tr('auto_trade_off_label'), font=('Segoe UI', 10, 'bold'), bg='#111111', fg='#ef4444')
        self.auto_trade_status.pack(anchor='e')
        
        # Test/Canlı modu
        self.test_mode_status = tk.Label(self.info_panel, text=self.tr('mode_test'), font=('Segoe UI', 10, 'bold'), bg='#111111', fg='#f59e0b')
        self.test_mode_status.pack(anchor='e')
        
        
        # PNL Paneli kaldırıldı
        
        # Seçilen Coinler Kutucukları (Shadow + Card) - dikey olarak uzasın
        selected_coins_shadow = tk.Frame(right_frame, bg='#050505')
        selected_coins_shadow.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        tk.Frame(selected_coins_shadow, bg='#f59e0b', width=4, height=1).pack(side=tk.LEFT, fill=tk.Y)
        self.selected_coins_frame = ttk.LabelFrame(selected_coins_shadow, text=f"🎯 {self.tr('selected_coins_title')}", padding=10, style='Card.TLabelframe')
        self.selected_coins_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Seçilen coinlerin kutucukları için container - dikey olarak uzasın
        self.selected_coins_container = tk.Frame(self.selected_coins_frame, bg='#1f2937')
        self.selected_coins_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Modern Özet Kutucukları (Shadow + Card) - Tam genişlik
        summary_shadow = tk.Frame(right_frame, bg='#050505')
        summary_shadow.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        tk.Frame(summary_shadow, bg='#3b82f6', width=4, height=1).pack(side=tk.LEFT, fill=tk.Y)
        summary_frame = ttk.LabelFrame(summary_shadow, text=f"📊 {self.tr('account_summary')}", padding=10, style='Card.TLabelframe')
        self.summary_frame = summary_frame
        summary_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Modern kutucuklar için grid layout
        self.setup_modern_summary_cards(summary_frame)
        
        # Seçilen coinlerin kutucuklarını oluştur
        self.setup_selected_coins_cards()
        
        # Pozisyonlar listesi (Shadow + Card)
        positions_shadow = tk.Frame(right_frame, bg='#050505')
        positions_shadow.pack(fill=tk.BOTH, expand=True)
        tk.Frame(positions_shadow, bg='#8b5cf6', width=4, height=1).pack(side=tk.LEFT, fill=tk.Y)
        
        # Ortalanmış başlık için özel container
        pos_title_frame = tk.Frame(positions_shadow, bg='#101214')
        pos_title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Sol hizalı başlık
        self.pos_title_label = tk.Label(pos_title_frame, text=f"📂 {self.tr('open_positions_title')}", 
                                   font=('Segoe UI', 10, 'bold'), 
                                   bg='#101214', fg='#9ca3af', 
                                   pady=10)
        self.pos_title_label.pack(anchor='w', padx=10)
        
        positions_frame = ttk.Frame(pos_title_frame, style='Card.TFrame')
        self.positions_frame = positions_frame
        positions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        # Toolbar for actions
        pos_toolbar = ttk.Frame(positions_frame, style='Dark.TFrame')
        pos_toolbar.pack(fill=tk.X, pady=(0,6))
        # Buttons near 'Tümünü Kapat' - RESPONSIVE LAYOUT
        center_bar = ttk.Frame(pos_toolbar, style='Dark.TFrame')
        center_bar.pack(fill=tk.X, expand=True, padx=4)  # Ekranı doldur
        
        # Grid layout ile responsive butonlar - Her buton eşit genişlikte
        # Her kolonu eşit weight ile configure et (responsive)
        for i in range(8):
            center_bar.columnconfigure(i, weight=1, uniform='btn')
        
        # Butonları grid ile yerleştir (padding ve font responsive olarak ayarlanacak)
        # ipady ile iç yükseklik arttırıldı
        btn_ipady = 3  # İç yükseklik padding'i
        
        self.close_all_btn = ttk.Button(center_bar, text=self.tr('close_all_trades'), command=self.close_all_positions, style='Danger.TButton')
        self.close_all_btn.grid(row=0, column=0, sticky='nsew', padx=1, pady=2, ipady=btn_ipady)
        
        self.close_selected_btn = ttk.Button(center_bar, text=self.tr('close_selected_trade'), command=self.close_selected_position, style='Warning.TButton')
        self.close_selected_btn.grid(row=0, column=1, sticky='nsew', padx=1, pady=2, ipady=btn_ipady)
        
        self.auto_btn = ttk.Button(center_bar, text=self.tr('auto_trade_btn'), command=self.toggle_auto_trade, style='AutoOff.TButton')
        self.auto_btn.grid(row=0, column=2, sticky='nsew', padx=1, pady=2, ipady=btn_ipady)
        
        # save_settings_btn kaldırıldı - sol paneldeki buton kullanılıyor
        
        self.refresh_btn = ttk.Button(center_bar, text=self.tr('refresh_btn'), command=self.update_symbol_list, style='Refresh.TButton')
        self.refresh_btn.grid(row=0, column=3, sticky='nsew', padx=1, pady=2, ipady=btn_ipady)
        
        self.refresh_summary_btn = ttk.Button(center_bar, text=self.tr('refresh_summary_btn'), command=self.manual_refresh_summary, style='Summary.TButton')
        self.refresh_summary_btn.grid(row=0, column=4, sticky='nsew', padx=1, pady=2, ipady=btn_ipady)
        
        self.update_btn = ttk.Button(center_bar, text=self.tr('update_btn'), command=self.check_for_updates, style='Update.TButton')
        self.update_btn.grid(row=0, column=5, sticky='nsew', padx=1, pady=2, ipady=btn_ipady)
        
        # Kullanım kılavuzu butonu - Mor renk (diğer butonlardan farklı)
        self.user_guide_btn = ttk.Button(center_bar, text=self.tr('user_guide_btn'), command=self.show_user_guide, style='Modern.TButton')
        self.user_guide_btn.grid(row=0, column=6, sticky='nsew', padx=1, pady=2, ipady=btn_ipady)
        
        # Window resize event'i için buton metinlerini responsive yap
        self.root.bind('<Configure>', self.on_window_resize)
        # İlk açılışta da buton metinlerini ayarla (debounce olmadan direkt)
        self.root.after(100, self._do_resize_buttons)
        # Log butonu kaldırıldı
        
        # Güncelleme uyarı rozeti (başlangıçta gizli) - grid layout için ayrı satır
        self.update_warning_label = tk.Label(center_bar, text="", 
                                           bg=CARD, fg='#ef4444',
                                           font=('Segoe UI', 10, 'bold'))
        # Varsayılan olarak gizle, grid_remove ile
        self.update_warning_label.grid(row=1, column=0, columnspan=8, sticky='ew', pady=(4, 0))
        self.update_warning_label.grid_remove()  # Başlangıçta gizli
        
        # Açık pozisyonlar için scrollable frame
        pos_tree_frame = tk.Frame(positions_frame, bg=CARD)
        pos_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for positions (kaldıraç oranı eklendi, checkbox eklendi)
        # Kolon ID'leri (sabit - veri bağlama için)
        columns = ("Select", "Symbol", "Side", "Size", "Entry Price", "Leverage", "PNL")
        self.positions_tree = ttk.Treeview(pos_tree_frame, columns=columns, show="headings", height=8, style='Dark.Treeview')
        pos_scrollbar = ttk.Scrollbar(pos_tree_frame, orient=tk.VERTICAL, command=self.positions_tree.yview)
        self.positions_tree.configure(yscrollcommand=pos_scrollbar.set)
        
        # Checkbox state'lerini saklamak için dict
        self.position_checkboxes = {}  # {item_id: True/False}
        
        # Zebra, hover ve LONG/SHORT renkleri
        self.positions_tree.tag_configure('even', background='#111827')
        self.positions_tree.tag_configure('odd', background='#0f172a')
        self.positions_tree.tag_configure('hover', background='#1f2937')
        # LONG/SHORT renk ayarları
        self.positions_tree.tag_configure('long_even', background='#1a3f2e')  # Açık yeşil - çift satır
        self.positions_tree.tag_configure('long_odd', background='#163529')   # Açık yeşil - tek satır
        self.positions_tree.tag_configure('short_even', background='#3f1a1a') # Açık kırmızı - çift satır
        self.positions_tree.tag_configure('short_odd', background='#351616')  # Açık kırmızı - tek satır
        
        # Kolon başlıklarını çeviriye dahil et
        column_headers = {
            "Select": "☑",  # Checkbox sütunu
            "Symbol": self.tr('position_symbol'),
            "Side": self.tr('position_side'),
            "Size": self.tr('position_size'),
            "Entry Price": self.tr('position_entry_price'),
            "Leverage": self.tr('position_leverage'),
            "PNL": self.tr('position_pnl')
        }
        
        # Kolon ayarları (genişlik ve hizalama) - Tümü ortalı
        column_configs = {
            "Select": {"width": 50, "anchor": "center", "minwidth": 40},
            "Symbol": {"width": 110, "anchor": "center", "minwidth": 90},
            "Side": {"width": 70, "anchor": "center", "minwidth": 60},
            "Size": {"width": 130, "anchor": "center", "minwidth": 110},
            "Entry Price": {"width": 140, "anchor": "center", "minwidth": 120},
            "Leverage": {"width": 70, "anchor": "center", "minwidth": 60},
            "PNL": {"width": 110, "anchor": "center", "minwidth": 90}
        }
        
        for col in columns:
            # Çevrilmiş başlığı kullan
            self.positions_tree.heading(col, text=column_headers.get(col, col), anchor="center")
            config = column_configs.get(col, {"width": 110, "anchor": "center", "minwidth": 90})
            self.positions_tree.column(col, 
                                     width=config["width"], 
                                     anchor=config["anchor"],
                                     minwidth=config["minwidth"],
                                     stretch=True)  # Sayfaya yayılması için stretch=True
        
        # Checkbox toggle için tıklama eventi
        self.positions_tree.bind('<Button-1>', self.on_position_tree_click)
                
        self.positions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pos_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 📰 Haber Akışı Bölümü
        news_shadow = tk.Frame(right_frame, bg='#8b5cf6', height=2)
        news_shadow.pack(fill=tk.X, pady=(10, 0))
        
        news_frame = tk.Frame(right_frame, bg=CARD, relief='solid', borderwidth=1)
        news_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Başlık
        news_header = tk.Frame(news_frame, bg=CARD)
        news_header.pack(fill=tk.X, padx=12, pady=8)
        
        self.news_title_label = tk.Label(news_header, text=f"📰 {self.tr('crypto_news')}", font=('Segoe UI', 14, 'bold'), 
                bg=CARD, fg=FG)
        self.news_title_label.pack(side=tk.LEFT)
        
        self.news_refresh_btn = tk.Button(news_header, text="🔄", font=('Segoe UI', 10),
                                         bg='#374151', fg='white', relief='flat',
                                         cursor='hand2', padx=8, pady=4,
                                         command=lambda: threading.Thread(target=self.refresh_news, daemon=True).start())
        self.news_refresh_btn.pack(side=tk.RIGHT)
        
        # Haber listesi (scrollable)
        news_container = tk.Frame(news_frame, bg=CARD)
        news_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        news_canvas = tk.Canvas(news_container, bg=CARD, highlightthickness=0)
        news_scrollbar = ttk.Scrollbar(news_container, orient=tk.VERTICAL, command=news_canvas.yview)
        news_canvas.configure(yscrollcommand=news_scrollbar.set)
        
        self.news_list_frame = tk.Frame(news_canvas, bg=CARD)
        self.news_canvas = news_canvas  # Canvas'ı sakla
        self.news_window = news_canvas.create_window((0, 0), window=self.news_list_frame, anchor='nw')
        
        news_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        news_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas genişliği değiştiğinde frame genişliğini güncelle - SAĞA KADAR UZAT
        def _on_canvas_configure(event):
            # Canvas genişliği kadar frame genişliği yap
            canvas_width = event.width
            news_canvas.itemconfig(self.news_window, width=canvas_width)
        news_canvas.bind('<Configure>', _on_canvas_configure)
        
        # Mouse wheel scroll
        def _on_news_mousewheel(event):
            news_canvas.yview_scroll(-int(event.delta/120), 'units')
        news_canvas.bind('<MouseWheel>', _on_news_mousewheel)
        self.news_list_frame.bind('<MouseWheel>', _on_news_mousewheel)
        
        # Mouse wheel'i tüm alt widget'lara bağla (haber kartları için)
        self.news_mousewheel_callback = _on_news_mousewheel
        
        # Scroll region güncelleme
        def _on_news_frame_config(event):
            news_canvas.configure(scrollregion=news_canvas.bbox('all'))
        self.news_list_frame.bind('<Configure>', _on_news_frame_config)
        
        # Açık pozisyonlar tablosu için mouse wheel (eski kodun devamı)
        def _on_positions_mousewheel(event):
            self.positions_tree.yview_scroll(-int(event.delta/120), 'units')
        self.positions_tree.bind('<MouseWheel>', _on_positions_mousewheel)
        pos_tree_frame.bind('<MouseWheel>', _on_positions_mousewheel)
        # Hover state holders
        self._pos_row_tags = {}
        self._pos_hover_item = None
        self.positions_tree.bind('<Motion>', self._on_positions_tree_motion)
        self.positions_tree.bind('<Leave>', self._on_positions_tree_leave)
        # Sıralama
        self._init_treeview_sort(self.positions_tree, columns)
        
        
        # Log alanı kaldırıldı
    
    # setup_pnl_panel fonksiyonu kaldırıldı
    
    def setup_modern_summary_cards(self, parent):
        """Modern simetrik kutucuklar oluşturur"""
        # Ana grid container - tam genişlik
        grid_frame = tk.Frame(parent, bg='#1f2937')
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # 2x3 grid layout için satır ve sütunlar - eşit dağılım
        for i in range(2):  # 2 satır
            grid_frame.grid_rowconfigure(i, weight=1, uniform="row")
        for j in range(3):  # 3 sütun
            grid_frame.grid_columnconfigure(j, weight=1, uniform="col")
        
        # Kutucuk verileri
        cards_data = [
            {
                'title': f'💰 {self.tr("total_pnl_label")}',
                'value': '0.00 USDT',
                'icon': '📈',
                'color': '#10b981',
                'bg_color': '#064e3b',
                'row': 0, 'col': 0
            },
            {
                'title': f'💸 {self.tr("total_fee_label")}',
                'value': '0.00 USDT',
                'icon': '💳',
                'color': '#f59e0b',
                'bg_color': '#451a03',
                'row': 0, 'col': 1
            },
            {
                'title': f'📊 {self.tr("total_trades_label")}',
                'value': '0',
                'icon': '🔄',
                'color': '#3b82f6',
                'bg_color': '#1e3a8a',
                'row': 0, 'col': 2
            },
            {
                'title': f'📈 {self.tr("long_positions_label")}',
                'value': '0',
                'icon': '⬆️',
                'color': '#22c55e',
                'bg_color': '#14532d',
                'row': 1, 'col': 0
            },
            {
                'title': f'📉 {self.tr("short_positions_label")}',
                'value': '0',
                'icon': '⬇️',
                'color': '#ef4444',
                'bg_color': '#7f1d1d',
                'row': 1, 'col': 1
            },
            {
                'title': f'💎 {self.tr("total_balance_label")}',
                'value': '0.00 USDT',
                'icon': '🏦',
                'color': '#8b5cf6',
                'bg_color': '#581c87',
                'row': 1, 'col': 2
            }
        ]
        
        # Kutucukları oluştur
        self.summary_cards = {}
        for card_data in cards_data:
            card = self.create_summary_card(grid_frame, card_data)
            self.summary_cards[card_data['title']] = card
            card.grid(row=card_data['row'], column=card_data['col'], 
                     padx=4, pady=4, sticky='nsew')
    
    def create_summary_card(self, parent, card_data):
        """Tek bir kutucuk oluşturur"""
        # Ana kutucuk frame - minimum yükseklik
        card_frame = tk.Frame(parent, bg=card_data['bg_color'], relief='flat', bd=0)
        card_frame.configure(height=120)  # Minimum yükseklik
        
        # İç padding için inner frame
        inner_frame = tk.Frame(card_frame, bg=card_data['bg_color'])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # İkon ve başlık
        header_frame = tk.Frame(inner_frame, bg=card_data['bg_color'])
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        icon_label = tk.Label(header_frame, text=card_data['icon'], 
                             font=('Segoe UI', 16), 
                             bg=card_data['bg_color'], fg=card_data['color'])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_frame, text=card_data['title'], 
                              font=('Segoe UI', 10, 'bold'), 
                              bg=card_data['bg_color'], fg='#9ca3af')
        title_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Değer
        value_label = tk.Label(inner_frame, text=card_data['value'], 
                              font=('Segoe UI', 14, 'bold'), 
                              bg=card_data['bg_color'], fg='white')
        value_label.pack(fill=tk.X, pady=(0, 4))
        
        # Değişim göstergesi (opsiyonel)
        change_label = tk.Label(inner_frame, text="", 
                               font=('Segoe UI', 9), 
                               bg=card_data['bg_color'], fg='#6b7280')
        change_label.pack(fill=tk.X)
        
        # Hover efekti
        def on_enter(event):
            card_frame.config(bg='#374151')
            inner_frame.config(bg='#374151')
            header_frame.config(bg='#374151')
            icon_label.config(bg='#374151')
            title_label.config(bg='#374151')
            value_label.config(bg='#374151')
            change_label.config(bg='#374151')
        
        def on_leave(event):
            card_frame.config(bg=card_data['bg_color'])
            inner_frame.config(bg=card_data['bg_color'])
            header_frame.config(bg=card_data['bg_color'])
            icon_label.config(bg=card_data['bg_color'])
            title_label.config(bg=card_data['bg_color'])
            value_label.config(bg=card_data['bg_color'])
            change_label.config(bg=card_data['bg_color'])
        
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
        
        # Label referanslarını sakla
        card_frame.value_label = value_label
        card_frame.change_label = change_label
        
        return card_frame
    
    def setup_selected_coins_cards(self):
        """Seçilen coinlerin kutucuklarını oluşturur"""
        try:
            # Mevcut kutucukları temizle
            for widget in self.selected_coins_container.winfo_children():
                widget.destroy()
            
            # Otomatik yüzde hesaplama - seçilen coin sayısına göre eşit dağıtım
            total_coins = len(self.selected_symbols)
            
            self.log_message(f"📦 Coin kartları oluşturuluyor: {total_coins} coin")
            
            if total_coins == 0:
                self.log_message("⚠️ Seçili coin yok, kartlar oluşturulmadı")
                return
            
            # Bakiye % ayarından toplam yüzdeyi al
            try:
                total_balance_pct = float(self.balance_percent_var.get())
            except Exception:
                total_balance_pct = 100.0
            
            # Her coin için yüzde hesapla
            per_coin_pct = total_balance_pct / total_coins
            
            # Seçilen coinlerin kutucuklarını oluştur
            self.selected_coins_cards = {}
            for i, symbol in enumerate(self.selected_symbols):
                card = self.create_selected_coin_card(symbol, i, per_coin_pct)
                self.selected_coins_cards[symbol] = card
                # Kutucukları yatay olarak sırala ama dikey olarak da uzasın
                card.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
            
            self.log_message(f"✅ {total_coins} coin kartı oluşturuldu")
        except Exception as e:
            self.log_message(f"❌ Coin kartları oluşturma hatası: {e}")
            import traceback
            self.log_message(f"Detay: {traceback.format_exc()}")
    
    def create_selected_coin_card(self, symbol, index, per_coin_pct=100.0):
        """Tek bir seçilen coin kutucuğu oluşturur"""
        # Ana kutucuk frame - aşağıya doğru uzasın (yükseklik artırıldı - stop loss için)
        card_frame = tk.Frame(self.selected_coins_container, 
                             bg='#374151', 
                             relief='flat', 
                             bd=1,
                             width=180,
                             height=170)
        card_frame.pack_propagate(False)
        
        # Üst kısım - Coin adı ve çarpı butonu
        header_frame = tk.Frame(card_frame, bg='#374151')
        header_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        # Coin adı
        coin_label = tk.Label(header_frame, text=symbol, 
                             font=('Segoe UI', 12, 'bold'), 
                             bg='#374151', fg='#f9fafb')
        coin_label.pack(side=tk.LEFT)
        
        # Çarpı butonu - küçültüldü (en sağda)
        remove_btn = tk.Button(header_frame, text='×', 
                              font=('Segoe UI', 12, 'bold'),
                              bg='#ef4444', fg='white',
                              relief='flat', bd=0,
                              width=2, height=1,
                              cursor='hand2',
                              command=lambda s=symbol: self.remove_selected_coin(s))
        remove_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Header frame'in sağ tarafını da tıklanabilir yap
        def on_header_click(event):
            self.remove_selected_coin(symbol)
        
        # Orta kısım - Fiyat ve değişim %
        price_frame = tk.Frame(card_frame, bg='#374151')
        price_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Fiyat bilgisi
        price_label = tk.Label(price_frame, text='$0.00', 
                              font=('Segoe UI', 10, 'bold'), 
                              bg='#374151', fg='#f9fafb')
        price_label.pack(side=tk.LEFT)
        
        # Değişim % bilgisi
        change_percent_label = tk.Label(price_frame, text='+0.00%', 
                                       font=('Segoe UI', 9, 'bold'), 
                                       bg='#374151', fg='#22c55e')
        change_percent_label.pack(side=tk.RIGHT)
        
        # Yüzde girişi
        percent_frame = tk.Frame(card_frame, bg='#374151')
        percent_frame.pack(fill=tk.X, padx=8, pady=2)
        
        percent_label = tk.Label(percent_frame, text=self.tr('trade_percent_label'), 
                                font=('Segoe UI', 9), 
                                bg='#374151', fg='#9ca3af')
        percent_label.pack(side=tk.LEFT)
        
        # Her coin için hesaplanan yüzdeyi göster (sadece gösterim)
        percent_display = tk.Label(percent_frame, 
                                   text=f"{per_coin_pct:.2f}%",
                                   font=('Segoe UI', 11, 'bold'),
                                   bg='#374151', 
                                   fg='#22c55e',  # Yeşil renk - görünür
                                   width=8)
        percent_display.pack(side=tk.RIGHT)
        
        # Stop Loss girişi
        stop_loss_frame = tk.Frame(card_frame, bg='#374151')
        stop_loss_frame.pack(fill=tk.X, padx=8, pady=2)
        
        stop_loss_label = tk.Label(stop_loss_frame, text=f"🛑 {self.tr('stop_loss_coin_label')}", 
                                   font=('Segoe UI', 9), 
                                   bg='#374151', fg='#9ca3af')
        stop_loss_label.pack(side=tk.LEFT)
        
        # Stop Loss Entry - Varsayılan olarak global stop loss değerini kullan
        default_stop_loss = self.coin_stop_losses.get(symbol, None)
        if default_stop_loss is None:
            # Kaydedilmiş değer yoksa global stop loss'u kullan
            try:
                default_stop_loss = self.stop_loss_pct_var.get()
            except:
                default_stop_loss = "0"
        else:
            default_stop_loss = str(default_stop_loss)
        
        stop_loss_var = tk.StringVar(value=default_stop_loss)
        stop_loss_entry = tk.Entry(stop_loss_frame, 
                                   textvariable=stop_loss_var,
                                   font=('Segoe UI', 9),
                                   bg='#1f2937', 
                                   fg='#f9fafb',
                                   relief='flat',
                                   width=5,
                                   insertbackground='white')
        stop_loss_entry.pack(side=tk.RIGHT)
        
        # Stop Loss değiştiğinde kaydet
        def on_stop_loss_change(event=None):
            try:
                val = float(stop_loss_var.get())
                if val < 0:
                    val = 0
                self.coin_stop_losses[symbol] = val
                self.save_settings_file()
            except:
                pass
        
        stop_loss_entry.bind('<FocusOut>', on_stop_loss_change)
        stop_loss_entry.bind('<Return>', on_stop_loss_change)
        
        # Alt kısım - Durum yazısı (Yükseliyor/Düşüyor/Nötr) - çok daha yukarı
        status_frame = tk.Frame(card_frame, bg='#374151')
        status_frame.pack(fill=tk.X, padx=8, pady=(8, 8))
        
        # Başlangıçta "Nötr" göster
        status_label = tk.Label(status_frame, text=self.tr('neutral_text'), 
                               font=('Segoe UI', 10, 'bold'), 
                               bg='#374151', fg='#9ca3af')
        status_label.pack(side=tk.LEFT)
        
        # Sadece durum yazısı kalacak (Yükseliyor/Düşüyor/Nötr)
        # Değişim yüzdesi ve oku kaldırıldı
        
        # Hover efektleri
        def on_enter(event):
            # Mevcut renk kodlamasını koruyarak hover efekti uygula
            current_bg = card_frame.cget('bg')
            if current_bg == '#064e3b':  # Yeşil
                hover_bg = '#065f46'
            elif current_bg == '#7f1d1d':  # Kırmızı
                hover_bg = '#991b1b'
            else:  # Gri
                hover_bg = '#4b5563'
            
            card_frame.config(bg=hover_bg)
            header_frame.config(bg=hover_bg)
            price_frame.config(bg=hover_bg)
            percent_frame.config(bg=hover_bg)
            stop_loss_frame.config(bg=hover_bg)
            status_frame.config(bg=hover_bg)
            coin_label.config(bg=hover_bg)
            price_label.config(bg=hover_bg)
            change_percent_label.config(bg=hover_bg)
            percent_label.config(bg=hover_bg)
            percent_display.config(bg=hover_bg)
            stop_loss_label.config(bg=hover_bg)
            status_label.config(bg=hover_bg)
        
        def on_leave(event):
            # Orijinal renk kodlamasına geri dön
            # Bu fonksiyon update_selected_coins_cards tarafından güncellenecek
            pass
        
        # Hover event'lerini bağla
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
        
        # Card objesini döndür (güncelleme için gerekli)
        card_frame.percent_display = percent_display
        card_frame.header_frame = header_frame
        card_frame.price_frame = price_frame
        card_frame.percent_frame = percent_frame
        card_frame.stop_loss_frame = stop_loss_frame
        card_frame.status_frame = status_frame
        card_frame.coin_label = coin_label
        card_frame.price_label = price_label
        card_frame.change_percent_label = change_percent_label
        card_frame.percent_label = percent_label
        card_frame.stop_loss_label = stop_loss_label
        card_frame.stop_loss_entry = stop_loss_entry
        card_frame.status_label = status_label
        
        return card_frame
    
    def remove_selected_coin(self, symbol):
        """Seçilen coini listeden çıkarır"""
        if symbol in self.selected_symbols:
            self.selected_symbols.remove(symbol)
            self.update_selected_count_label()
            self.setup_selected_coins_cards()  # Kutucukları yenile (otomatik yüzde hesaplama ile)
            self.update_selected_coins_cards()  # Verileri güncelle
            self.log_message(self.tr('coin_removed').format(symbol=symbol))
    
    def update_selected_coins_cards(self):
        """Seçilen coinlerin kutucuklarını günceller - momentum tabanlı"""
        if not hasattr(self, 'selected_coins_cards'):
            return
        
        try:
            # Önceki değerleri saklamak için gerekli
            if not hasattr(self, 'previous_changes'):
                self.previous_changes = {}
            
            # latest_changes verilerini kontrol et; yoksa erken çık
            if not (hasattr(self, 'latest_changes') and self.latest_changes):
                # Veri kaynağı yoksa kartları varsayılan hâlde bırak
                return
            
            # Throttling kaldırıldı - artık interval süresine göre çalışıyor

            # Her coin için değişim durumunu güncelle (sadece değişenleri paint et)
            for symbol, card in self.selected_coins_cards.items():
                # Card güvenlik kontrolü
                if card is None:
                    self.log_message(f"⚠️ Kart bulunamadı: {symbol}")
                    continue
                    
                # Aday semboller: orijinal, base+USDT, base+USDC (bazı çiftler USDC'dedir)
                base = self.get_base_symbol_from_binance(symbol)
                candidate_symbols = [symbol, base + 'USDT', base + 'USDC']
                sym = candidate_symbols[0]
                
                if hasattr(self, 'latest_changes') and self.latest_changes:
                    
                    # BNB için özel kontrol
                    if symbol == 'BNBUSDT' and sym not in self.latest_changes:
                        # BNB farklı sembollerle denenebilir
                        alternative_symbols = ['BNBUSDT', 'BNB', 'BNBUSD']
                        for alt_sym in alternative_symbols:
                            if alt_sym in self.latest_changes:
                                sym = alt_sym
                                break
                    
                # latest_changes içinde bulunan ilk adayı seç
                resolved = None
                if hasattr(self, 'latest_changes') and self.latest_changes:
                    for cand in candidate_symbols:
                        if cand in self.latest_changes:
                            resolved = cand
                            break
                
                if resolved is not None:
                    sym = resolved
                    current_change = float(self.latest_changes[sym])
                    
                    # Önceki değeri al
                    previous_change = self.previous_changes.get(symbol, current_change)
                    
                    # Momentum hesapla (şimdiki - önceki)
                    momentum = current_change - previous_change
                    
                    # Önceki değeri güncelle
                    self.previous_changes[symbol] = current_change
                    
                    # Fiyat ve değişim %'sini güncelle
                    try:
                        # Fiyat için de sembol eşleştirme yap
                        price = None
                        if hasattr(self, 'latest_prices') and self.latest_prices:
                            # Aynı candidate_symbols ile ara
                            for price_sym in [symbol, sym, base + 'USDT', base + 'USDC']:
                                if price_sym in self.latest_prices:
                                    price = self.latest_prices.get(price_sym)
                                    break
                        
                        # Hala yoksa API'den çek
                        if price is None and hasattr(self, 'client') and self.client:
                            try:
                                fticker = self.client.futures_symbol_ticker(symbol=symbol)
                                price = float(fticker['price'])
                                # Cache'e kaydet
                                self.latest_prices[symbol] = price
                            except Exception:
                                pass
                        
                        if price is not None and hasattr(card, 'price_label') and card.price_label is not None:
                            prev_price_txt = card.price_label.cget('text')
                            # Bindelik ayraçlı fiyat formatı
                            new_price_txt = f"${price:,.4f}" if price >= 1 else f"${price:.8f}"
                            if prev_price_txt != new_price_txt:
                                card.price_label.config(text=new_price_txt)
                    except Exception as e:
                        # Fiyat güncellenemiyor, sessizce devam et
                        pass
                    
                    # Değişim %'sini güncelle (24 saatlik)
                    if hasattr(card, 'change_percent_label') and card.change_percent_label is not None:
                        change_text = f"{current_change:+.2f}%"
                        card.change_percent_label.config(text=change_text)
                    
                    # Momentum tabanlı renk kodlaması - tüm kutucuğa yansıt
                    try:
                        if momentum > 0.1:  # Momentum pozitif (yükseliş hızlanıyor)
                            # Yükseliş momentumu - yeşil
                            bg_color = '#064e3b'
                            fg_color = '#f9fafb'
                            status_text = self.tr('rising_text')
                            status_color = '#22c55e'
                            change_color = '#22c55e'
                        elif momentum < -0.1:  # Momentum negatif (düşüş hızlanıyor)
                            # Düşüş momentumu - kırmızı
                            bg_color = '#7f1d1d'
                            fg_color = '#f9fafb'
                            status_text = self.tr('falling_text')
                            status_color = '#ef4444'
                            change_color = '#ef4444'
                        else:
                            # Nötr momentum - gri
                            bg_color = '#374151'
                            fg_color = '#f9fafb'
                            status_text = self.tr('neutral_text')
                            status_color = '#9ca3af'
                            change_color = '#9ca3af'
                        
                        # Renkleri güvenli şekilde uygula
                        card.config(bg=bg_color)
                        if hasattr(card, 'header_frame'): card.header_frame.config(bg=bg_color)
                        if hasattr(card, 'price_frame'): card.price_frame.config(bg=bg_color)
                        if hasattr(card, 'percent_frame'): card.percent_frame.config(bg=bg_color)
                        if hasattr(card, 'stop_loss_frame'): card.stop_loss_frame.config(bg=bg_color)
                        if hasattr(card, 'status_frame'): card.status_frame.config(bg=bg_color)
                        if hasattr(card, 'coin_label'): card.coin_label.config(bg=bg_color, fg=fg_color)
                        if hasattr(card, 'price_label'): card.price_label.config(bg=bg_color, fg=fg_color)
                        if hasattr(card, 'change_percent_label'): card.change_percent_label.config(bg=bg_color, fg=change_color)
                        if hasattr(card, 'percent_label'): card.percent_label.config(bg=bg_color, fg='#9ca3af')
                        if hasattr(card, 'stop_loss_label'): card.stop_loss_label.config(bg=bg_color, fg='#9ca3af')
                        if hasattr(card, 'status_label'): card.status_label.config(text=status_text, fg=status_color, bg=bg_color)
                    except Exception:
                        pass  # Renk güncellemesi başarısız, devam et
                else:
                    # Veri bulunamadığında varsayılan değerler (Nötr olarak göster)
                    # Debug: Hangi sembol bulunamadı? (sadece ilk kez logla)
                    if not hasattr(self, '_logged_missing_symbols'):
                        self._logged_missing_symbols = set()
                    if symbol not in self._logged_missing_symbols:
                        self.log_message(f"⚠️ Veri bulunamadı: {symbol} (Denenen: {candidate_symbols})")
                        self._logged_missing_symbols.add(symbol)
                    
                    # Veri yoksa Nötr olarak göster
                    try:
                        if hasattr(card, 'status_label') and card.status_label:
                            card.status_label.config(text=self.tr('neutral_text'), fg='#9ca3af')
                        if hasattr(card, 'price_label') and card.price_label:
                            card.price_label.config(text='--.--')
                        if hasattr(card, 'change_percent_label') and card.change_percent_label:
                            card.change_percent_label.config(text='+0.00%')
                    except Exception:
                        pass
                    
        except Exception as e:
            self.log_message(f"Seçilen coinler güncelleme hatası: {e}")
        
    # update_pnl_panel fonksiyonu kaldırıldı
    
    def fetch_account_summary_data(self):
        """Binance API'den hesap özet verilerini çeker"""
        if not self.client:
            return None
        
        try:
            # Timestamp ve bağlantı hatalarını önlemek için retry mekanizması
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Hesap bilgileri
                    # Paylaşımlı önbellek: 2 sn (sürekli güncel - minimum gecikme)
                    import time
                    now = time.time()
                    cache_expired = now - self._cache_account['ts'] > 2
                    if cache_expired or not self._cache_account['data']:
                        account_info = self.client.futures_account()
                        self._cache_account = {'ts': now, 'data': account_info}
                        # Log sadece değişiklik olduğunda (sessiz mod)
                    else:
                        account_info = self._cache_account['data']
                    break
                except Exception as e:
                    error_str = str(e)
                    # Geçici hatalar: Timestamp, ConnectionError, ProtocolError
                    is_retryable = ("Timestamp" in error_str or 
                                   "Connection" in error_str or 
                                   "Remote" in error_str or
                                   "Timeout" in error_str)
                    
                    if is_retryable and attempt < max_retries - 1:
                        self.log_message(f"Geçici API hatası, tekrar deneniyor... (Deneme {attempt + 1}/{max_retries})")
                        import time
                        # Bekleme süresi: 1, 2, 3 saniye
                        time.sleep(attempt + 1)
                        continue
                    else:
                        raise e
            
            # Pozisyonlar
            for attempt in range(max_retries):
                try:
                    pos_cache_expired = now - self._cache_positions['ts'] > 1
                    if pos_cache_expired or not self._cache_positions['data']:
                        positions = self.client.futures_position_information()
                        self._cache_positions = {'ts': now, 'data': positions}
                        # Sessiz mod - pozisyonlar çok sık güncellenir
                    else:
                        positions = self._cache_positions['data']
                    break
                except Exception as e:
                    error_str = str(e)
                    is_retryable = ("Timestamp" in error_str or 
                                   "Connection" in error_str or 
                                   "Remote" in error_str or
                                   "Timeout" in error_str)
                    
                    if is_retryable and attempt < max_retries - 1:
                        self.log_message(f"Pozisyonlar için geçici hata, tekrar deneniyor... (Deneme {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(attempt + 1)
                        continue
                    else:
                        raise e
            
            # İşlem geçmişi kaldırıldı - Sadece 5 dakikada bir cache'li versiyonu kullanılacak
            # Bu çağrı gereksizdi ve symbol parametresi olmadığı için yavaştı
            trades = getattr(self, '_last_trades_cache', [])
            
            # Verileri işle
            summary_data = self.process_summary_data(account_info, positions, trades)
            return summary_data
            
        except Exception as e:
            self.log_message(f"Hesap verisi çekme hatası: {e}")
            import traceback
            self.log_message(f"Detaylı hata: {traceback.format_exc()}")
            return None
    
    def process_summary_data(self, account_info, positions, trades):
        """Hesap verilerini işleyerek özet verileri oluşturur"""
        try:
            # Toplam bakiye - farklı alanları dene
            total_balance = 0.0
            try:
                # Farklı bakiye alanlarını dene
                balance_fields = ['totalWalletBalance', 'totalMarginBalance', 'totalCrossWalletBalance', 'totalInitialMargin', 'availableBalance', 'maxWithdrawAmount']
                total_balance = 0.0
                
                for field in balance_fields:
                    if field in account_info:
                        field_value = float(account_info.get(field, 0.0))
                        if field_value > 0:
                            total_balance = field_value
                            break
                
                if total_balance == 0.0:
                    # Alternatif bakiye hesaplama
                    if 'assets' in account_info:
                        for asset in account_info['assets']:
                            asset_name = asset.get('asset', '')
                            wallet_balance = float(asset.get('walletBalance', 0.0))
                            if asset_name in ('USDT', 'USDC', 'BUSD', 'FDUSD', 'TUSD'):
                                total_balance += wallet_balance
            except Exception as e:
                self.log_message(f"Özet kartları - Bakiye hesaplama hatası: {e}")
            
            # Son fallback: Spot cüzdan bakiyesini kontrol et
            if total_balance == 0.0:
                try:
                    spot_account = self.client.get_account()
                    spot_balance = 0.0
                    for balance in spot_account.get('balances', []):
                        asset_name = balance.get('asset', '')
                        free_balance = float(balance.get('free', 0.0))
                        locked_balance = float(balance.get('locked', 0.0))
                        total_spot_balance = free_balance + locked_balance
                        if asset_name in ('USDT','USDC','BUSD','FDUSD','TUSD') and total_spot_balance > 0:
                            spot_balance += total_spot_balance
                    if spot_balance > 0:
                        total_balance = spot_balance
                except Exception as e:
                    pass  # Sessizce devam et
            
            # Toplam PNL (realized + unrealized)
            total_unrealized_pnl = 0.0
            total_realized_pnl = 0.0
            try:
                total_unrealized_pnl = float(account_info.get('totalUnrealizedProfit', 0.0))
                total_realized_pnl = float(account_info.get('totalRealizedProfit', 0.0))
            except Exception as e:
                self.log_message(f"PNL hesaplama hatası: {e}")
            
            # Geçmiş işlemlerden toplam FEE ve İŞLEM SAYISI hesapla
            # NOT: Trade History kullan, Income History değil!
            # ⚡ PERFORMANS: 5 dakikada bir yenile (çok sık çekmek UI'yi donduruyor!)
            total_fee = 0.0
            total_trades_count = 0
            all_trades = []
            
            # Cache kontrolü - 5 dakikada bir yenile
            import time as _t_cache
            cache_ttl = 300  # 5 dakika = 300 saniye
            cache_expired = _t_cache.time() - getattr(self, '_last_fee_calc_ts', 0.0) > cache_ttl
            
            if cache_expired:
                try:
                    # Son 7 gün için trade history çek (SADECE AÇIK POZİSYONLAR)
                    from datetime import datetime, timedelta
                    end_time = int(datetime.now().timestamp() * 1000)
                    start_time = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
                    
                    # SADECE açık pozisyonu olan sembolleri al (PERFORMANS!)
                    active_symbols = set()
                    for pos in positions:
                        position_amt = float(pos.get('positionAmt', 0))
                        if position_amt != 0:
                            active_symbols.add(pos['symbol'])
                    
                    # Eğer açık pozisyon yoksa, en son trade yapılan 10 sembolü kontrol et
                    if not active_symbols:
                        exchange_info = self.client.futures_exchange_info()
                        all_symbols = [s['symbol'] for s in exchange_info.get('symbols', []) if s['symbol'].endswith('USDT')]
                        active_symbols = set(all_symbols[:10])  # İlk 10 sembol (hızlı başlangıç)
                    
                    self.log_message(f"📊 Trade history çekiliyor... ({len(active_symbols)} aktif sembol)")
                    
                    # Her sembol için trade history çek
                    unique_order_ids = set()
                    symbol_count = 0
                    
                    for symbol in active_symbols:
                        try:
                            symbol_trades = self.client.futures_account_trades(
                                symbol=symbol,
                                startTime=start_time,
                                endTime=end_time,
                                limit=1000
                            )
                            
                            if symbol_trades:
                                symbol_count += 1
                                all_trades.extend(symbol_trades)
                                
                                # Fee ve order ID'leri topla
                                for trade in symbol_trades:
                                    commission = float(trade.get('commission', 0.0))
                                    total_fee += abs(commission)
                                    
                                    order_id = trade.get('orderId', None)
                                    if order_id:
                                        unique_order_ids.add(order_id)
                        
                        except Exception as e:
                            # Symbol için veri yoksa sessizce geç
                            pass
                    
                    # İşlem sayısı = Unique order ID sayısı
                    total_trades_count = len(unique_order_ids)
                    
                    # Cache'e kaydet
                    self._last_fee_calc_ts = _t_cache.time()
                    self._cached_total_fee = total_fee
                    self._cached_total_trades = total_trades_count
                    
                    self.log_message(f"✅ Trade history: {total_trades_count} işlem, {total_fee:.2f} USDT komisyon (son 7 gün, {symbol_count} sembol)")
                    
                except Exception as e:
                    self.log_message(f"❌ Trade history hatası: {e}")
                    # Hata olursa eski değerleri kullan
                    total_fee = getattr(self, '_cached_total_fee', 0.0)
                    total_trades_count = getattr(self, '_cached_total_trades', 0)
            else:
                # Cache'den oku (5 dakika dolmadı, yeniden çekme!)
                total_fee = getattr(self, '_cached_total_fee', 0.0)
                total_trades_count = getattr(self, '_cached_total_trades', 0)
            
            # Toplam PNL = Account'tan gelen değerler (Binance'in kendi hesaplaması)
            # totalRealizedProfit: Tüm zamanların realized PNL'i
            # totalUnrealizedProfit: Şu anki açık pozisyonların PNL'i
            total_pnl = total_unrealized_pnl + total_realized_pnl
            
            # Long ve Short pozisyon sayıları
            long_positions = 0
            short_positions = 0
            try:
                for pos in positions:
                    position_amt = float(pos.get('positionAmt', 0))
                    if position_amt > 0:
                        long_positions += 1
                    elif position_amt < 0:
                        short_positions += 1
            except Exception as e:
                self.log_message(f"Pozisyon sayma hatası: {e}")
            
            result = {
                'total_balance': total_balance,
                'total_pnl': total_pnl,
                'total_fee': total_fee,
                'total_trades': total_trades_count,
                'long_positions': long_positions,
                'short_positions': short_positions,
                'unrealized_pnl': total_unrealized_pnl,
                'realized_pnl': total_realized_pnl
            }
            
            return result
            
        except Exception as e:
            self.log_message(f"Veri işleme hatası: {e}")
            import traceback
            self.log_message(f"Detaylı hata: {traceback.format_exc()}")
            return None
    
    def update_summary_cards(self, summary_data=None):
        """Özet kutucuklarını günceller"""
        if not hasattr(self, 'summary_cards'):
            return
        
        # Manuel yenileme mi yoksa otomatik güncelleme mi?
        is_manual = summary_data is not None
        
        if summary_data is None:
            if not self.client:
                return
            # Otomatik güncelleme - sessiz çalış (fazla log yazma)
            summary_data = self.fetch_account_summary_data()
        
        if not summary_data:
            # Varsayılan değerler
            summary_data = {
                'total_balance': 0.0,
                'total_pnl': 0.0,
                'total_fee': 0.0,
                'total_trades': 0,
                'long_positions': 0,
                'short_positions': 0
            }
        
        try:
            # Kutucukları güncelle (bindelik ayraçlı)
            cards_to_update = {
                f'💰 {self.tr("total_pnl_label")}': f"{summary_data['total_pnl']:,.2f} USDT",
                f'💸 {self.tr("total_fee_label")}': f"{summary_data['total_fee']:,.2f} USDT",
                f'📊 {self.tr("total_trades_label")}': f"{summary_data['total_trades']:,}",
                f'📈 {self.tr("long_positions_label")}': f"{summary_data['long_positions']:,}",
                f'📉 {self.tr("short_positions_label")}': f"{summary_data['short_positions']:,}",
                f'💎 {self.tr("total_balance_label")}': f"{summary_data['total_balance']:,.2f} USDT"
            }
            
            # Batch UI güncelleme için kuyruğa ekle
            for card_title, new_value in cards_to_update.items():
                if card_title in self.summary_cards:
                    # Sadece değer değiştiyse kuyruğa ekle
                    if self._last_card_values.get(card_title) != new_value:
                        self._ui_update_queue.append((card_title, new_value))
                        self._last_card_values[card_title] = new_value
            
            # UI güncellemelerini batch halinde uygula
            self._apply_batch_ui_updates()
            
        except Exception as e:
            self.log_message(f"Özet kutucukları güncelleme hatası: {e}")
            import traceback
            self.log_message(f"Detaylı hata: {traceback.format_exc()}")
    
    def _apply_batch_ui_updates(self):
        """UI güncellemelerini batch halinde uygula"""
        if not self._ui_update_queue:
            return
            
        try:
            for card_title, new_value in self._ui_update_queue:
                if card_title in self.summary_cards:
                    card = self.summary_cards[card_title]
                    card.value_label.config(text=new_value)
                    
                    # PNL için renk değişimi
                    if card_title == '💰 Toplam PNL':
                        pnl_value = float(new_value.split()[0].replace(',', ''))
                        if pnl_value > 0:
                            card.value_label.config(fg='#22c55e')
                        elif pnl_value < 0:
                            card.value_label.config(fg='#ef4444')
                        else:
                            card.value_label.config(fg='white')
                    
                    # Bakiye için renk değişimi
                    elif card_title == f'💎 {self.tr("total_balance_label")}':
                        balance_value = float(new_value.split()[0].replace(',', ''))
                        if balance_value > 1000:
                            card.value_label.config(fg='#22c55e')
                        elif balance_value > 100:
                            card.value_label.config(fg='#f59e0b')
                        else:
                            card.value_label.config(fg='#ef4444')
            
            # Kuyruğu temizle
            self._ui_update_queue.clear()
            
        except Exception as e:
            self.log_message(f"Batch UI güncelleme hatası: {e}")
    
    def manual_refresh_summary(self):
        """Manuel olarak özet kutucuklarını yeniler"""
        self.log_message("📊 Manuel özet yenileme başlatılıyor...")
        
        # API client kontrolü
        if not self.client:
            self.log_message("❌ API bağlantısı yok! Önce API'ye bağlanın.")
            messagebox.showwarning(
                self.tr('error'),
                "API bağlantısı yok!\n\nÖnce API Key ve Secret girerek bağlantı kurun."
            )
            return
        
        try:
            # Buton görsel geri bildirimi
            original_text = self.refresh_summary_btn.cget('text')
            self.refresh_summary_btn.config(text=f"🔄 {self.tr('refreshing')}")
            self.refresh_summary_btn.config(state='disabled')
            
            # Manuel yenileme için TÜM cache'leri tamamen temizle
            self._cache_account = {'ts': 0.0, 'data': None}
            self._cache_positions = {'ts': 0.0, 'data': None}
            self._last_trades_fetch_ts = 0.0
            self._last_income_fetch_ts = 0.0
            self._last_trades_cache = None
            self._last_income_cache = None
            
            # Son değerleri de temizle (UI'ı zorla güncelle)
            self._last_card_values.clear()
            
            self.log_message("🔄 Cache tamamen temizlendi, API'den yeni veriler çekiliyor...")
            
            # Thread'de çalıştır (UI bloke olmasın)
            def restore_button():
                self.refresh_summary_btn.config(text=original_text)
                self.refresh_summary_btn.config(state='normal')
            
            self._manual_refresh_restore_callback = restore_button
            threading.Thread(target=self._refresh_summary_thread, daemon=True).start()
        except Exception as e:
            self.log_message(f"❌ Manuel yenileme hatası: {e}")
            import traceback
            self.log_message(f"Detaylı hata: {traceback.format_exc()}")
            # Butonu geri getir
            try:
                self.refresh_summary_btn.config(state='normal')
            except:
                pass
    
    def _refresh_summary_thread(self):
        """Thread'de çalışan özet yenileme fonksiyonu"""
        try:
            self.log_message("📡 API'den hesap verileri çekiliyor...")
            summary_data = self.fetch_account_summary_data()
            
            if summary_data:
                self.log_message(f"✅ Veriler alındı! Bakiye: {summary_data.get('total_balance', 0):.2f} USDT, PNL: {summary_data.get('total_pnl', 0):.2f} USDT")
                # UI thread'de güncelle
                self.root.after(0, lambda: self.update_summary_cards(summary_data))
                self.root.after(0, lambda: self.log_message("✅ Özet kutucukları güncellendi!"))
                
                # Butonu geri getir
                if hasattr(self, '_manual_refresh_restore_callback'):
                    self.root.after(0, self._manual_refresh_restore_callback)
                    delattr(self, '_manual_refresh_restore_callback')
            else:
                self.log_message("⚠️ API'den veri alınamadı!")
                self.root.after(0, lambda: messagebox.showwarning(
                    self.tr('error'),
                    "Hesap verileri alınamadı!\n\nAPI bağlantınızı ve izinlerinizi kontrol edin."
                ))
                
                # Butonu geri getir
                if hasattr(self, '_manual_refresh_restore_callback'):
                    self.root.after(0, self._manual_refresh_restore_callback)
                    delattr(self, '_manual_refresh_restore_callback')
            
        except Exception as e:
            self.log_message(f"❌ Thread yenileme hatası: {e}")
            import traceback
            self.log_message(f"Detaylı hata: {traceback.format_exc()}")
            self.root.after(0, lambda err=str(e): messagebox.showerror(
                self.tr('error'),
                f"Özet yenileme hatası:\n\n{err}"
            ))
            
            # Butonu geri getir (hata durumunda da)
            if hasattr(self, '_manual_refresh_restore_callback'):
                self.root.after(0, self._manual_refresh_restore_callback)
                delattr(self, '_manual_refresh_restore_callback')
    
    def start_summary_monitor(self):
        """Hesap özeti sürekli güncelleme thread'ini başlat"""
        if self.summary_thread_running:
            return
        
        self.summary_thread_running = True
        self.summary_thread = threading.Thread(target=self.summary_monitor_loop, daemon=True)
        self.summary_thread.start()
        self.log_message("✅ Hesap özeti sürekli güncelleme başlatıldı (5 saniye aralık - optimize)")
    
    def stop_summary_monitor(self):
        """Hesap özeti sürekli güncelleme thread'ini durdur"""
        self.summary_thread_running = False
        self.log_message("⏹️ Hesap özeti sürekli güncelleme durduruldu")
    
    def summary_monitor_loop(self):
        """Hesap özetini sürekli günceller - her 5 saniyede bir (performans optimize)"""
        while self.summary_thread_running:
            try:
                if self.client:
                    # Cache'leri kontrol et ve süresi dolmuşsa temizle
                    # Böylece fetch_account_summary_data otomatik olarak yeni veri çeker
                    import time as _t
                    now = _t.time()
                    
                    # Hesap ve pozisyon cache'ini zorla süresi doldur (2 saniye cache)
                    if now - self._cache_account['ts'] > 2:
                        self._cache_account = {'ts': 0.0, 'data': None}
                    if now - self._cache_positions['ts'] > 1:
                        self._cache_positions = {'ts': 0.0, 'data': None}
                    
                    # UI thread'de güncelle
                    self.root.after(0, self.update_summary_cards)
                
                # 5 saniye bekle (performans optimizasyonu)
                time.sleep(5)
            except Exception as e:
                self.log_message(f"Hesap özeti güncelleme hatası: {e}")
                time.sleep(10)
    
    def log_message(self, message):
        # Basit konsol log - UI kaldırıldı
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Konsol çıktısı (Unicode güvenli)
        try:
            print(log_entry)
        except UnicodeEncodeError:
            safe_message = message.encode('ascii', 'ignore').decode('ascii')
            print(f"[{timestamp}] {safe_message}")

    # _flush_log_ui_batch fonksiyonu kaldırıldı
    
    def fmt_price(self, value, decimals: int = 4) -> str:
        try:
            s = f"{float(value):,.{decimals}f}"
            # Türkçe için nokta/binlik, virgül/ondalık dönüşümü
            try:
                lang = (self.lang_var.get() or '').split(' - ')[0]
            except Exception:
                lang = 'tr'
            if lang == 'tr':
                s = s.replace(',', '§').replace('.', ',').replace('§', '.')
            return s
        except Exception:
            return str(value)
    
    def save_config(self):
        # Her zaman giriş alanlarından oku (bağlanmadan önce de kaydedilsin)
        try:
            api_key = self.api_key_entry.get().strip()
            api_secret = self.api_secret_entry.get().strip()
        except Exception:
            api_key = getattr(self, 'api_key', '')
            api_secret = getattr(self, 'api_secret', '')
        env = self.env_code() if hasattr(self, 'env_code') else ('test' if (self.env_var.get() == 'Test') else 'live')
        try:
            save_config_env(env, api_key, api_secret, path='config.json')
        except Exception as e:
            self.log_message(f"Config kaydetme hatası: {e}")
    
    def load_config(self):
        try:
            cfg = load_config_all(path='config.json')
            self._api_cfg_all = cfg
            # Mevcut ortama uygun alanları doldur
            self._apply_api_fields_for_env()
        except Exception as e:
            self.log_message(f"Config yükleme hatası: {e}")
    
    def connect_api(self):
        # Eğer zaten bağlıysa, bağlantıyı kopar
        if hasattr(self, 'client') and self.client:
            self.disconnect_api()
            return
            
        self.api_key = self.api_key_entry.get().strip()
        self.api_secret = self.api_secret_entry.get().strip()
        # Kullanıcı bağlan'a bastığında, bağlantı başarılı olmasa bile anahtarları kaydet
        self.save_config()
        
        if not self.api_key or not self.api_secret:
            # Butonu kırmızı tut
            self.connect_btn.config(text=f"🔌 {self.tr('connect_btn_text')}", style='Connect.Disconnected.TButton')
            messagebox.showerror(self.tr('error'), self.tr('api_keys_required'))
            return
        
        try:
            use_testnet = (self.env_var.get() == self.tr('env_test'))
            self.client = make_client(self.api_key, self.api_secret, use_testnet)
            
            # Futures testnet URL ayarı
            if use_testnet:
                # python-binance futures testnet desteklemesi için URL override
                self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi/v1'
            
            # Test connection
            account_info = self.client.futures_account()
            # Hesap bilgilerini detaylı logla
            self.log_message(f"Hesap bilgisi alanları: {list(account_info.keys())}")
            
            # Test modu durumunu güncelle
            self.update_test_mode_status()
            self.log_message(f"Hesap bilgisi örneği: {str(account_info)[:500]}...")
            # Toplam cüzdan bakiyesi (USD) -> daha güvenilir alan
            try:
                # Farklı bakiye alanlarını dene
                balance_fields = ['totalWalletBalance', 'totalMarginBalance', 'totalCrossWalletBalance', 'totalInitialMargin', 'availableBalance', 'maxWithdrawAmount']
                self.balance = 0.0
                
                for field in balance_fields:
                    if field in account_info:
                        field_value = float(account_info.get(field, 0.0))
                        self.log_message(f"{field}: {field_value}")
                        if field_value > 0:
                            self.balance = field_value
                            self.log_message(f"Bakiye bulundu: {field} = {field_value}")
                            break
                
                if self.balance == 0.0:
                    self.log_message("Hiçbir bakiye alanında değer bulunamadı")
                    
            except Exception as e:
                self.balance = 0.0
                self.log_message(f"Bakiye alanları kontrol hatası: {e}")
            
            # Eğer 0 görünüyorsa USDT/USDC gibi varlıkları toplayarak deneyelim (geriye dönük)
            try:
                if self.balance == 0.0 and 'assets' in account_info:
                    total = 0.0
                    self.log_message(f"Assets bulundu, sayısı: {len(account_info['assets'])}")
                    for a in account_info['assets']:
                        asset_name = a.get('asset', '')
                        wallet_balance = float(a.get('walletBalance', 0.0))
                        if asset_name in ('USDT', 'USDC', 'BUSD', 'FDUSD', 'TUSD'):
                            total += wallet_balance
                            self.log_message(f"Asset {asset_name}: {wallet_balance}")
                    if total > 0:
                        self.balance = total
                        self.log_message(f"Assets'den toplam bakiye: {total}")
                else:
                    self.log_message(f"Assets bulunamadı veya bakiye zaten 0 değil")
            except Exception as e:
                self.log_message(f"Assets hesaplama hatası: {e}")
            
            # Ek fallback: futures_account_balance ile bakiyeleri topla
            try:
                bals = self.client.futures_account_balance()
                tot2 = 0.0
                self.log_message(f"futures_account_balance sonucu: {len(bals) if bals else 0} varlık")
                for b in bals or []:
                    asset_name = b.get('asset', '')
                    balance_val = float(b.get('balance', b.get('availableBalance', 0.0)))
                    if asset_name in ('USDT','USDC','BUSD','FDUSD','TUSD'):
                        tot2 += balance_val
                        self.log_message(f"Futures balance {asset_name}: {balance_val}")
                if tot2 > 0:
                    self.balance = tot2
                    self.log_message(f"Futures'dan toplam bakiye: {tot2}")
            except Exception as e:
                self.log_message(f"Futures balance hatası: {e}")
            
            # Son fallback: Spot cüzdan bakiyesini kontrol et
            if self.balance == 0.0:
                try:
                    spot_account = self.client.get_account()
                    spot_balance = 0.0
                    self.log_message(f"Spot cüzdan kontrol ediliyor...")
                    for balance in spot_account.get('balances', []):
                        asset_name = balance.get('asset', '')
                        free_balance = float(balance.get('free', 0.0))
                        locked_balance = float(balance.get('locked', 0.0))
                        total_spot_balance = free_balance + locked_balance
                        if asset_name in ('USDT','USDC','BUSD','FDUSD','TUSD') and total_spot_balance > 0:
                            spot_balance += total_spot_balance
                            self.log_message(f"Spot balance {asset_name}: {total_spot_balance} (free: {free_balance}, locked: {locked_balance})")
                    if spot_balance > 0:
                        self.balance = spot_balance
                        self.log_message(f"Spot cüzdan'dan toplam bakiye: {spot_balance}")
                except Exception as e:
                    self.log_message(f"Spot cüzdan kontrol hatası: {e}")
            
            env_name = self.tr('env_test') if use_testnet else self.tr('env_live')
            if self.connection_label:
                self.connection_label.config(text=self.tr('connected_fmt').format(env=env_name), foreground="green")
            if self.balance_label:
                self.balance_label.config(text=f"Balance: ${self.balance:,.2f}")
            
            # Butonu yeşil yap ve metni güncelle
            self.connect_btn.config(text=f"🔌 {self.tr('disconnect')}", style='Connect.Connected.TButton')
            
            self.log_message("Binance Futures API'ye başarıyla bağlandı!")
            self.save_config()
            
            # İlk fiyat ve değişimleri hemen çek (async - kullanıcıyı bekleme)
            threading.Thread(target=self.fetch_initial_market_data, daemon=True).start()
            
            # Özet kutucuklarını hemen güncelle
            self.root.after(0, self.update_summary_cards)
            
            # Market monitor'ı başlat (eğer çalışmıyorsa)
            if not hasattr(self, 'market_thread') or not self.market_thread_running:
                self.start_market_monitor()
            
            # ✅ Hesap özeti sürekli güncelleme thread'ini başlat (her 3 saniye)
            self.start_summary_monitor()
            
            # Start price updates
            self.start_price_updates()
            
            # İlk başlatımda geçmiş işlemleri de çek
            # Geçmiş işlemler alanı kaldırıldı
            
        except Exception as e:
            # Butonu kırmızı tut ve metni güncelle
            self.connect_btn.config(text="🔌 Bağlan", style='Connect.Disconnected.TButton')
            messagebox.showerror("API Hata", f"Bağlantı hatası: {str(e)}")
            self.log_message(f"API bağlantı hatası: {e}")
    
    def fetch_initial_market_data(self):
        """API'ye bağlanır bağlanmaz sadece seçilen coinler için fiyat çek (hızlı)"""
        try:
            if not self.selected_symbols:
                self.log_message("Seçili coin yok, ilk veri çekme atlandı")
                return
                
            self.log_message(f"İlk fiyatlar çekiliyor: {len(self.selected_symbols)} coin...")
            
            # Sadece seçilen coinler için fiyatları hızlıca çek
            if not hasattr(self, 'latest_prices'):
                self.latest_prices = {}
            if not hasattr(self, 'latest_changes'):
                self.latest_changes = {}
            
            for symbol in self.selected_symbols:
                try:
                    # Fiyatı çek
                    ticker = self.client.futures_symbol_ticker(symbol=symbol)
                    price = float(ticker['price'])
                    self.latest_prices[symbol] = price
                    
                    # 1 saatlik değişimi çek (kline)
                    url = "https://fapi.binance.com/fapi/v1/klines"
                    params = {
                        'symbol': symbol,
                        'interval': '1h',
                        'limit': 2
                    }
                    resp = self.session.get(url, params=params, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        if len(data) >= 2:
                            current_close = float(data[1][4])
                            previous_close = float(data[0][4])
                            change_percent = ((current_close - previous_close) / previous_close) * 100
                            self.latest_changes[symbol] = change_percent
                    
                except Exception as e:
                    self.log_message(f"Fiyat çekme hatası {symbol}: {e}")
                    continue
            
            self.log_message(f"İlk fiyatlar alındı: {len(self.latest_prices)} coin")
            # UI'de seçilen coinlerin kartlarını güncelle
            self.root.after(0, self.update_selected_coins_cards)
                
        except Exception as e:
            self.log_message(f"İlk veri çekme hatası: {e}")
    
    def disconnect_api(self):
        """API bağlantısını kopar"""
        try:
            # Client'ı temizle
            self.client = None
            
            # UI'yi güncelle
            self.connect_btn.config(text=f"🔌 {self.tr('connect_btn_text')}", style='Connect.Disconnected.TButton')
            if self.connection_label:
                self.connection_label.config(text=f"{self.tr('connection_status')} {self.tr('not_connected')}", foreground="red")
            if self.balance_label:
                self.balance_label.config(text="Balance: $0.00")
            
            # Oto trade'i durdur
            if self.auto_trade_enabled:
                self.auto_trade_enabled = False
                self.auto_btn.config(style='AutoOff.TButton')
                self.auto_status_label.config(text=self.tr('auto_off'))
            
            # Piyasa durumunu sıfırla
            self.set_market_status(self.tr('market_neutral_text'), 'neutral')
            
            # Summary monitor'ı durdur
            if hasattr(self, 'summary_thread_running') and self.summary_thread_running:
                self.stop_summary_monitor()
            
            # Test modu durumunu güncelle
            self.update_test_mode_status()
            
            self.log_message("API bağlantısı koptu!")
            
        except Exception as e:
            self.log_message(f"Bağlantı koparma hatası: {e}")
    
    def start_price_updates(self):
        if self.price_thread and self.price_thread_running:
            return
            
        self.price_thread_running = True
        self.price_thread = threading.Thread(target=self.price_update_loop)
        self.price_thread.daemon = True
        self.price_thread.start()
    
    def price_update_loop(self):
        while self.price_thread_running and self.client:
            try:
                # Get current price
                ticker = self.client.futures_symbol_ticker(symbol=self.current_symbol)
                self.current_price = float(ticker['price'])
                
                # Update price history for chart
                current_time = datetime.now()
                self.price_history.append(self.current_price)
                self.time_history.append(current_time)
                
                # Keep only last 50 points
                if len(self.price_history) > 50:
                    self.price_history.pop(0)
                    self.time_history.pop(0)
                
                # Update UI in main thread
                self.root.after(0, self.update_ui)
                
                # Update positions
                self.root.after(0, self.update_positions)
                
                # Piyasa kontrol süresine göre güncelle
                interval = getattr(self, 'market_interval_seconds', 10)
                time.sleep(interval)
                
            except Exception as e:
                self.log_message(f"Fiyat güncelleme hatası: {e}")
                time.sleep(5)
    
    def update_ui(self):
        # Seçili Coin Bilgisi alanı kaldırıldı
        
        # Özet kutucukları artık market_monitor_loop içinde güncelleniyor
        
        # Grafik kaldırıldı
        pass
        
    def on_symbol_selection_change(self, event=None):
        """Listbox seçimi değişikliklerini dinle (artık sadece görsel feedback için)"""
        # Bu fonksiyon artık sadece UI feedback için kullanılıyor
        # Gerçek işlem listesi add/remove butonlarıyla yönetiliyor
        pass
    
    def add_selected_symbols(self):
        """Seçili coinleri işlemde kullanılacak listeye ekle"""
        try:
            selected_indices = self.symbol_listbox.curselection()
            if not selected_indices:
                self.log_message("Listeden coin seçin")
                return
            
            added_count = 0
            for idx in selected_indices:
                symbol = self.symbol_listbox.get(idx)
                if symbol not in self.selected_symbols:
                    self.selected_symbols.append(symbol)
                    added_count += 1
            
            if added_count > 0:
                self.log_message(f"{added_count} coin eklendi")
                self.update_selected_count_label()
                self.setup_selected_coins_cards()  # Kutucukları yenile (otomatik yüzde hesaplama ile)
                self.update_selected_coins_cards()  # Verileri güncelle
                self.save_settings_file()
            else:
                self.log_message("Seçili coinler zaten listede")
                
        except Exception as e:
            self.log_message(f"Coin ekleme hatası: {e}")
    
    def remove_selected_symbols(self):
        """Seçili coinleri işlemde kullanılacak listeden çıkar"""
        try:
            selected_indices = self.symbol_listbox.curselection()
            if not selected_indices:
                self.log_message("Listeden coin seçin")
                return
            
            removed_count = 0
            for idx in selected_indices:
                symbol = self.symbol_listbox.get(idx)
                if symbol in self.selected_symbols:
                    self.selected_symbols.remove(symbol)
                    removed_count += 1
            
            if removed_count > 0:
                self.log_message(f"{removed_count} coin çıkarıldı")
                self.update_selected_count_label()
                self.setup_selected_coins_cards()  # Kutucukları yenile (otomatik yüzde hesaplama ile)
                self.update_selected_coins_cards()  # Verileri güncelle
                self.save_settings_file()
            else:
                self.log_message("Seçili coinler zaten listede değil")
                
        except Exception as e:
            self.log_message(f"Coin çıkarma hatası: {e}")
    
    def update_selected_count_label(self):
        """Seçili coin sayısını güncelle"""
        try:
            count = len(self.selected_symbols)
            self.selected_count_label.config(text=self.tr('selected_count').format(count=count))
            
            # İlk seçili coin'i current_symbol yap (eski şekilde uyumluluk için)
            if self.selected_symbols:
                self.current_symbol = self.selected_symbols[0]
                
        except Exception as e:
            self.log_message(f"Sayı güncelleme hatası: {e}")
    
    def filter_symbol_list(self):
        """Arama metnine göre listbox'ı filtreler"""
        try:
            query = (self.symbol_search_var.get() or '').strip().upper()
            # Kaynak listeyi hazırla (önbellek varsa kullan)
            if hasattr(self, 'all_symbols_cache') and self.all_symbols_cache:
                source = list(self.all_symbols_cache)
            else:
                source = [self.symbol_listbox.get(i) for i in range(self.symbol_listbox.size())]
            # Filtrele
            filtered = [s for s in source if query in s.upper()] if query else source
            # Güncelle
            self.symbol_listbox.delete(0, tk.END)
            for s in filtered:
                self.symbol_listbox.insert(tk.END, s)
        except Exception as e:
            self.log_message(f"Sembol arama hatası: {e}")
    
    # Coin status badges function removed - only market status is shown
    
    def on_symbol_change(self, event=None):
        # Bu fonksiyon artık on_symbol_selection_change ile değiştirildi
        # Geriye dönük uyumluluk için koruyoruz
        pass
    
    def on_position_tree_click(self, event):
        """Pozisyon tablosunda checkbox toggle"""
        try:
            # Tıklanan bölgeyi belirle
            region = self.positions_tree.identify("region", event.x, event.y)
            if region != "cell":
                return
            
            # Tıklanan sütunu belirle
            column = self.positions_tree.identify_column(event.x)
            if column != "#1":  # #1 = ilk sütun (Select)
                return
            
            # Tıklanan item'ı belirle
            item_id = self.positions_tree.identify_row(event.y)
            if not item_id:
                return
            
            # Checkbox durumunu toggle et
            current_state = self.position_checkboxes.get(item_id, False)
            new_state = not current_state
            self.position_checkboxes[item_id] = new_state
            
            # Checkbox karakterini güncelle
            values = list(self.positions_tree.item(item_id, 'values'))
            values[0] = "☑" if new_state else "☐"
            self.positions_tree.item(item_id, values=values)
            
        except Exception as e:
            self.log_message(f"Checkbox toggle hatası: {e}")
    
    def toggle_auto_trade(self):
        if not self.client:
            messagebox.showerror("Hata", "Önce API'ye bağlanın!")
            return
        self.auto_trade_enabled = not self.auto_trade_enabled
        if self.auto_trade_enabled:
            self.auto_btn.config(style='AutoOn.TButton')
            self.auto_status_label.config(text=self.tr('auto_on'))
            self.log_message("Oto trade başlatıldı.")
            self.save_settings_file()
            # Hemen tek seferlik karar ver
            self.trigger_auto_trade_once()
            # Sürekli piyasa izleyicisini de başlat (çalışmıyorsa)
            try:
                self.start_market_monitor()
            except Exception as e:
                self.log_message(f"Oto trade market monitor başlatma hatası: {e}")
        else:
            self.auto_btn.config(style='AutoOff.TButton')
            self.auto_status_label.config(text=self.tr('auto_off'))
            self.log_message("Oto trade durduruldu.")
        
        # Oto trade durumunu güncelle
        self.update_auto_trade_status()
        self.save_settings_file()
        # İstenirse izleyici durdurulabilir (şimdilik açık kalsın)
    
    def trigger_auto_trade_once(self):
        try:
            # İlk 100 coini al
            symbols = self.get_top100_symbols_any()
            if not symbols:
                self.log_message("Oto trade için sembol listesi alınamadı.")
                return
            
            # İlk 100 coin için 1 saatlik değişimleri çek (CoinPaprika API)
            usdt_syms = [s + 'USDT' for s in symbols[:100]]
            self.market_service.fetch_futures_1h(usdt_syms)
            changes = self.market_service.latest_changes
            
            if not changes:
                self.log_message("Oto trade için 1h veri alınamadı.")
                return
            
            # Veri kaynağı bilgilendirme (ilk çalıştırmada)
            if len(changes) > 0 and not hasattr(self, '_data_source_logged'):
                if self.market_service._coinpaprika_failed:
                    self.log_message(f"🔄 Binance Fallback aktif - {len(changes)} coin verisi alındı")
                else:
                    self.log_message(f"🌐 CoinPaprika API aktif (60sn cache) - {len(changes)} coin verisi alındı")
                self._data_source_logged = True
            
            # 1 saatlik değişime göre yükselen ve düşen coin sayılarını hesapla
            rising_now = sum(1 for sym in usdt_syms if sym in changes and changes[sym] > 0)
            falling_now = sum(1 for sym in usdt_syms if sym in changes and changes[sym] < 0)
            neutral_now = sum(1 for sym in usdt_syms if sym in changes and changes[sym] == 0)  # Tam sıfır olanlar
            total_coins = rising_now + falling_now + neutral_now  # Veri alınan coin sayısı
            
            # Piyasa trend eşiği kontrolü
            market_up = False
            market_down = False
            state = None  # Varsayılan: nötr
            
            # Piyasa trend eşiğini al
            try:
                market_threshold = int(self.market_threshold_var.get())
            except Exception:
                market_threshold = 55  # varsayılan
            
            # Yeni mantık: Eşik değerine göre
            if rising_now >= market_threshold and falling_now >= market_threshold:
                # Her ikisi de eşik üzerinde -> Yükselen daha fazlaysa yükseliş, değilse düşüş
                if rising_now > falling_now:
                    state = 'up'
                    market_up = True
                    self.log_message(f"✅ [Piyasa Yükseliyor] Yükselen: {rising_now} >= Eşik: {market_threshold} (Düşen: {falling_now})")
                else:
                    state = 'down'
                    market_down = True
                    self.log_message(f"🔻 [Piyasa Düşüyor] Düşen: {falling_now} >= Eşik: {market_threshold} (Yükselen: {rising_now})")
            elif rising_now >= market_threshold:
                # Sadece yükselenler eşik üzerinde -> Piyasa Yükseliyor
                state = 'up'
                market_up = True
                self.log_message(f"✅ [Piyasa Yükseliyor] Yükselen: {rising_now} >= Eşik: {market_threshold}")
            elif falling_now >= market_threshold:
                # Sadece düşenler eşik üzerinde -> Piyasa Düşüyor
                state = 'down'
                market_down = True
                self.log_message(f"🔻 [Piyasa Düşüyor] Düşen: {falling_now} >= Eşik: {market_threshold}")
            else:
                # Hiçbiri eşik üzerinde değil -> Nötr
                state = None
                self.log_message(f"⚪ [Piyasa Nötr] Yükselen: {rising_now}, Düşen: {falling_now} (Eşik: {market_threshold}), Nötr: {neutral_now}, Toplam: {total_coins}")
                
            # İlk ölçüm bilgisi (sadece bilgi amaçlı)
            if self.prev_rising_count is None:
                self.log_message(f"📊 [İlk Ölçüm] Piyasa durumu tespit edildi")
                
            self.log_message(f"📊 [Piyasa Detay] Yükselen={rising_now} Düşen={falling_now} Nötr={neutral_now} Toplam={total_coins}/{len(usdt_syms)} (1h)")
            
            # Kaydet
            self.prev_rising_count = rising_now
            self.market_trend_state = state
            
            # Sadece piyasa durumunu güncelle (ok işaretleri ile)
            if market_up:
                self.set_market_status(self.tr('market_rising_text'), 'green')
            elif market_down:
                self.set_market_status(self.tr('market_falling_text'), 'red')
            else:
                self.set_market_status(self.tr('market_neutral_text'), 'neutral')
            
            # Sembol durumu (sadece trading için, UI'da gösterilmiyor)
            base = self.get_base_symbol_from_binance(self.current_symbol)
            sym_full = base + 'USDT'
            symbol_up = symbol_down = False
            if sym_full in changes:
                cur = changes[sym_full]
                prev = self.prev_symbol_change
                if prev is not None:
                    symbol_up = cur > prev
                    symbol_down = cur < prev
                self.log_message(f"Momentum (tek sefer) {base}: cur={cur:.2f}% prev={prev if prev is not None else 'None'} (1h)")
                self.prev_symbol_change = cur
            self.auto_trade_decision(market_up, market_down, symbol_up, symbol_down)
        except Exception as e:
            self.log_message(f"Oto trade tetikleme hatası: {e}")
    
    
    
    def update_positions(self):
        if not self.client:
            return
        
        try:
            # Pozisyonlar: 5 sn önbellek
            import time
            now = time.time()
            if now - self._cache_positions['ts'] > 5 or not self._cache_positions['data']:
                positions = self.client.futures_position_information()
                self._cache_positions = {'ts': now, 'data': positions}
            else:
                positions = self._cache_positions['data']
            
            # Periyodik bakiye etiketi güncelle (her 30 sn)
            try:
                now_ts = time.time()
                if not hasattr(self, 'last_balance_fetch_ts'):
                    self.last_balance_fetch_ts = 0
                if now_ts - self.last_balance_fetch_ts > 30:
                    now_ts = time.time()
                    if now_ts - self._cache_account['ts'] > 30 or not self._cache_account['data']:
                        acc = self.client.futures_account()
                        self._cache_account = {'ts': now_ts, 'data': acc}
                    else:
                        acc = self._cache_account['data']
                    bal = 0.0
                    try:
                        # Farklı bakiye alanlarını dene
                        balance_fields = ['totalWalletBalance', 'totalMarginBalance', 'totalCrossWalletBalance', 'totalInitialMargin', 'availableBalance', 'maxWithdrawAmount']
                        bal = 0.0
                        
                        for field in balance_fields:
                            if field in acc:
                                field_value = float(acc.get(field, 0.0))
                                self.log_message(f"Periyodik güncelleme - {field}: {field_value}")
                                if field_value > 0:
                                    bal = field_value
                                    self.log_message(f"Periyodik güncelleme - Bakiye bulundu: {field} = {field_value}")
                                    break
                        
                        if bal == 0.0:
                            self.log_message("Periyodik güncelleme - Hiçbir bakiye alanında değer bulunamadı")
                            
                    except Exception as e:
                        bal = 0.0
                        self.log_message(f"Periyodik güncelleme - Bakiye alanları kontrol hatası: {e}")
                    if bal == 0.0 and 'assets' in acc:
                        try:
                            total = 0.0
                            self.log_message(f"Periyodik güncelleme - Assets bulundu, sayısı: {len(acc['assets'])}")
                            for a in acc['assets']:
                                asset_name = a.get('asset', '')
                                wallet_balance = float(a.get('walletBalance', 0.0))
                                if asset_name in ('USDT', 'USDC', 'BUSD', 'FDUSD', 'TUSD'):
                                    total += wallet_balance
                                    self.log_message(f"Periyodik güncelleme - Asset {asset_name}: {wallet_balance}")
                            bal = total
                            self.log_message(f"Periyodik güncelleme - Assets'den toplam: {total}")
                        except Exception as e:
                            self.log_message(f"Periyodik güncelleme - Assets hatası: {e}")
                    # Ek fallback: futures_account_balance
                    try:
                        if (bal == 0.0) or (bal is None):
                            bals = self.client.futures_account_balance()
                            tot2 = 0.0
                            self.log_message(f"Periyodik güncelleme - futures_account_balance: {len(bals) if bals else 0} varlık")
                            for b in bals or []:
                                asset_name = b.get('asset', '')
                                balance_val = float(b.get('balance', b.get('availableBalance', 0.0)))
                                if asset_name in ('USDT','USDC','BUSD','FDUSD','TUSD'):
                                    tot2 += balance_val
                                    self.log_message(f"Periyodik güncelleme - Futures {asset_name}: {balance_val}")
                            if tot2 > 0:
                                bal = tot2
                                self.log_message(f"Periyodik güncelleme - Futures'dan toplam: {tot2}")
                    except Exception as e:
                        self.log_message(f"Periyodik güncelleme - Futures hatası: {e}")
                    
                    # Son fallback: Spot cüzdan bakiyesini kontrol et
                    if bal == 0.0:
                        try:
                            spot_account = self.client.get_account()
                            spot_balance = 0.0
                            self.log_message(f"Periyodik güncelleme - Spot cüzdan kontrol ediliyor...")
                            for balance in spot_account.get('balances', []):
                                asset_name = balance.get('asset', '')
                                free_balance = float(balance.get('free', 0.0))
                                locked_balance = float(balance.get('locked', 0.0))
                                total_spot_balance = free_balance + locked_balance
                                if asset_name in ('USDT','USDC','BUSD','FDUSD','TUSD') and total_spot_balance > 0:
                                    spot_balance += total_spot_balance
                                    self.log_message(f"Periyodik güncelleme - Spot balance {asset_name}: {total_spot_balance}")
                            if spot_balance > 0:
                                bal = spot_balance
                                self.log_message(f"Periyodik güncelleme - Spot cüzdan'dan toplam: {spot_balance}")
                        except Exception as e:
                            self.log_message(f"Periyodik güncelleme - Spot cüzdan hatası: {e}")
                    
                    self.balance = bal
                    if self.balance_label:
                        self.balance_label.config(text=f"Balance: ${self.balance:,.2f}")
                    self.last_balance_fetch_ts = now_ts
            except Exception:
                pass
            
            # Clear existing items
            for item in self.positions_tree.get_children():
                self.positions_tree.delete(item)
            # reset hover cache for positions
            self._pos_row_tags = {}
            self._pos_hover_item = None
            
            any_pos = False
            unrealized_sum = 0.0
            # Add current positions
            row_i = 0
            
            # Not: Kaldıraç ayarlama, kullanıcı değeri değiştirdiğinde veya pozisyon açarken yapılıyor
            
            for pos in positions:
                if float(pos['positionAmt']) != 0:
                    any_pos = True
                    symbol = pos['symbol']
                    size = float(pos['positionAmt'])
                    entry_price = float(pos['entryPrice'])
                    unrealized_pnl = float(pos.get('unRealizedProfit', pos.get('unrealizedProfit', 0)))
                    unrealized_sum += unrealized_pnl
                    side = "LONG" if size > 0 else "SHORT"
                    
                    # Kaldıraç oranını al - seçili coinler için paneldeki değeri göster
                    try:
                        if symbol in self.selected_symbols:
                            leverage = self.leverage_var.get()
                        else:
                            leverage = "1"
                    except Exception:
                        leverage = "1"
                    
                    # LONG/SHORT renkli tag seçimi
                    is_even = (row_i % 2) == 0
                    if side == "LONG":
                        tag = 'long_even' if is_even else 'long_odd'
                    else:  # SHORT
                        tag = 'short_even' if is_even else 'short_odd'
                    
                    row_i += 1
                    # Insert into tree (checkbox, kaldıraç eklendi, bindelik ayraçlı)
                    # Checkbox durumu: varsayılan olarak boş (☐)
                    checkbox_char = "☐"
                    item_id = self.positions_tree.insert("", "end", values=(
                        checkbox_char, symbol, side, f"{abs(size):,.6f}", 
                        f"${self.fmt_price(entry_price, 4)}", f"{leverage}x", f"${unrealized_pnl:,.2f}"
                    ), tags=(tag,))
                    # Checkbox durumunu kaydet (varsayılan: False)
                    if item_id not in self.position_checkboxes:
                        self.position_checkboxes[item_id] = False
            # PNL panel kaldırıldı
            # Hedef PNL kaldırıldı - Kar Al (%) kullanılıyor
            # Stop Loss eski kontrol kaldırıldı - check_stop_loss_take_profit() kullanılıyor
            # Update totals label
            realized_sum = getattr(self, 'realized_pnl_sum', 0.0)
            total = realized_sum + unrealized_sum
            # total_pnl_label kaldırıldı - artık kullanılmıyor
                    
        except Exception as e:
            self.log_message(f"Pozisyon güncelleme hatası: {str(e)}")
    
    # ------------------ Market Monitor (CoinPaprika) ------------------
    def start_market_monitor(self):
        if self.market_thread_running:
            return
        self.market_thread_running = True
        self.market_thread = threading.Thread(target=self.market_monitor_loop)
        self.market_thread.daemon = True
        self.market_thread.start()
        self.log_message("Piyasa izleme (CoinPaprika) başlatıldı.")
    
    def stop_market_monitor(self):
        self.market_thread_running = False
    
    def round_step(self, value, step):
        try:
            dval = Decimal(str(value))
            dstep = Decimal(str(step))
            # Quantize down to step precision
            q = dval.quantize(dstep, rounding=ROUND_DOWN)
            # Avoid negative zero
            if q == 0:
                return 0.0
            return float(q)
        except Exception:
            return value
    
    def get_symbol_lot_step(self, symbol):
        # Geriye: (step, min_qty) float (geriye dönük uyumluluk)
        try:
            step_str, min_qty_str, _ = self.get_symbol_lot_info(symbol)
            return (float(step_str), float(min_qty_str))
        except Exception:
            return (0.000001, 0.0)

    def get_symbol_lot_info(self, symbol):
        # Döner: (step_str, min_qty_str, decimals, notional_min, qty_precision)
        try:
            if not hasattr(self, '_exchange_cache'):
                self._exchange_cache = {'ts': 0, 'data': None}
            now = time.time()
            if not self._exchange_cache['data'] or now - self._exchange_cache['ts'] > 600:
                resp = self.session.get("https://fapi.binance.com/fapi/v1/exchangeInfo", timeout=10)
                if resp.status_code == 200:
                    self._exchange_cache['data'] = resp.json()
                    self._exchange_cache['ts'] = now
            data = self._exchange_cache['data'] or {}
            for s in data.get('symbols', []):
                if s.get('symbol') == symbol:
                    # Varsayılanlar
                    lot_step = None
                    lot_min = None
                    market_step = None
                    market_min = None
                    notional_min = 0.0
                    qty_prec = s.get('quantityPrecision', None)
                    for f in s.get('filters', []):
                        ftype = f.get('filterType')
                        if ftype == 'LOT_SIZE':
                            lot_step = f.get('stepSize')
                            lot_min = f.get('minQty')
                        elif ftype == 'MARKET_LOT_SIZE':
                            market_step = f.get('stepSize')
                            market_min = f.get('minQty')
                        elif ftype in ('MIN_NOTIONAL', 'NOTIONAL'):
                            notional_min = float(f.get('notional', notional_min))
                    # Öncelik: LOT_SIZE
                    step_str = lot_step or market_step or '0.000001'
                    min_qty_str = lot_min or market_min or '0.0'
                    # Ondalık sayısı step'ten
                    dec = 0
                    if '.' in step_str:
                        dec = len(step_str.split('.')[1].rstrip('0'))
                    if isinstance(qty_prec, int):
                        dec = min(dec, max(qty_prec, 0))
                    return (step_str, min_qty_str, dec, notional_min, qty_prec if isinstance(qty_prec, int) else dec)
            return ('0.000001', '0.0', 6, 0.0, 6)
        except Exception:
            return ('0.000001', '0.0', 6, 0.0, 6)

    def ceil_to_step(self, value, step_str):
        try:
            dval = Decimal(str(value))
            dstep = Decimal(step_str)
            n = (dval / dstep).to_integral_value(rounding=ROUND_DOWN)
            if n * dstep < dval:
                n = n + 1
            return n * dstep
        except Exception:
            return Decimal(str(value))

    def round_and_format_qty(self, symbol, qty, price_hint=None, force_step=None, force_decimals=None):
        # qty: float quantity; returns (qty_float, qty_str) formatted to step and meeting notional
        try:
            step_str, min_qty_str, dec, notional_min, qty_prec = self.get_symbol_lot_info(symbol)
            if force_step:
                step_str = force_step
            # min qty
            dval = Decimal(str(max(qty, float(min_qty_str))))
            dstep = Decimal(step_str)
            q = dval.quantize(dstep, rounding=ROUND_DOWN)
            if q <= 0:
                q = Decimal(min_qty_str)
            # notional kontrolü
            if notional_min and price_hint and float(q) * float(price_hint) < notional_min:
                need = self.ceil_to_step(Decimal(str(notional_min)) / Decimal(str(price_hint)), step_str)
                q = need
            # precision uygula
            dec_use = max(dec, qty_prec if isinstance(qty_prec, int) else dec)
            if force_decimals is not None:
                dec_use = force_decimals
            qty_str = f"{q:.{dec_use}f}" if dec_use > 0 else f"{int(q)}"
            return float(q), qty_str
        except Exception:
            q = max(qty, 0.0)
            return q, str(q)

    def place_market_order_with_retries(self, symbol, side, qty_raw, price_hint=None):
        # Çoklu strateji ile -1111 precision hatasına karşı dene
        strategies = []
        # 1) Varsayılan (LOT_SIZE/MARKET_LOT_SIZE)
        step_str, min_qty_str, dec, notional_min, qprec = self.get_symbol_lot_info(symbol)
        strategies.append((step_str, dec))
        # 2) 0.1 adımı dene
        strategies.append(('0.1', 1))
        # 3) 1 adımı dene
        strategies.append(('1', 0))
        last_err = None
        for step, decimals in strategies:
            qf, qs = self.round_and_format_qty(symbol, qty_raw, price_hint=price_hint, force_step=step, force_decimals=decimals)
            try:
                self.log_message(f"OrderTry {symbol} step={step} dec={decimals} -> qty={qs}")
                return self.client.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=qs)
            except BinanceAPIException as e:
                last_err = e
                if e.code != -1111:
                    raise
                continue
        # son hata
        if last_err:
            raise last_err

    def get_current_position(self, symbol):
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            if positions:
                pos = positions[0]
                amt = float(pos['positionAmt'])
                entry = float(pos['entryPrice'])
                return amt, entry
        except Exception:
            pass
        return 0.0, 0.0

    def ensure_isolated_margin(self, symbol):
        try:
            self.client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')
            self.log_message(f"Margin tipi ISOLATED ayarlandı: {symbol}")
        except BinanceAPIException as e:
            # -4046: No need to change margin type or already isolated
            try:
                code = getattr(e, 'code', None)
                msg = getattr(e, 'message', '')
            except Exception:
                code = None
                msg = ''
            if code in (-4046, 4046) or 'No need to change' in str(msg) or 'margin type is same' in str(msg).lower():
                self.log_message(f"Margin tipi zaten ISOLATED: {symbol}")
                return
            else:
                self.log_message(f"Margin tipi değiştirilemedi: {symbol} - {e}")
                raise
        except Exception as ex:
            self.log_message(f"Margin tipi hata: {symbol} - {ex}")
            # Devam et (bazı durumlarda mevcut pozisyon varken değiştirilemez)
    
    def log_trade(self, symbol, qty, entry_price, exit_price, pnl):
        try:
            row = {
                'time': datetime.now().strftime('%m-%d %H:%M'),
                'symbol': symbol,
                'qty': qty,
                'entry': entry_price,
                'exit': exit_price,
                'pnl': pnl
            }
            line = f"{row['time']},{row['symbol']},{row['qty']},{row['entry']},{row['exit']},{row['pnl']}\n"
            path = self.get_trades_path()
            self.ensure_csv_header(path, 'time,symbol,qty,entry,exit,pnl')
            with open(path, 'a', encoding='utf-8') as f:
                f.write(line)
        except Exception as e:
            self.log_message(f"Trade log yazılamadı: {e}")
    
    def env_code(self) -> str:
        try:
            return 'test' if (self.env_var.get() == 'Test') else 'live'
        except Exception:
            return 'live'

    def get_trades_path(self) -> str:
        return f"trades_history_{self.env_code()}.csv"

    def get_totals_path(self) -> str:
        return f"totals_history_{self.env_code()}.csv"

    def get_binance_realized_pnl_total(self):
        """Binance'den toplam realized PNL'i al"""
        try:
            # Son 365 gün için toplam realized PNL
            end_ms = int(time.time() * 1000)
            start_ms = end_ms - 365*24*60*60*1000  # 1 yıl
            
            # Income cache kontrolü (10 saniye - sürekli güncel)
            current_time = time.time()
            if (current_time - self._last_income_fetch_ts) < 10 and self._last_income_cache:
                incomes = self._last_income_cache
                # Sessiz mod - cache kullanılıyor
            else:
                incomes = self.client.futures_income_history(startTime=start_ms, endTime=end_ms, limit=1000)
                self._last_income_cache = incomes
                self._last_income_fetch_ts = current_time
                # Sessiz mod - sürekli güncelleniyor
            total = 0.0
            
            for inc in incomes:
                itype = inc.get('incomeType', '')
                if itype in ('REALIZED_PNL', 'COMMISSION', 'FUNDING_FEE'):
                    total += float(inc.get('income', 0.0))
                    
            return total
        except Exception as e:
            self.log_message(f"Binance PNL toplamı alınamadı: {e}")
            return 0.0
    
    # Bu fonksiyon artık update_binance_cumulative_pnl ile değiştirildi
    def update_cumulative_pnl_label(self):
        """Eski local PNL fonksiyonu - artık Binance kullanıyor"""
        try:
            self.update_binance_cumulative_pnl()
        except Exception as e:
            self.log_message(f"PNL label güncelleme hatası: {e}")

    def ensure_csv_header(self, path, header_line):
        try:
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(header_line + "\n")
        except Exception:
            pass

    def write_totals_snapshot(self):
        try:
            totals_path = self.get_totals_path()
            self.ensure_csv_header(totals_path, 'time,local_total,binance_realized,total')
            local_total = getattr(self, 'local_total_pnl', 0.0)
            binance_realized = getattr(self, 'binance_realized_total', 0.0)
            total = float(local_total) + float(binance_realized)
            line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{local_total:.2f},{binance_realized:.2f},{total:.2f}\n"
            with open(totals_path, 'a', encoding='utf-8') as f:
                f.write(line)
            self.log_message(f"Toplam PNL kaydedildi: {totals_path}")
        except Exception as e:
            self.log_message(f"Toplam PNL yazılamadı: {e}")
    
    def check_for_updates(self):
        """Güncelleme kontrolü yap ve diyaloğu göster"""
        try:
            if not SoftwareUpdater or not UpdateDialog:
                messagebox.showinfo(self.tr('info'), self.tr('update_module_not_loaded'))
                return
            
            self.log_message("Güncelleme kontrol ediliyor...")
            
            def check_updates_thread():
                try:
                    updater = SoftwareUpdater(lang=self.lang_var.get().split(' - ')[0] if ' - ' in self.lang_var.get() else self.lang_var.get())
                    has_update, message = updater.check_for_updates()
                    
                    # Ana thread'de UI'yi güncelle
                    self.root.after(0, lambda: self.show_update_dialog(updater, has_update, message))
                    
                except Exception as e:
                    error_msg = self.tr('update_check_error').format(error=e)
                    self.root.after(0, lambda: messagebox.showerror(self.tr('error'), error_msg))
            
            # Thread'de kontrol et (UI bloke olmasın)
            threading.Thread(target=check_updates_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror(self.tr('error'), self.tr('update_check_failed').format(error=e))
    
    def show_update_dialog(self, updater, has_update, message):
        """Güncelleme diyaloğunu göster"""
        try:
            dialog = UpdateDialog(self.root, updater)
            dialog.show_update_dialog(has_update, message)
            
            if has_update:
                self.log_message("Yeni güncelleme mevcut!")
                self.show_update_warning(True)
            else:
                self.log_message("Yazılım güncel.")
                self.show_update_warning(False)
                
        except Exception as e:
            messagebox.showerror(self.tr('error'), self.tr('update_dialog_error').format(error=e))
    
    def show_update_warning(self, show):
        """Güncelleme uyarısını göster/gizle - Grid layout için"""
        try:
            if not self.update_warning_label:
                return
                
            if show:
                warning_text = self.tr('update_available')
                self.update_warning_label.config(text=warning_text)
                # Grid ile göster
                try:
                    self.update_warning_label.grid()  # grid_remove ile gizlenmişti, tekrar göster
                except Exception:
                    pass
                self.update_available = True
            else:
                self.update_warning_label.config(text="")
                # Hide with grid_remove to prevent white gap
                self.update_warning_label.grid_remove()
                self.update_available = False
                
        except Exception as e:
            print(f"Güncelleme uyarısı gösterme hatası: {e}")
    
    def auto_check_updates_on_startup(self):
        """Program başlangıcında otomatik güncelleme kontrolü"""
        try:
            if not SoftwareUpdater or not UpdateDialog:
                return
            
            def auto_check():
                try:
                    # 3 saniye bekle (program tam yüklensin)
                    time.sleep(3)
                    
                    updater = SoftwareUpdater(lang=self.lang_var.get().split(' - ')[0] if ' - ' in self.lang_var.get() else self.lang_var.get())
                    has_update, message = updater.check_for_updates()
                    
                    if has_update:
                        # Güncelleme uyarısını göster
                        self.root.after(0, lambda: self.show_update_warning(True))
                        
                        # Güncelleme varsa kullanıcıya sor
                        def ask_user():
                            result = messagebox.askyesno(
                                "Güncelleme Mevcut", 
                                f"{message}\n\nGüncellemeyi şimdi yüklemek istiyor musunuz?",
                                parent=self.root
                            )
                            if result:
                                self.show_update_dialog(updater, has_update, message)
                        
                        self.root.after(0, ask_user)
                    else:
                        # Güncelleme uyarısını gizle
                        self.root.after(0, lambda: self.show_update_warning(False))
                        
                except Exception as e:
                    print(f"Otomatik güncelleme kontrolü hatası: {e}")
            
            # Thread'de otomatik kontrol et
            threading.Thread(target=auto_check, daemon=True).start()
            
        except Exception as e:
            print(f"Otomatik güncelleme kontrolü başlatılamadı: {e}")
    
    def update_symbol_list(self):
        try:
            symbols = self.get_top100_symbols_any()
            avail_set = self.get_binance_usdt_perp_set()
            allowed = [s + 'USDT' for s in symbols if (s + 'USDT') in avail_set]
            if not allowed:
                return
            
            # Mevcut seçimleri koru
            current_selection = self.selected_symbols.copy()
            # Listbox state'i koru (arama/scroll/seçim)
            try:
                query = (self.symbol_search_var.get() or '').strip()
            except Exception:
                query = ''
            try:
                prev_selected_values = [self.symbol_listbox.get(i) for i in self.symbol_listbox.curselection()]
            except Exception:
                prev_selected_values = []
            try:
                y0, _ = self.symbol_listbox.yview()
            except Exception:
                y0 = 0.0
            
            # Kaynağı güncelle ve filtreyi koru
            self.all_symbols_cache = list(allowed)
            self.symbol_listbox.delete(0, tk.END)
            if query:
                # Var olan filter metnini bozmadan uygula
                try:
                    self.filter_symbol_list()
                except Exception:
                    for symbol in allowed:
                        self.symbol_listbox.insert(tk.END, symbol)
            else:
                for symbol in allowed:
                    self.symbol_listbox.insert(tk.END, symbol)
            # Önceki seçimleri geri yükle
            if prev_selected_values:
                try:
                    current_items = [self.symbol_listbox.get(i) for i in range(self.symbol_listbox.size())]
                    for idx, val in enumerate(current_items):
                        if val in prev_selected_values:
                            self.symbol_listbox.selection_set(idx)
                except Exception:
                    pass
            # Scroll konumunu geri getir
            try:
                if y0:
                    self.symbol_listbox.yview_moveto(y0)
            except Exception:
                pass
            
            # Mevcut işlem listesinde olmayan coinleri temizle
            self.selected_symbols = [s for s in self.selected_symbols if s in allowed]
            
            # Eğer hiç coin seçili değilse ilk 5'ini otomatik ekle
            if not self.selected_symbols and len(allowed) >= 5:
                self.selected_symbols = allowed[:5]
                self.log_message("Otomatik olarak ilk 5 coin seçildi")
            
            # Etiket güncelle
            self.update_selected_count_label()
            
            # Seçilen coinlerin kutucuklarını güncelle
            if hasattr(self, 'selected_coins_container'):
                self.setup_selected_coins_cards()
                self.update_selected_coins_cards()
            
        except Exception as e:
            self.log_message(f"Sembol listesi güncellenemedi: {e}")
    
    def get_binance_usdt_perp_set(self):
        try:
            if not hasattr(self, '_perp_cache'):
                self._perp_cache = {'ts': 0, 'set': set()}
            now = time.time()
            if not self._perp_cache['set'] or now - self._perp_cache['ts'] > 600:
                ex = self.session.get("https://fapi.binance.com/fapi/v1/exchangeInfo", timeout=10)
                sset = set()
                if ex.status_code == 200:
                    info = ex.json()
                    for s in info.get('symbols', []):
                        try:
                            if s.get('contractType') == 'PERPETUAL' and s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING':
                                sset.add(s.get('symbol'))
                        except Exception:
                            continue
                self._perp_cache['set'] = sset
                self._perp_cache['ts'] = now
            return self._perp_cache['set']
        except Exception:
            return set()
    
    def get_available_usdt(self):
        try:
            bals = self.client.futures_account_balance()
            for b in bals:
                if b.get('asset') == 'USDT':
                    return float(b.get('availableBalance', b.get('balance', 0.0)))
        except Exception:
            pass
        return max(0.0, self.balance)
    
    def calc_auto_usdt_amount(self):
        """Bakiyenin yüzdesine göre USDT miktarı hesaplar"""
        try:
            balance_percent = float(self.balance_percent_var.get())
            if balance_percent <= 0:
                return 0.0
            
            # Mevcut bakiyeyi al
            available_balance = self.get_available_usdt()
            
            # Yüzdeyi uygula
            usdt_amount = available_balance * (balance_percent / 100.0)
            return max(0.0, usdt_amount)
        except Exception:
            return 0.0
    
    def ensure_long_position(self, symbol_ctx=None):
        # Yalnızca seçili sembol için çalış
        if symbol_ctx and symbol_ctx != self.current_symbol:
            return
        amt, entry = self.get_current_position(self.current_symbol)
        if amt > 0:
            self.log_message("Zaten LONG pozisyon var, koru")
            return
        # ensure isolated margin and set leverage
        try:
            self.ensure_isolated_margin(self.current_symbol)
        except Exception:
            pass
        try:
            lev = int(self.leverage_var.get())
            # Lisans yoksa veya süresi bitmişse max 1x
            if not self.license_valid:
                lev = 1
                self.leverage_var.set("1")
                self.log_message(self.tr('license_leverage_limited_log'))
            self.client.futures_change_leverage(symbol=self.current_symbol, leverage=lev)
        except Exception:
            pass
        if amt < 0:
            # close short
            try:
                t = self.client.futures_symbol_ticker(symbol=self.current_symbol)
                exit_price = float(t.get('price', 0))
            except Exception:
                exit_price = self.current_price
            pnl = (entry - exit_price) * abs(amt)  # short close pnl
            self.client.futures_create_order(symbol=self.current_symbol, side='BUY', type='MARKET', quantity=abs(amt))
            try:
                self.log_trade(self.current_symbol, abs(amt), entry, exit_price, pnl)
            except Exception:
                pass
        usdt_amount = self.calc_auto_usdt_amount()
        
        # KALDIRAÇ UYGULA
        lev = int(self.leverage_var.get())
        if not self.license_valid:
            lev = 1
        leveraged_amount = usdt_amount * lev
        
        raw = max(1e-8, leveraged_amount) / max(1e-8, self.current_price)
        qty_float, qty_str = self.round_and_format_qty(self.current_symbol, raw, price_hint=self.current_price)
        step_str, min_qty_str, dec, notional_min, qprec = self.get_symbol_lot_info(self.current_symbol)
        self.log_message(f"OrderCheck {self.current_symbol} step={step_str} minQty={min_qty_str} notionalMin={notional_min} qPrec={qprec} raw={raw:.8f} price={self.fmt_price(self.current_price, 4)} -> qty={qty_str}")
        self.place_market_order_with_retries(self.current_symbol, 'BUY', raw, price_hint=self.current_price)
        self.log_message(f"Otomatik LONG açıldı | Marjin: {usdt_amount:.2f} USDT | Kaldıraç: {lev}x | Pozisyon: {leveraged_amount:.2f} USDT | Miktar: {qty_float}")
    
    def get_selected_symbol(self):
        try:
            sel = self.positions_tree.selection()
            if not sel:
                return None
            vals = self.positions_tree.item(sel[0], 'values')
            return vals[0] if vals else None
        except Exception:
            return None

    def close_selected_position(self):
        """Checkbox'ı işaretli olan tüm pozisyonları kapat"""
        if not self.client:
            messagebox.showwarning(self.tr('info'), self.tr('connect_api_first'))
            return
        
        # Checkbox'ı işaretli olan item'ları bul
        selected_items = []
        for item_id, is_checked in self.position_checkboxes.items():
            if is_checked:
                # TreeView'de item hala var mı kontrol et
                try:
                    values = self.positions_tree.item(item_id, 'values')
                    if values:
                        # values[1] = Symbol (values[0] = checkbox)
                        symbol = values[1]
                        selected_items.append((item_id, symbol))
                except Exception:
                    # Item artık yok
                    pass
        
        if not selected_items:
            messagebox.showinfo(self.tr('info'), self.tr('select_position_from_table'))
            return
        
        # Seçili pozisyonları kapat (arka planda, rate limit için delay ile)
        def close_positions_with_delay():
            closed_count = 0
            failed_symbols = []
            
            for idx, (item_id, symbol) in enumerate(selected_items):
                try:
                    self.log_message(f"⏳ Kapatılıyor ({idx+1}/{len(selected_items)}): {symbol}")
                    success = self.close_symbol_positions(symbol)
                    
                    if success:
                        closed_count += 1
                        # Checkbox durumunu temizle
                        if item_id in self.position_checkboxes:
                            self.position_checkboxes[item_id] = False
                        
                        # Her pozisyon kapandıktan sonra tabloyu VE özeti hemen güncelle (sıralı görünüm)
                        def refresh_table_and_summary():
                            self._cache_positions = {'ts': 0.0, 'data': None}
                            self._cache_account = {'ts': 0.0, 'data': None}
                            self.update_positions()
                            self.update_summary_cards()  # ✅ Hesap özetini de güncelle!
                        
                        self.root.after(0, refresh_table_and_summary)
                        
                        # Rate limit için pozisyonlar arasında delay
                        if idx < len(selected_items) - 1:
                            time.sleep(1.0)  # 1 saniye bekle (tablo güncellensin)
                    else:
                        # Pozisyon zaten kapalıydı veya bulunamadı
                        self.log_message(f"⚠️ [{symbol}] Açık pozisyon bulunamadı")
                        
                except Exception as e:
                    error_msg = str(e)
                    self.log_message(f"❌ Pozisyon kapatma hatası {symbol}: {error_msg}")
                    failed_symbols.append(symbol)
                    # Hata olsa bile devam et, diğer pozisyonları kapat
                    continue
            
            # Tüm işlemler bittikten sonra sonuç mesajı göster
            def show_result():
                if closed_count > 0:
                    msg = self.tr('positions_closed').format(count=closed_count)
                    if failed_symbols:
                        msg += f"\n\n❌ Hata: {', '.join(failed_symbols)}"
                    messagebox.showinfo(self.tr('success'), msg)
                elif failed_symbols:
                    messagebox.showerror(self.tr('error'), f"Kapatılamadı: {', '.join(failed_symbols)}")
            
            self.root.after(0, show_result)
        
        # Arka planda çalıştır (UI donmasın)
        threading.Thread(target=close_positions_with_delay, daemon=True).start()

    def open_settings_dialog(self):
        try:
            info = (
                f"Ortam: {self.env_var.get()}\n"
                f"Interval(sn): {self.market_interval_var.get()}\n"
                f"Stop Loss(%): {getattr(self, 'stop_loss_pct_var', tk.StringVar(value='0')).get()}\n"
                f"Kar Al(%): {getattr(self, 'take_profit_pct_var', tk.StringVar(value='0')).get()}\n"
            )
            messagebox.showinfo(self.tr('info'), info)
        except Exception as e:
            messagebox.showerror(self.tr('error'), str(e))

    def close_symbol_positions(self, symbol):
        """Belirtilen sembol için tüm pozisyonları kapat"""
        order_success = False
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            if not positions:
                self.log_message(f"[{symbol}] Pozisyon bilgisi alınamadı")
                return False
                
            pos = positions[0]
            amt = float(pos.get('positionAmt', 0))
            entry = float(pos.get('entryPrice', 0))
            
            if amt == 0:
                self.log_message(f"[{symbol}] Açık pozisyon yok")
                return False
            
            # Exit price from ticker
            try:
                t = self.client.futures_symbol_ticker(symbol=symbol)
                exit_price = float(t.get('price', 0))
            except Exception:
                exit_price = entry
            
            # Pozisyonu kapat
            side = 'SELL' if amt > 0 else 'BUY'
            self.client.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=abs(amt))
            order_success = True
            
            # PNL hesapla ve logla
            pnl = (exit_price - entry) * amt
            try:
                self.log_trade(symbol, abs(amt), entry, exit_price, pnl)
            except Exception as log_err:
                self.log_message(f"[{symbol}] Log hatası (önemsiz): {log_err}")
            
            self.log_message(f"✅ [{symbol}] Pozisyon kapatıldı (PNL: ${pnl:.2f})")
            
            # Cache'leri temizle (hesap özeti güncellensin)
            self._cache_positions = {'ts': 0.0, 'data': None}
            self._cache_account = {'ts': 0.0, 'data': None}
            return True
            
        except Exception as e:
            if order_success:
                # Emir gönderildi ama sonrası hata verdi - yine de başarılı sayılır
                self.log_message(f"⚠️ [{symbol}] Pozisyon kapatıldı ama işlem sonrası hata: {e}")
                return True
            else:
                # Emir gönderilemedi - gerçek hata
                self.log_message(f"❌ [{symbol}] Pozisyon kapatma hatası: {e}")
                raise  # Exception'ı yukarı fırlat
    
    def ensure_short_position(self, symbol_ctx=None):
        # Yalnızca seçili sembol için çalış
        if symbol_ctx and symbol_ctx != self.current_symbol:
            return
        amt, entry = self.get_current_position(self.current_symbol)
        if amt < 0:
            self.log_message("Zaten SHORT pozisyon var, koru")
            return
        # set leverage (lisans kontrolü)
        try:
            lev = int(self.leverage_var.get())
            # Lisans yoksa veya süresi bitmişse max 1x
            if not self.license_valid:
                lev = 1
                self.leverage_var.set("1")
                self.log_message(self.tr('license_leverage_limited_log'))
            self.client.futures_change_leverage(symbol=self.current_symbol, leverage=lev)
        except Exception:
            pass
        if amt > 0:
            # close long
            try:
                t = self.client.futures_symbol_ticker(symbol=self.current_symbol)
                exit_price = float(t.get('price', 0))
            except Exception:
                exit_price = self.current_price
            pnl = (exit_price - entry) * abs(amt)  # long close pnl
            self.client.futures_create_order(symbol=self.current_symbol, side='SELL', type='MARKET', quantity=abs(amt))
            try:
                self.log_trade(self.current_symbol, abs(amt), entry, exit_price, pnl)
            except Exception:
                pass
        # open short with lot step
        usdt_amount = self.calc_auto_usdt_amount()
        
        # KALDIRAÇ UYGULA
        lev = int(self.leverage_var.get())
        if not self.license_valid:
            lev = 1
        leveraged_amount = usdt_amount * lev
        
        raw = max(1e-8, leveraged_amount) / max(1e-8, self.current_price)
        qty_float, qty_str = self.round_and_format_qty(self.current_symbol, raw, price_hint=self.current_price)
        # Debug log
        step_str, min_qty_str, dec, notional_min, qprec = self.get_symbol_lot_info(self.current_symbol)
        self.log_message(f"OrderCheck {self.current_symbol} step={step_str} minQty={min_qty_str} notionalMin={notional_min} qPrec={qprec} raw={raw:.8f} price={self.fmt_price(self.current_price, 4)} -> qty={qty_str}")
        self.place_market_order_with_retries(self.current_symbol, 'SELL', raw, price_hint=self.current_price)
        self.log_message(f"Otomatik SHORT açıldı | Marjin: {usdt_amount:.2f} USDT | Kaldıraç: {lev}x | Pozisyon: {leveraged_amount:.2f} USDT | Miktar: {qty_float}")
    
    def ensure_long_position_multi(self, symbol):
        """Belirtilen symbol için LONG pozisyon aç/koru"""
        try:
            amt, entry = self.get_current_position(symbol)
            if amt > 0:
                self.log_message(f"[{symbol}] Zaten LONG pozisyon var, koru")
                return
            
            # Isolated margin ve leverage ayarla
            try:
                self.ensure_isolated_margin(symbol)
                lev = int(self.leverage_var.get())
                # Lisans yoksa veya süresi bitmişse max 1x
                if not self.license_valid:
                    lev = 1
                    self.leverage_var.set("1")
                    self.log_message(f"[{symbol}] {self.tr('license_leverage_limited_log')}")
                self.client.futures_change_leverage(symbol=symbol, leverage=lev)
            except Exception as e:
                self.log_message(f"[{symbol}] Margin/leverage hatası: {e}")
            
            # Mevcut SHORT pozisyonu varsa kapat
            if amt < 0:
                try:
                    t = self.client.futures_symbol_ticker(symbol=symbol)
                    exit_price = float(t.get('price', 0))
                    pnl = (entry - exit_price) * abs(amt)
                    self.client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=abs(amt))
                    try:
                        self.log_trade(symbol, abs(amt), entry, exit_price, pnl)
                    except Exception:
                        pass
                    self.log_message(f"[{symbol}] SHORT pozisyon kapatıldı")
                except Exception as e:
                    self.log_message(f"[{symbol}] SHORT kapama hatası: {e}")
                    return
            
            # LONG pozisyon aç
            usdt_amount = self.calc_auto_usdt_amount_per_coin()
            current_price = self.get_symbol_current_price(symbol)
            
            if current_price <= 0:
                self.log_message(f"[{symbol}] Fiyat bilgisi alınamıyor")
                return
            
            # KALDIRAÇ UYGULA - Marjin × Kaldıraç = Pozisyon Büyüklüğü
            lev = int(self.leverage_var.get())
            if not self.license_valid:
                lev = 1
            leveraged_amount = usdt_amount * lev
            
            raw = max(1e-8, leveraged_amount) / max(1e-8, current_price)
            qty_float, qty_str = self.round_and_format_qty(symbol, raw, price_hint=current_price)
            
            self.place_market_order_with_retries(symbol, 'BUY', raw, price_hint=current_price)
            self.log_message(f"[{symbol}] LONG pozisyon açıldı | Marjin: {usdt_amount:.2f} USDT | Kaldıraç: {lev}x | Pozisyon: {leveraged_amount:.2f} USDT | Miktar: {qty_str}")
            
        except Exception as e:
            self.log_message(f"[{symbol}] LONG pozisyon açma hatası: {e}")
    
    def ensure_short_position_multi(self, symbol):
        """Belirtilen symbol için SHORT pozisyon aç/koru"""
        try:
            amt, entry = self.get_current_position(symbol)
            if amt < 0:
                self.log_message(f"[{symbol}] Zaten SHORT pozisyon var, koru")
                return
            
            # Isolated margin ve leverage ayarla
            try:
                self.ensure_isolated_margin(symbol)
                lev = int(self.leverage_var.get())
                # Lisans yoksa veya süresi bitmişse max 1x
                if not self.license_valid:
                    lev = 1
                    self.leverage_var.set("1")
                    self.log_message(f"[{symbol}] {self.tr('license_leverage_limited_log')}")
                self.client.futures_change_leverage(symbol=symbol, leverage=lev)
            except Exception as e:
                self.log_message(f"[{symbol}] Margin/leverage hatası: {e}")
            
            # Mevcut LONG pozisyonu varsa kapat
            if amt > 0:
                try:
                    t = self.client.futures_symbol_ticker(symbol=symbol)
                    exit_price = float(t.get('price', 0))
                    pnl = (exit_price - entry) * abs(amt)
                    self.client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=abs(amt))
                    try:
                        self.log_trade(symbol, abs(amt), entry, exit_price, pnl)
                    except Exception:
                        pass
                    self.log_message(f"[{symbol}] LONG pozisyon kapatıldı")
                except Exception as e:
                    self.log_message(f"[{symbol}] LONG kapama hatası: {e}")
                    return
            
            # SHORT pozisyon aç
            usdt_amount = self.calc_auto_usdt_amount_per_coin()
            current_price = self.get_symbol_current_price(symbol)
            
            if current_price <= 0:
                self.log_message(f"[{symbol}] Fiyat bilgisi alınamıyor")
                return
            
            # KALDIRAÇ UYGULA - Marjin × Kaldıraç = Pozisyon Büyüklüğü
            lev = int(self.leverage_var.get())
            if not self.license_valid:
                lev = 1
            leveraged_amount = usdt_amount * lev
            
            raw = max(1e-8, leveraged_amount) / max(1e-8, current_price)
            qty_float, qty_str = self.round_and_format_qty(symbol, raw, price_hint=current_price)
            
            self.place_market_order_with_retries(symbol, 'SELL', raw, price_hint=current_price)
            self.log_message(f"[{symbol}] SHORT pozisyon açıldı | Marjin: {usdt_amount:.2f} USDT | Kaldıraç: {lev}x | Pozisyon: {leveraged_amount:.2f} USDT | Miktar: {qty_str}")
            
        except Exception as e:
            self.log_message(f"[{symbol}] SHORT pozisyon açma hatası: {e}")
    
    def calc_auto_usdt_amount_per_coin(self):
        """Her coin için USDT miktarını hesapla (seçili coin sayısına göre böl)"""
        try:
            total_amount = self.calc_auto_usdt_amount()
            coin_count = max(1, len(self.selected_symbols))
            per_coin_amount = total_amount / coin_count
            
            # Detaylı log
            self.log_message(f"💰 Toplam: {total_amount:.2f} USDT | Coin Sayısı: {coin_count} | Her Coin: {per_coin_amount:.2f} USDT")
            
            return per_coin_amount
        except Exception:
            return 10.0  # varsayılan
    
    def get_symbol_current_price(self, symbol):
        """Symbol'un güncel fiyatını al"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception:
            return 0.0
    
    def restore_symbol_selections(self):
        """Kaydedilmiş coin seçimlerini yükle"""
        try:
            self.log_message(f"🔄 restore_symbol_selections çağrıldı")
            self.log_message(f"📋 Mevcut selected_symbols: {self.selected_symbols}")
            
            if self.selected_symbols:
                self.log_message(f"✅ {len(self.selected_symbols)} coin bulundu, kartlar oluşturuluyor...")
                self.update_selected_count_label()
                # ✅ Coin kartlarını oluştur
                self.setup_selected_coins_cards()
                # Verileri güncelle
                self.update_selected_coins_cards()
                self.log_message(f"✅ Kaydedilmiş seçimler yüklendi: {len(self.selected_symbols)} coin")
            else:
                self.log_message("⚠️ selected_symbols listesi boş! Kaydedilmiş seçim bulunamadı")
            
        except Exception as e:
            self.log_message(f"❌ Seçimleri geri yükleme hatası: {e}")
            import traceback
            self.log_message(f"Detay: {traceback.format_exc()}")
    
    def auto_trade_decision(self, market_up, market_down, symbol_up, symbol_down):
        try:
            now = time.time()
            cooldown = self.market_interval_seconds
            if now - self.last_auto_action_time < cooldown:
                return
            self.log_message(f"Seçili sembol: {self.current_symbol}")
            self.log_message(f"Oto karar: market_up={market_up}, market_down={market_down}, symbol_up={symbol_up}, symbol_down={symbol_down}")
            if market_up and symbol_up:
                self.log_message("Koşul sağlandı (LONG) -> emir gönderiliyor")
                self.ensure_long_position()
                self.last_auto_action_time = now
            elif market_down and symbol_down:
                self.log_message("Koşul sağlandı (SHORT) -> emir gönderiliyor")
                self.ensure_short_position()
                self.last_auto_action_time = now
            else:
                self.log_message("Oto trade: nötr, bekleniyor")
        except Exception as e:
            self.log_message(f"Otomatik işlem hatası: {e}")
    
    def analyze_multi_coin_momentum(self, changes):
        """Seçili tüm coinler için momentum analizi yap"""
        try:
            if not changes or not self.selected_symbols:
                return
            
            for symbol in self.selected_symbols:
                base = self.get_base_symbol_from_binance(symbol)
                sym_full = base + 'USDT'
                
                if sym_full in changes:
                    current_change = changes[sym_full]
                    
                    # Önceki değer var mı?
                    prev_change = self.symbol_momentum.get(symbol, {}).get('prev_change')
                    
                    # Coin yön kontrolü (1h değişime göre)
                    # momentum_up: Coin 1h içinde yükseliyor mu? (pozitif değişim)
                    # momentum_down: Coin 1h içinde düşüyor mu? (negatif değişim)
                    momentum_up = current_change > 0
                    momentum_down = current_change < 0
                    
                    # Fiyat bilgisini de sakla
                    self.symbol_prices[symbol] = current_change
                    
                    # Momentum bilgisini güncelle
                    self.symbol_momentum[symbol] = {
                        'prev_change': current_change,
                        'momentum_up': momentum_up,
                        'momentum_down': momentum_down,
                        'change_percent': current_change
                    }
                    
        except Exception as e:
            self.log_message(f"Multi-coin momentum analizi hatası: {e}")
    
    def check_stop_loss_take_profit(self):
        """Tüm pozisyonlar için Stop Loss ve Kar Al kontrolü yapar (oto trade açık değilken de çalışır)"""
        if not self.client:
            return
        
        try:
            # Global Kar Al ve Stop Loss yüzdelerini al
            try:
                global_take_profit_pct = float(self.take_profit_pct_var.get())
            except Exception:
                global_take_profit_pct = 0.0
            
            try:
                global_stop_loss_pct = float(self.stop_loss_pct_var.get())
            except Exception:
                global_stop_loss_pct = 0.0
            
            # Mevcut pozisyonları al
            positions = self.client.futures_position_information()
            for pos in positions:
                pos_symbol = pos.get('symbol')
                
                position_amt = float(pos.get('positionAmt', 0))
                if abs(position_amt) < 0.001:
                    continue  # Pozisyon yok
                
                entry_price = float(pos.get('entryPrice', 0))
                mark_price = float(pos.get('markPrice', 0))
                leverage = int(pos.get('leverage', 1))
                
                if entry_price == 0 or mark_price == 0:
                    continue
                
                # Kar/Zarar yüzdesini hesapla - KALDIRAÇ DAHİL!
                if position_amt > 0:  # LONG
                    pnl_pct = ((mark_price - entry_price) / entry_price) * 100 * leverage
                else:  # SHORT
                    pnl_pct = ((entry_price - mark_price) / entry_price) * 100 * leverage
                
                # Coin-specific değerleri al (öncelik), yoksa global değerleri kullan
                coin_specific_stop_loss = self.coin_stop_losses.get(pos_symbol, None)
                
                # Stop Loss: Önce coin-specific, sonra global
                if coin_specific_stop_loss is not None and coin_specific_stop_loss > 0:
                    stop_loss_pct = coin_specific_stop_loss
                    stop_loss_source = "Coin-Specific"
                else:
                    stop_loss_pct = global_stop_loss_pct
                    stop_loss_source = "Global"
                
                # Take Profit: Şu an sadece global (ileride coin-specific eklenebilir)
                take_profit_pct = global_take_profit_pct
                
                # Kar Al kontrolü
                if take_profit_pct > 0 and pnl_pct >= take_profit_pct:
                    self.log_message(f"[{pos_symbol}] ✅ Kar Al seviyesine ulaşıldı ({pnl_pct:.2f}% >= {take_profit_pct}%) | Kaldıraç: {leverage}x -> Pozisyon kapatılıyor")
                    self.close_symbol_positions(pos_symbol)
                    continue
                
                # Stop Loss kontrolü
                if stop_loss_pct > 0 and pnl_pct <= -stop_loss_pct:
                    self.log_message(f"[{pos_symbol}] 🛑 Stop Loss ({stop_loss_source}) seviyesine ulaşıldı ({pnl_pct:.2f}% <= -{stop_loss_pct}%) | Kaldıraç: {leverage}x -> Pozisyon kapatılıyor")
                    self.close_symbol_positions(pos_symbol)
                    continue
                    
        except Exception as e:
            self.log_message(f"Kar/Zarar kontrolü hatası: {e}")
    
    def execute_multi_coin_auto_trade(self, market_up, market_down, changes):
        """Seçili tüm coinler için otomatik işem kararları ver - Momentum kaybı korumalı"""
        try:
            now = time.time()
            cooldown = self.market_interval_seconds
            
            # Genel cooldown kontrolü
            if now - self.last_auto_action_time < cooldown:
                return
            
            # ⚠️ MOMENTUM KAYBI KONTROLÜ - Trading durdurulmuşsa trend değişimi veya momentum toparlanması bekle
            if self.trading_paused:
                # Tam trend değişimi kontrolü
                current_trend = 'up' if market_up else ('down' if market_down else 'neutral')
                
                if self.last_market_trend and current_trend != self.last_market_trend and current_trend != 'neutral':
                    # Trend değişti! (up → down veya down → up)
                    self.log_message(f"✅ TREND DEĞİŞTİ: {self.last_market_trend} → {current_trend} | Trading yeniden aktif!")
                    self.trading_paused = False
                    self.positive_momentum_count = 0  # Sayacı sıfırla
                    self.last_market_trend = current_trend
                else:
                    # Hala aynı trend veya nötr, bekle
                    return
            
            action_taken = False
            
            for symbol in self.selected_symbols:
                try:
                    base = self.get_base_symbol_from_binance(symbol)
                    momentum = self.symbol_momentum.get(symbol, {})
                    
                    coin_up = momentum.get('momentum_up', False)
                    coin_down = momentum.get('momentum_down', False)
                    
                    # Yeni mantık: Piyasa ve coin aynı yönde hareket ediyorsa pozisyon aç
                    if market_up and coin_up:
                        self.log_message(f"[{symbol}] 📈 LONG koşulu: Piyasa yükselişte + Coin 1h yükselişte -> LONG açılıyor")
                        self.ensure_long_position_multi(symbol)
                        action_taken = True
                        
                    elif market_down and coin_down:
                        self.log_message(f"[{symbol}] 📉 SHORT koşulu: Piyasa düşüşte + Coin 1h düşüşte -> SHORT açılıyor")
                        self.ensure_short_position_multi(symbol)
                        action_taken = True
                        
                    else:
                        # Piyasa ve coin uyumsuz -> yeni pozisyon açma, mevcut pozisyonları koru
                        coin_change_pct = momentum.get('change_percent', 0)
                        
                        # 1. Piyasa düşüyor ama coin düşmüyor (coin nötr veya pozitif)
                        if market_down and not coin_down:
                            self.log_message(f"[{symbol}] ⚠️ Uyumsuzluk: Piyasa düşüyor ama coin düşmüyor (1h: {coin_change_pct:+.2f}%) -> Yeni pozisyon açılmıyor, mevcut pozisyonlar korunuyor")
                        
                        # 2. Piyasa yükseliyor ama coin yükselmıyor (coin nötr veya negatif)
                        elif market_up and not coin_up:
                            self.log_message(f"[{symbol}] ⚠️ Uyumsuzluk: Piyasa yükseliyor ama coin yükselmıyor (1h: {coin_change_pct:+.2f}%) -> Yeni pozisyon açılmıyor, mevcut pozisyonlar korunuyor")
                        
                        # Not: Pozisyon kapatılmıyor, sadece yeni pozisyon açılmıyor
                            
                except Exception as e:
                    self.log_message(f"[{symbol}] işlem kararı hatası: {e}")
                    continue
            
            if action_taken:
                self.last_auto_action_time = now
                
        except Exception as e:
            self.log_message(f"Çoklu coin otomatik işlem hatası: {e}")
    
    def market_monitor_loop(self):
        """
        Piyasa analiz döngüsü - Market interval süresinde çalışır
        
        Bu döngü içinde:
        - Top 100 coin analizi
        - Piyasa breadth hesaplaması
        - Seçili coin kartlarının güncellenmesi
        - Hesap özeti kartlarının güncellenmesi (satır 3599)
        - Otomatik trading kararları
        
        Hesap Özeti artık bu döngü içinde güncellenir (piyasa kontrol süresi ile senkron)
        """
        while self.market_thread_running:
            try:
                interval = self.market_interval_seconds
                # Saat başı top100 (Paprika veya Binance fallback)
                symbols = self.get_top100_symbols_any()
                
                if symbols:
                    # İlk 100 coin için 1 saatlik değişimleri çek (CoinPaprika API)
                    usdt_syms = [s + 'USDT' for s in symbols[:100]]
                    self.market_service.fetch_futures_1h(usdt_syms)
                    changes = self.market_service.latest_changes
                    
                    # expose latest changes for UI
                    self.latest_changes = changes
                    # Sembol arama için önbellek
                    try:
                        self.all_symbols_cache = [s + 'USDT' for s in symbols]
                    except Exception:
                        pass
                    # Sembol listesini GUI'de güncelle
                    self.root.after(0, self.update_symbol_list)
                    
                    if changes:
                        # 1 saatlik değişime göre yükselen ve düşen coin sayılarını hesapla
                        rising_now = sum(1 for sym in usdt_syms if sym in changes and changes[sym] > 0)
                        falling_now = sum(1 for sym in usdt_syms if sym in changes and changes[sym] < 0)
                        neutral_now = sum(1 for sym in usdt_syms if sym in changes and changes[sym] == 0)  # Tam sıfır olanlar
                        total_coins = rising_now + falling_now + neutral_now  # Veri alınan coin sayısı
                        
                        # Piyasa trend eşiği kontrolü
                        market_up_now = False
                        market_down_now = False
                        state = None  # Varsayılan: nötr
                        
                        # Piyasa trend eşiğini al
                        try:
                            market_threshold = int(self.market_threshold_var.get())
                        except Exception:
                            market_threshold = 55  # varsayılan
                        
                        # Yeni mantık: Eşik değerine göre
                        if rising_now >= market_threshold and falling_now >= market_threshold:
                            # Her ikisi de eşik üzerinde -> Yükselen daha fazlaysa yükseliş, değilse düşüş
                            if rising_now > falling_now:
                                state = 'up'
                                market_up_now = True
                                self.log_message(f"✅ [Piyasa Yükseliyor] Yükselen: {rising_now} >= Eşik: {market_threshold} (Düşen: {falling_now})")
                            else:
                                state = 'down'
                                market_down_now = True
                                self.log_message(f"🔻 [Piyasa Düşüyor] Düşen: {falling_now} >= Eşik: {market_threshold} (Yükselen: {rising_now})")
                        elif rising_now >= market_threshold:
                            # Sadece yükselenler eşik üzerinde -> Piyasa Yükseliyor
                            state = 'up'
                            market_up_now = True
                            self.log_message(f"✅ [Piyasa Yükseliyor] Yükselen: {rising_now} >= Eşik: {market_threshold}")
                        elif falling_now >= market_threshold:
                            # Sadece düşenler eşik üzerinde -> Piyasa Düşüyor
                            state = 'down'
                            market_down_now = True
                            self.log_message(f"🔻 [Piyasa Düşüyor] Düşen: {falling_now} >= Eşik: {market_threshold}")
                        else:
                            # Hiçbiri eşik üzerinde değil -> Nötr
                            state = None
                            self.log_message(f"⚪ [Piyasa Nötr] Yükselen: {rising_now}, Düşen: {falling_now} (Eşik: {market_threshold}), Nötr: {neutral_now}, Toplam: {total_coins}")
                            
                        # İlk ölçüm bilgisi (sadece bilgi amaçlı)
                        if self.prev_rising_count is None:
                            self.log_message(f"📊 [İlk Ölçüm] Piyasa durumu tespit edildi")
                            
                        self.log_message(f"📊 [Piyasa Detay] Yükselen={rising_now} Düşen={falling_now} Nötr={neutral_now} Toplam={total_coins}/{len(usdt_syms)} (1h)")
                        
                        # UI'ı güncelle
                        if market_up_now:
                            self.root.after(0, lambda: self.set_market_status(self.tr('market_rising_text'), 'green'))
                        elif market_down_now:
                            self.root.after(0, lambda: self.set_market_status(self.tr('market_falling_text'), 'red'))
                        else:
                            self.root.after(0, lambda: self.set_market_status(self.tr('market_neutral_text'), 'neutral'))
                        
                        # ⚠️ MOMENTUM KAYBI KONTROLÜ (Kaydetmeden ÖNCE kontrol et!)
                        if self.prev_rising_count is not None and self.prev_falling_count is not None:
                            rising_change = rising_now - self.prev_rising_count
                            falling_change = falling_now - self.prev_falling_count
                            
                            # Momentum eşiğini al
                            try:
                                momentum_threshold = int(self.momentum_threshold_var.get())
                            except Exception:
                                momentum_threshold = 3  # varsayılan
                            
                            # LONG POZİSYONLAR: Yükselen sayısı eşik kadar düştü mü?
                            if market_up_now and rising_change <= -momentum_threshold and self.client:
                                self.log_message(f"🚨 MOMENTUM KAYBI TESPİT EDİLDİ! | Yükselen: {self.prev_rising_count} → {rising_now} ({rising_change:+d}) | LONG pozisyonlar kapatılıyor...")
                                self.trading_paused = True
                                self.positive_momentum_count = 0  # Sayacı sıfırla
                                self.last_market_trend = 'up'
                                # Tüm pozisyonları kapat
                                for symbol in self.selected_symbols:
                                    try:
                                        self.close_symbol_positions(symbol)
                                    except Exception as e:
                                        self.log_message(f"[{symbol}] Pozisyon kapatma hatası: {e}")
                                self.log_message(f"⏸️ TRADING DURAKLATILDI - Tüm pozisyonlar kapatıldı, trend değişimi veya momentum toparlanması bekleniyor")
                            
                            # SHORT POZİSYONLAR: Yükselen sayısı eşik kadar arttı mı?
                            elif market_down_now and rising_change >= momentum_threshold and self.client:
                                self.log_message(f"🚨 MOMENTUM KAYBI TESPİT EDİLDİ! | Yükselen: {self.prev_rising_count} → {rising_now} ({rising_change:+d}) | SHORT pozisyonlar kapatılıyor...")
                                self.trading_paused = True
                                self.positive_momentum_count = 0  # Sayacı sıfırla
                                self.last_market_trend = 'down'
                                # Tüm pozisyonları kapat
                                for symbol in self.selected_symbols:
                                    try:
                                        self.close_symbol_positions(symbol)
                                    except Exception as e:
                                        self.log_message(f"[{symbol}] Pozisyon kapatma hatası: {e}")
                                self.log_message(f"⏸️ TRADING DURAKLATILDI - Tüm pozisyonlar kapatıldı, trend değişimi veya momentum toparlanması bekleniyor")
                            
                            # 🔄 MOMENTUM TOPARLANMA KONTROLÜ - Trading duraklatıldıysa pozitif artış sayacı
                            elif self.trading_paused:
                                # Aynı trend içinde momentum toparlanıyor mu?
                                if self.last_market_trend == 'up' and market_up_now and rising_change > 0:
                                    # Yükseliş trendinde pozitif artış var
                                    
                                    # HIZLI TOPARLANMA: Tek seferde eşik kadar veya daha fazla artış
                                    if rising_change >= momentum_threshold:
                                        self.log_message(f"🚀 HIZLI TOPARLANMA: Yükselen {self.prev_rising_count} → {rising_now} ({rising_change:+d} >= {momentum_threshold}) | Trading yeniden aktif!")
                                        self.trading_paused = False
                                        self.positive_momentum_count = 0
                                    else:
                                        # Küçük artışlar - sayaç sistemi
                                        self.positive_momentum_count += 1
                                        self.log_message(f"📈 MOMENTUM TOPARLANMA: Yükselen {self.prev_rising_count} → {rising_now} ({rising_change:+d}) | Sayaç: {self.positive_momentum_count}/3")
                                        
                                        # 3 üst üste pozitif artış olursa trading yeniden aktif
                                        if self.positive_momentum_count >= 3:
                                            self.log_message(f"✅ MOMENTUM TOPARLANDI! (3 interval üst üste pozitif artış) | Trading yeniden aktif!")
                                            self.trading_paused = False
                                            self.positive_momentum_count = 0
                                        
                                elif self.last_market_trend == 'down' and market_down_now and falling_change > 0:
                                    # Düşüş trendinde düşen sayısı artıyor (toparlanma)
                                    
                                    # HIZLI TOPARLANMA: Tek seferde eşik kadar veya daha fazla artış
                                    if falling_change >= momentum_threshold:
                                        self.log_message(f"🚀 HIZLI TOPARLANMA: Düşen {self.prev_falling_count} → {falling_now} ({falling_change:+d} >= {momentum_threshold}) | Trading yeniden aktif!")
                                        self.trading_paused = False
                                        self.positive_momentum_count = 0
                                    else:
                                        # Küçük artışlar - sayaç sistemi
                                        self.positive_momentum_count += 1
                                        self.log_message(f"📉 MOMENTUM TOPARLANMA: Düşen {self.prev_falling_count} → {falling_now} ({falling_change:+d}) | Sayaç: {self.positive_momentum_count}/3")
                                        
                                        # 3 üst üste pozitif artış olursa trading yeniden aktif
                                        if self.positive_momentum_count >= 3:
                                            self.log_message(f"✅ MOMENTUM TOPARLANDI! (3 interval üst üste pozitif artış) | Trading yeniden aktif!")
                                            self.trading_paused = False
                                            self.positive_momentum_count = 0
                                        
                                else:
                                    # Negatif veya nötr değişim - sayacı sıfırla
                                    if self.positive_momentum_count > 0:
                                        self.log_message(f"⚠️ Momentum toparlanma kesintiye uğradı - Sayaç sıfırlandı")
                                        self.positive_momentum_count = 0
                        
                        # Trend'i kaydet (momentum kaybı yoksa)
                        if not self.trading_paused:
                            if market_up_now:
                                self.last_market_trend = 'up'
                            elif market_down_now:
                                self.last_market_trend = 'down'
                            else:
                                self.last_market_trend = 'neutral'
                        
                        # Kaydet (momentum kontrolünden SONRA)
                        self.prev_rising_count = rising_now
                        self.prev_falling_count = falling_now
                        self.market_trend_state = state
                        
                        # Seçili sembol durumu (eski sistem - artık kullanılmıyor)
                        base = self.get_base_symbol_from_binance(self.current_symbol)
                        sym_full = base + 'USDT'
                        coin_up = coin_down = False
                        if sym_full in changes:
                            cur = changes[sym_full]
                            prev = self.prev_symbol_change
                            # Coin yön kontrolü: cur > 0 = yükseliyor, cur < 0 = düşüyor
                            coin_up = cur > 0
                            coin_down = cur < 0
                            self.log_message(f"Momentum {base}: cur={cur:.2f}% prev={prev if prev is not None else 'None'} (1h)")
                            self.prev_symbol_change = cur
                            # Coin momentum analizi tamamlandı - UI'da gösterilmiyor
                        
                        # Çoklu coin momentum analizi
                        self.analyze_multi_coin_momentum(changes)
                        
                        # ✅ STOP LOSS ve KAR AL kontrolü (her zaman çalışır, oto trade açık olmasa da)
                        self.check_stop_loss_take_profit()
                        
                        # Otomatik işlem kararı - Çoklu coin için
                        if self.auto_trade_enabled and self.client and self.selected_symbols:
                            self.root.after(0, lambda: self.execute_multi_coin_auto_trade(market_up_now, market_down_now, changes))
                
                    # Seçilen coinlerin kutucuklarını güncelle (interval süresine göre)
                    self.root.after(0, self.update_selected_coins_cards)
                
                # ✅ HESAP ÖZETİ - Artık ayrı thread'de sürekli güncelleniyor (her 3 saniye)
                # Bu satır kaldırıldı - start_summary_monitor() otomatik günceller
                
                # Sağ üst köşe bilgilerini güncelle
                self.root.after(0, self.update_auto_trade_status)
                self.root.after(0, self.update_test_mode_status)
                
                # Piyasa kontrol süresine göre bekle
                # Hesap özeti artık ayrı thread'de sürekli güncelleniyor
                time.sleep(interval)
            except Exception as e:
                self.log_message(f"Piyasa izleme hatası: {e}")
                time.sleep(10)
    
    def get_top100_symbols_paprika(self):
        # Saatte 1 kez günceller ve coin100.txt'ye yazar
        try:
            now = time.time()
            if self.top100_symbols and now - self.top100_last_fetch < 3600:
                return self.top100_symbols
            url = "https://api.coinpaprika.com/v1/tickers"
            params = {"quotes": "USD"}
            headers = {"User-Agent": "BinanceFuturesGUI/1.0 (+contact: contact@example.com)"}
            resp = self.session.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code != 200:
                # fallback kullanılacak
                return self.top100_symbols
            data = resp.json()
            try:
                data_sorted = sorted(data, key=lambda x: int(x.get('rank', 999999)))[:100]
            except Exception:
                data_sorted = data[:100]
            syms = []
            for item in data_sorted:
                sym = item.get('symbol')
                if sym and sym.isalpha():
                    syms.append(sym.upper())
            self.top100_symbols = syms
            self.top100_last_fetch = now
            # Dosyaya yaz
            self.write_top100_file(syms)
            return self.top100_symbols
        except Exception:
            return self.top100_symbols
    
    def get_top100_symbols_from_binance(self):
        # Binance Futures USDT perpetual en yüksek hacimli 100 sembol
        try:
            now = time.time()
            if self.top100_symbols and now - self.top100_last_fetch < 3600:
                return self.top100_symbols
            # Tüm 24h ticker verisi
            tick = self.session.get("https://fapi.binance.com/fapi/v1/ticker/24hr", timeout=10)
            if tick.status_code != 200:
                return self.top100_symbols
            tickers = {t['symbol']: t for t in tick.json() if 'symbol' in t}
            # Perpetual USDT sembollerini filtrele
            ex = self.session.get("https://fapi.binance.com/fapi/v1/exchangeInfo", timeout=10)
            if ex.status_code != 200:
                return self.top100_symbols
            info = ex.json()
            syms_meta = []
            for s in info.get('symbols', []):
                try:
                    if s.get('contractType') == 'PERPETUAL' and s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING':
                        sym = s.get('symbol')
                        if sym in tickers:
                            qv = float(tickers[sym].get('quoteVolume', 0.0))
                            syms_meta.append((sym, qv))
                except Exception:
                    continue
            syms_meta.sort(key=lambda x: x[1], reverse=True)
            top = [sym[:-4] for sym, _ in syms_meta[:100] if sym.endswith('USDT')]
            if top:
                self.top100_symbols = top
                self.top100_last_fetch = now
                self.write_top100_file(top)
            return self.top100_symbols
        except Exception:
            return self.top100_symbols
    
    def get_top100_symbols_any(self):
        # Önce CoinPaprika, olmazsa Binance fallback
        syms = self.get_top100_symbols_paprika()
        if not syms or len(syms) < 50:
            syms = self.get_top100_symbols_from_binance()
        return syms
    
    def write_top100_file(self, syms):
        try:
            with open("coin100.txt", "w", encoding="utf-8") as f:
                for s in syms:
                    f.write(f"{s}\n")
            self.log_message("Top100 coin listesi coin100.txt dosyasına yazıldı.")
        except Exception as e:
            self.log_message(f"coin100.txt yazılamadı: {e}")
    
    def update_income_history(self):
        # Geçmiş işlemler alanı kaldırıldı
        pass
    
    def update_binance_cumulative_pnl(self):
        # Geçmiş işlemler alanı kaldırıldı
        pass
    
    def write_binance_totals_snapshot(self):
        # Geçmiş işlemler alanı kaldırıldı
        pass
    
    def manual_update_history(self):
        # Geçmiş işlemler alanı kaldırıldı
        pass
    
    def _get_assets_dir(self):
        import os
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
        os.makedirs(d, exist_ok=True)
        return d

    # Logo fonksiyonu kaldırıldı - sadece piyasa durumu gösteriliyor
    

    def _restore_prev_hover(self, tree, hover_attr, map_attr):
        prev = getattr(self, hover_attr, None)
        if prev and prev in getattr(self, map_attr, {}):
            try:
                orig = getattr(self, map_attr)[prev]
                tree.item(prev, tags=orig)
            except Exception:
                pass
        setattr(self, hover_attr, None)

    def _on_positions_tree_motion(self, event):
        self._tree_hover_generic(self.positions_tree, event, '_pos_hover_item', '_pos_row_tags')

    def _on_positions_tree_leave(self, event):
        self._restore_prev_hover(self.positions_tree, '_pos_hover_item', '_pos_row_tags')

    def _on_history_tree_motion(self, event):
        # Geçmiş işlemler alanı kaldırıldı
        pass

    def _on_history_tree_leave(self, event):
        # Geçmiş işlemler alanı kaldırıldı
        pass

    def _tree_hover_generic(self, tree, event, hover_attr, map_attr):
        row_id = tree.identify_row(event.y)
        if not row_id:
            self._restore_prev_hover(tree, hover_attr, map_attr)
            return
        current = getattr(self, hover_attr, None)
        if row_id == current:
            return
        # restore previous
        self._restore_prev_hover(tree, hover_attr, map_attr)
        # apply hover
        try:
            orig_tags = tree.item(row_id, 'tags') or ()
            getattr(self, map_attr)[row_id] = orig_tags
            tree.item(row_id, tags=('hover',))
            setattr(self, hover_attr, row_id)
        except Exception:
            pass

    def _init_treeview_sort(self, tree, columns):
        if not hasattr(self, '_tree_sort_state'):
            self._tree_sort_state = {}
        for col in columns:
            tree.heading(col, text=col, command=lambda c=col, t=tree: self._treeview_sort_by(t, c))

    def _treeview_sort_by(self, tree, col):
        # Determine state
        key = str(tree)
        state = self._tree_sort_state.get(key, {'col': None, 'asc': True})
        asc = not state['asc'] if state['col'] == col else True
        # Collect data
        items = []
        for iid in tree.get_children(''):
            val = tree.set(iid, col)
            try:
                v = float(val.replace('%','').replace('$','').replace(',',''))
            except Exception:
                v = val
            items.append((v, iid))
        items.sort(reverse=not asc)
        # Reorder and re-zebra
        for i, (_, iid) in enumerate(items):
            tree.move(iid, '', i)
            tag = 'odd' if (i % 2) else 'even'
            try:
                # keep hover if this is current hovered row
                current_hover = getattr(self, '_pos_hover_item', None)
                if tree is getattr(self, 'positions_tree', None) and iid == current_hover:
                    tree.item(iid, tags=('hover',))
                else:
                    tree.item(iid, tags=(tag,))
            except Exception:
                pass
        # Update heading arrows
        cols = tree['columns']
        for c in cols:
            label = c
            if c == col:
                label += ' ' + ('▲' if asc else '▼')
            tree.heading(c, text=label, command=lambda cc=c, t=tree: self._treeview_sort_by(t, cc))
        self._tree_sort_state[key] = {'col': col, 'asc': asc}

    # Banner background update function removed - only market status labels are used
    
    def set_market_status(self, text, color):
        # Update market status label only
        if color == 'green':
            self.market_status_label.config(bg='#22c55e', fg='#111827')
        elif color == 'red':
            self.market_status_label.config(bg='#ef4444', fg='#ffffff')
        else:
            self.market_status_label.config(bg='#374151', fg='#ffffff')
        self.market_status_label.config(text=text)
        self.save_settings_file()
    
    
    def update_auto_trade_status(self):
        """Oto Trade durumunu güncelle"""
        try:
            if self.auto_trade_enabled:
                self.auto_trade_status.config(text=self.tr('auto_trade_on_label'), fg='#10b981')
            else:
                self.auto_trade_status.config(text=self.tr('auto_trade_off_label'), fg='#ef4444')
        except Exception as e:
            self.log_message(f"Auto trade status güncelleme hatası: {e}")
    
    def update_test_mode_status(self):
        """Test/Canlı mod durumunu güncelle"""
        try:
            if hasattr(self, 'client') and self.client:
                # Environment değişkeninden kontrol et
                if hasattr(self, 'env_var') and self.env_var.get() == self.tr('env_test'):
                    self.test_mode_status.config(text=self.tr('mode_test'), fg='#f59e0b')
                else:
                    self.test_mode_status.config(text=self.tr('mode_live'), fg='#22c55e')
            else:
                self.test_mode_status.config(text=self.tr('mode_test'), fg='#6b7280')
        except Exception as e:
            self.log_message(f"Test mode status güncelleme hatası: {e}")
    
    # Symbol status function removed - only market status is shown
    
    def get_base_symbol_from_binance(self, symbol):
        # BTCUSDT -> BTC, ETHUSDT -> ETH, etc.
        bases = ["USDT", "BUSD", "USD", "TUSD", "USDC"]
        for b in bases:
            if symbol.endswith(b):
                return symbol[:-len(b)]
        return symbol
    
    # Symbol status update function removed - only market status is shown
    
    def on_env_change(self, event=None):
        # Ortam değiştiğinde alanları o ortama göre güncelle ve ayarları kaydet
        self._apply_api_fields_for_env()
        self.save_settings_file()
        # Ortam değişince PNL görünümlerini o ortama göre yenile
        try:
            self.last_income_fetch_ts = 0
            self.update_income_history()
            self.update_cumulative_pnl_label()
            self.write_totals_snapshot()
        except Exception:
            pass

    def on_language_change(self, event=None):
        # lang string like 'tr - Turkish'
        try:
            sel = self.lang_var.get().split(' - ')[0]
            if sel:
                self.lang_var.set(sel)
                self.current_language = sel  # Thread-safe dil kodu
        except Exception:
            pass
        self.apply_language()
        self.save_settings_file()
        
        # Haber başlığı ve haberleri yenile
        self.root.after(0, self.refresh_news)
    
    def on_interval_change(self, event=None):
        # sadece doğrulama ve kayıt
        try:
            val = int(self.market_interval_var.get())
            if val < 30:
                val = 30
                self.market_interval_var.set("30")
                self.log_message(f"⚠️ Minimum 30 saniye gereklidir (API limit koruması)")
            self.market_interval_seconds = val
            self.log_message(f"Piyasa kontrol süresi {val} saniye olarak ayarlandı")
        except Exception:
            self.market_interval_var.set("30")
            self.market_interval_seconds = 30
        self.save_settings_file()

    def on_leverage_change(self, event=None):
        try:
            lev = int(self.leverage_var.get())
        except Exception:
            lev = 1
        
        # Lisans kontrolü: Lisans yoksa veya süresi bitmişse max 1x
        if not self.license_valid and lev > 1:
            self.leverage_var.set("1")
            from tkinter import messagebox
            messagebox.showwarning(
                self.tr('license_leverage_warning_title'),
                self.tr('license_leverage_warning_msg')
            )
            return
        
        # Seçili tüm coinler için kaldıracı güncelle
        if hasattr(self, 'client') and self.client and hasattr(self, 'selected_symbols'):
            threading.Thread(target=self.update_leverage_for_all_coins, args=(lev,), daemon=True).start()
        
        self.save_settings_file()
    
    def update_leverage_for_all_coins(self, leverage):
        """Seçili tüm coinler için kaldıracı güncelle"""
        try:
            updated_count = 0
            for symbol in self.selected_symbols:
                try:
                    self.ensure_isolated_margin(symbol)
                    self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
                    updated_count += 1
                except Exception as e:
                    self.log_message(f"Kaldıraç güncelleme hatası {symbol}: {e}")
            
            if updated_count > 0:
                self.log_message(f"{updated_count} coin için kaldıraç {leverage}x olarak güncellendi")
        except Exception as e:
            self.log_message(f"Toplu kaldıraç güncelleme hatası: {e}")
    
    def on_target_change(self, event=None):
        # stop loss ve take profit değiştiğinde kaydet
        try:
            s = float(getattr(self, 'stop_loss_pct_var', tk.StringVar(value='0')).get())
            if s < 0:
                self.stop_loss_pct_var.set("0")
        except Exception:
            try:
                self.stop_loss_pct_var.set("0")
            except Exception:
                pass
        try:
            tp = float(getattr(self, 'take_profit_pct_var', tk.StringVar(value='0')).get())
            if tp < 0:
                self.take_profit_pct_var.set("0")
        except Exception:
            try:
                self.take_profit_pct_var.set("0")
            except Exception:
                pass
        self.save_settings_file()
    
    def on_balance_percent_change(self, event=None):
        """Bakiye yüzdesi değiştiğinde coin kartlarını güncelle"""
        try:
            # Yüzde validasyonu
            pct = float(self.balance_percent_var.get())
            if pct < 0:
                self.balance_percent_var.set("0")
            elif pct > 100:
                self.balance_percent_var.set("100")
        except Exception:
            self.balance_percent_var.set("10")
        
        # Coin kartlarını yeniden oluştur (yüzdeler güncellensin)
        if hasattr(self, 'selected_symbols') and self.selected_symbols:
            self.setup_selected_coins_cards()
        
        self.save_settings_file()
    
    def on_market_threshold_change(self, event=None):
        """Piyasa trend eşiği değiştiğinde kaydet"""
        try:
            # Validasyon
            val = int(self.market_threshold_var.get())
            if val < 1:
                self.market_threshold_var.set("1")
            elif val > 100:
                self.market_threshold_var.set("100")
        except Exception:
            self.market_threshold_var.set("55")
        
        # Ayarları kaydet
        self.save_settings_file()
    
    def on_momentum_change(self, event=None):
        """Momentum kaybı eşiği değiştiğinde kaydet"""
        try:
            # Validasyon
            val = int(self.momentum_threshold_var.get())
            if val < 1:
                self.momentum_threshold_var.set("1")
            elif val > 20:
                self.momentum_threshold_var.set("20")
        except Exception:
            self.momentum_threshold_var.set("3")
        
        self.save_settings_file()
    
    def reset_to_default_settings(self):
        """Default ayarları yükle"""
        try:
            # Kaldıraç: Lisans durumuna göre
            if self.license_valid:
                self.leverage_var.set("5")
            else:
                self.leverage_var.set("1")
            
            # Bakiye %
            self.balance_percent_var.set("100")
            
            # Piyasa Trend Eşiği
            self.market_threshold_var.set("60")
            
            # Momentum Kaybı Eşiği
            self.momentum_threshold_var.set("8")
            
            # Stop Loss (Zarar Durdur)
            self.stop_loss_pct_var.set("10")
            
            # Take Profit (Kar Al)
            self.take_profit_pct_var.set("3")
            
            # Piyasa kontrol süresi
            self.market_interval_var.set("60")
            self.market_interval_seconds = 60
            
            # Ayarları kaydet
            self.save_settings_file()
            
            # Kullanıcıya bilgi ver
            messagebox.showinfo(self.tr('info'), "✅ Default ayarlar yüklendi!")
            
        except Exception as e:
            self.log_message(f"Default ayarlar yüklenirken hata: {e}")
    
    def load_settings_file(self):
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            k, v = line.strip().split('=', 1)
                            if k == 'env':
                                self.env_var.set(v)
                            elif k == 'interval':
                                self.market_interval_var.set(v)
                            elif k == 'symbol':
                                self.symbol_var.set(v)
                            elif k == 'auto_trade':
                                # Ayarlarda aktif yazsa bile başlangıçta pasif kalsın
                                self._auto_trade_saved = (v == '1')
                            elif k == 'target_pnl':
                                pass  # Artık kullanılmıyor - Kar Al (%) var
                            elif k == 'neutral_close_pct':
                                pass  # Artık kullanılmıyor - Kaldırıldı
                            elif k == 'auto_percent':
                                pass  # Artık kullanılmıyor
                            elif k == 'stop_loss_pct':
                                try:
                                    self.stop_loss_pct_var.set(v)
                                except Exception:
                                    self.stop_loss_pct_var = tk.StringVar(value=v)
                            elif k == 'take_profit_pct':
                                try:
                                    self.take_profit_pct_var.set(v)
                                except Exception:
                                    self.take_profit_pct_var = tk.StringVar(value=v)
                            elif k == 'market_threshold':
                                try:
                                    self.market_threshold_var.set(v)
                                except Exception:
                                    self.market_threshold_var = tk.StringVar(value=v)
                            elif k == 'lang':
                                self.lang_var.set(v)
                            elif k == 'license':
                                self.license_var.set(v)
                            elif k == 'license_activation_date':
                                try:
                                    self.license_activation_date = float(v)
                                except Exception:
                                    self.license_activation_date = None
                            elif k == 'leverage':
                                self.leverage_var.set(v)
                            elif k == 'position_size':
                                # Eski sistem - artık kullanılmıyor
                                pass
                            elif k == 'balance_percent':
                                self.balance_percent_var.set(v)
                            elif k == 'momentum_threshold':
                                try:
                                    # UI elementi varsa güncelle, yoksa kaydet
                                    if hasattr(self, 'momentum_threshold_var'):
                                        self.momentum_threshold_var.set(v)
                                    else:
                                        # UI henüz oluşturulmamış, geçici olarak sakla
                                        self._pending_momentum_threshold = v
                                except Exception:
                                    if hasattr(self, 'momentum_threshold_var'):
                                        self.momentum_threshold_var = tk.StringVar(value=v)
                                    else:
                                        self._pending_momentum_threshold = v
                            elif k == 'selected_symbols':
                                # Seçili coinleri yükle (virgülle ayrılmış)
                                symbols = [s.strip() for s in v.split(',') if s.strip()]
                                if symbols:  # Eğer liste boş değilse
                                    self.selected_symbols = symbols
                                    self.log_message(f"🔄 Ayarlardan yüklenen coinler: {self.selected_symbols}")
                            elif k == 'coin_stop_losses':
                                # Her coin için özel stop loss yüzdelerini yükle
                                try:
                                    import json
                                    self.coin_stop_losses = json.loads(v)
                                    self.log_message(f"🔄 Coin-specific stop loss değerleri yüklendi: {self.coin_stop_losses}")
                                except Exception as e:
                                    self.log_message(f"⚠️ Coin stop loss yükleme hatası: {e}")
                                    self.coin_stop_losses = {}
                            # news_token artık kullanılmıyor - Sabit token
            # Lisans otomatik doğrula (varsa)
            try:
                if (self.license_var.get() or '').strip():
                    self.license_valid = self.validate_license(self.license_var.get())
                    if self.license_valid:
                        self.license_status_lbl.config(text=self.tr('license_status_active_short'), foreground="#10b981")
                        if hasattr(self, 'activate_btn'):
                            self.activate_btn.config(text=f"✔ {self.tr('license_active_btn')}")
                    else:
                        self.license_status_lbl.config(text=self.tr('license_status_invalid'), foreground="#f87171")
            except Exception:
                pass
            
            # Lisans kontrolü: Lisans yoksa kaldıracı 1x'e sabitle
            if not self.license_valid:
                try:
                    lev = int(self.leverage_var.get())
                    if lev > 1:
                        self.leverage_var.set("1")
                        self.log_message(self.tr('license_leverage_limited_log'))
                except Exception:
                    self.leverage_var.set("1")
            
            # Başlangıçta oto trade DAİMA kapalı
            self.auto_trade_enabled = False
            # UI yansıtma
            try:
                self.auto_btn.config(style='AutoOff.TButton')
                self.auto_status_label.config(text=self.tr('auto_off'))
            except Exception:
                pass
            self.apply_language()
            self.update_idletasks_safe()
        except Exception as e:
            self.log_message(f"Ayarlar yüklenemedi: {e}")
    
    def save_settings_file(self):
        try:
            import json
            settings = {
                'env': self.env_var.get(),
                'interval': self.market_interval_var.get(),
                'symbol': self.symbol_var.get(),
                'auto_trade': '1' if self.auto_trade_enabled else '0',
                'stop_loss_pct': getattr(self, 'stop_loss_pct_var', tk.StringVar(value='0')).get(),
                'take_profit_pct': getattr(self, 'take_profit_pct_var', tk.StringVar(value='0')).get(),
                'balance_percent': self.balance_percent_var.get(),
                'market_threshold': getattr(self, 'market_threshold_var', tk.StringVar(value='55')).get(),
                'momentum_threshold': getattr(self, 'momentum_threshold_var', tk.StringVar(value='3')).get(),
                'leverage': self.leverage_var.get(),
                'market_status': self.market_status_label.cget('text'),
                'symbol_status': 'N/A',
                'lang': self.lang_var.get(),
                'license': self.license_var.get(),
                'license_activation_date': str(self.license_activation_date) if self.license_activation_date else '',
                'selected_symbols': ','.join(self.selected_symbols),
                'coin_stop_losses': json.dumps(self.coin_stop_losses)
            }
            # değişiklik yoksa yazma
            if settings == self.last_saved_settings:
                return
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                for k, v in settings.items():
                    f.write(f"{k}={v}\n")
            self.last_saved_settings = settings
        except Exception as e:
            self.log_message(f"Ayarlar kaydedilemedi: {e}")
    
    def manual_save_settings(self):
        self.save_settings_file()
        messagebox.showinfo(self.tr('info'), self.tr('settings_saved'))

    def open_license_site(self):
        try:
            import webbrowser
            webbrowser.open('https://license.planc.space/')
        except Exception:
            pass

    def show_close_warning_dialog(self, open_positions_count):
        """
        Açık pozisyon uyarı dialogu göster
        Tamam butonu: Sadece dialogu kapat (pozisyonlar açık kalır)
        Yine de Kapat butonu: Pozisyonları açık bırakarak programı kapat
        """
        try:
            # Dialog penceresi oluştur
            dialog = tk.Toplevel(self.root)
            dialog.title(self.tr('close_positions_warning_title'))
            dialog.geometry('500x280')
            dialog.configure(bg='#1a1d23')
            dialog.resizable(False, False)
            
            # Pencereyi ortala
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
            y = (dialog.winfo_screenheight() // 2) - (280 // 2)
            dialog.geometry(f'500x280+{x}+{y}')
            
            # Modal yap
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Ana frame
            main_frame = tk.Frame(dialog, bg='#1a1d23')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Uyarı ikonu ve mesaj
            icon_label = tk.Label(main_frame, text="⚠️", font=('Segoe UI', 48), 
                                 bg='#1a1d23', fg='#f59e0b')
            icon_label.pack(pady=(0, 10))
            
            # Başlık
            title_label = tk.Label(main_frame, 
                                  text=self.tr('close_positions_warning_title'),
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#1a1d23', fg='#ffffff')
            title_label.pack(pady=(0, 10))
            
            # Mesaj
            message = self.tr('close_positions_warning_msg').format(count=open_positions_count)
            msg_label = tk.Label(main_frame, 
                                text=message,
                                font=('Segoe UI', 10),
                                bg='#1a1d23', fg='#9ca3af',
                                wraplength=400,
                                justify='center')
            msg_label.pack(pady=(0, 20))
            
            # Buton frame - Ortalanmış
            btn_frame = tk.Frame(main_frame, bg='#1a1d23')
            btn_frame.pack(pady=(10, 0))
            
            # Tamam butonu (SOLDA) - Sadece dialogu kapat
            def cancel_close():
                dialog.destroy()
            
            ok_btn = tk.Button(btn_frame, 
                               text=f"✓ {self.tr('ok_button')}",
                               command=cancel_close,
                               font=('Segoe UI', 10, 'bold'),
                               bg='#2563eb',
                               fg='#ffffff',
                               activebackground='#1d4ed8',
                               activeforeground='#ffffff',
                               cursor='hand2',
                               relief='raised',
                               bd=2,
                               padx=20,
                               pady=10)
            ok_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Yine de Kapat butonu (SAĞDA) - Programı kapat
            def close_program():
                dialog.destroy()
                self.close_attempt_count = 2  # Sayacı atla
                self.on_closing()  # Gerçekten kapat
            
            close_btn = tk.Button(btn_frame, 
                                  text=f"🔴 {self.tr('force_close_button')}",
                                  command=close_program,
                                  font=('Segoe UI', 10, 'bold'),
                                  bg='#dc2626',
                                  fg='#ffffff',
                                  activebackground='#b91c1c',
                                  activeforeground='#ffffff',
                                  cursor='hand2',
                                  relief='raised',
                                  bd=2,
                                  padx=20,
                                  pady=10)
            close_btn.pack(side=tk.LEFT)
            
            # ESC tuşu ile kapat
            dialog.bind('<Escape>', lambda e: cancel_close())
            
        except Exception as e:
            self.log_message(f"Dialog gösterme hatası: {e}")
    
    def on_window_resize(self, event=None):
        """Window resize olduğunda buton metinlerini ve font boyutlarını responsive yap"""
        try:
            # Sadece root window için çalış (child widget'lar için değil)
            if event and event.widget != self.root:
                return
            
            # Debounce: Çok sık çalışmasın
            if hasattr(self, '_resize_timer'):
                try:
                    self.root.after_cancel(self._resize_timer)
                except:
                    pass
            
            # 100ms sonra gerçekten güncelle
            self._resize_timer = self.root.after(100, self._do_resize_buttons)
                
        except Exception as e:
            pass  # Sessizce hataları yoksay
    
    def _do_resize_buttons(self):
        """Gerçek resize işlemini yap"""
        try:
            # Window genişliğini al
            width = self.root.winfo_width()
            
            # Genişlik eşiklerine göre buton metinlerini ve font boyutunu ayarla
            # Geniş ekran (>1400px): Tam metinler, normal font
            # Orta ekran (1000-1400px): Orta metinler, küçük font
            # Dar ekran (<1000px): Kısa metinler, çok küçük font
            
            if width > 1600:
                # Çok geniş ekran - tam metinler, normal font (10)
                font_size = 10
                padding = 8
                texts = {
                    'close_all': self.tr('close_all_trades'),
                    'close_selected': self.tr('close_selected_trade'),
                    'auto': self.tr('auto_trade_btn'),
                    'save': self.tr('save_settings_btn'),
                    'refresh': self.tr('refresh_btn'),
                    'refresh_summary': self.tr('refresh_summary_btn'),
                    'update': self.tr('update_btn'),
                    'guide': self.tr('user_guide_btn'),
                    'add_selected': self.tr('add_selected'),
                    'remove_selected': self.tr('remove_selected')
                }
            elif width > 1300:
                # Geniş ekran - kısaltılmış metinler, küçük font (9)
                font_size = 9
                padding = 6
                texts = {
                    'close_all': '[X] Tümü',
                    'close_selected': '[X] Seçili',
                    'auto': '>> Oto',
                    'save': '[S] Kaydet',
                    'refresh': '[R] Yenile',
                    'refresh_summary': '[≡] Özet',
                    'update': '[↓] Güncelle',
                    'guide': '[?] Kılavuz',
                    'add_selected': '+ Seçilenleri Ekle',
                    'remove_selected': '- Seçilenleri Kaldır'
                }
            elif width > 1000:
                # Orta ekran - daha kısa metinler, daha küçük font (8)
                font_size = 8
                padding = 4
                texts = {
                    'close_all': '[X] Tüm',
                    'close_selected': '[X] Seç',
                    'auto': '>> Oto',
                    'save': '[S] Kaydet',
                    'refresh': '[R] Yenile',
                    'refresh_summary': '[≡] Özet',
                    'update': '[↓] Güncelle',
                    'guide': '[?] Kılavuz',
                    'add_selected': '+ Ekle',
                    'remove_selected': '- Kaldır'
                }
            elif width > 800:
                # Dar ekran - çok kısa metinler, küçük font (7)
                font_size = 7
                padding = 2
                texts = {
                    'close_all': '[X] Tüm',
                    'close_selected': '[X] Seç',
                    'auto': '>> Oto',
                    'save': '[S]',
                    'refresh': '[R]',
                    'refresh_summary': '[≡]',
                    'update': '[↓]',
                    'guide': '[?]',
                    'add_selected': '+ Ekle',
                    'remove_selected': '- Kaldır'
                }
            else:
                # Çok dar ekran - sadece ikonlar, çok küçük font (7)
                font_size = 7
                padding = 2
                texts = {
                    'close_all': '[X]',
                    'close_selected': '[X]',
                    'auto': '>>',
                    'save': '[S]',
                    'refresh': '[R]',
                    'refresh_summary': '[≡]',
                    'update': '[↓]',
                    'guide': '[?]',
                    'add_selected': '+',
                    'remove_selected': '-'
                }
            
            # ttk.Style için responsive font stilleri ve padding oluştur
            style = ttk.Style()
            button_font = ('Segoe UI', font_size, 'bold')
            
            # Her stil için font ve padding güncelle (TÜM butonlar)
            # Dikey padding 8 (önceki 5'ten %60 artış - daha iyi görünüm için)
            vertical_padding = 8
            style.configure('Danger.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('Warning.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('AutoOff.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('AutoOn.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('Save.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('Refresh.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('Summary.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('Update.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('Modern.TButton', font=button_font, padding=(padding, vertical_padding))
            # Sol panel butonları da aynı boyutta
            style.configure('Accent.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('Connect.Connected.TButton', font=button_font, padding=(padding, vertical_padding))
            style.configure('Connect.Disconnected.TButton', font=button_font, padding=(padding, vertical_padding))
            
            # Her bir butonu güncelle (sadece text) - Ana butonlar ve sol panel butonlar
            buttons = [
                (self.close_all_btn, 'close_all'),
                (self.close_selected_btn, 'close_selected'),
                (self.auto_btn, 'auto'),
                (self.save_settings_btn, 'save'),
                (self.refresh_btn, 'refresh'),
                (self.refresh_summary_btn, 'refresh_summary'),
                (self.update_btn, 'update'),
                (self.user_guide_btn, 'guide'),
                (self.select_all_btn, 'add_selected'),
                (self.clear_selection_btn, 'remove_selected')
            ]
            
            for btn, key in buttons:
                try:
                    btn.config(text=texts[key])
                except:
                    pass
                        
        except Exception as e:
            pass  # Sessizce hataları yoksay
    
    def show_user_guide(self):
        """Kullanım kılavuzunu göster"""
        try:
            # Yeni pencere oluştur
            guide_window = tk.Toplevel(self.root)
            guide_window.title(self.tr('user_guide_title'))
            guide_window.geometry("900x700")
            guide_window.configure(bg='#111827')
            
            # Ana frame
            main_frame = ttk.Frame(guide_window, style='Dark.TFrame')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Başlık
            title_label = tk.Label(main_frame, 
                                  text=self.tr('user_guide_title'),
                                  font=('Segoe UI', 14, 'bold'),
                                  bg='#111827', fg='#ffffff')
            title_label.pack(pady=(0, 10))
            
            # Scrollable text frame
            text_frame = tk.Frame(main_frame, bg='#1f2937')
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Text widget
            text_widget = tk.Text(text_frame,
                                wrap=tk.WORD,
                                font=('Consolas', 10),
                                bg='#1f2937',
                                fg='#e5e7eb',
                                padx=20,
                                pady=20,
                                yscrollcommand=scrollbar.set,
                                relief=tk.FLAT)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)
            
            # Kullanım kılavuzu içeriğini ekle
            guide_content = self.tr('user_guide_content')
            text_widget.insert('1.0', guide_content)
            text_widget.config(state=tk.DISABLED)  # Sadece okunabilir yap
            
            # Kapat butonu
            close_btn = ttk.Button(main_frame,
                                  text=f"✖ {self.tr('cancel')}",
                                  command=guide_window.destroy,
                                  style='Modern.TButton')
            close_btn.pack(pady=(10, 0))
            
            # Pencereyi ortala
            guide_window.update_idletasks()
            x = (guide_window.winfo_screenwidth() // 2) - (900 // 2)
            y = (guide_window.winfo_screenheight() // 2) - (700 // 2)
            guide_window.geometry(f"900x700+{x}+{y}")
            
            # Pencereyi üstte tut
            guide_window.transient(self.root)
            guide_window.grab_set()
            
        except Exception as e:
            self.log_message(f"Kullanım kılavuzu gösterilirken hata: {e}")
            messagebox.showerror(self.tr('error'), f"Kullanım kılavuzu gösterilemedi: {e}")

    def get_machine_id(self) -> str:
        try:
            # Prefer Windows MachineGuid
            import sys
            if sys.platform.startswith('win'):
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Cryptography") as k:
                        v, _ = winreg.QueryValueEx(k, "MachineGuid")
                        if v:
                            return str(v)
                except Exception:
                    pass
            # Fallback to MAC-based UUID
            import uuid
            mac = uuid.getnode()
            return f"MAC-{mac:012x}"
        except Exception:
            return "UNKNOWN"

    def validate_license(self, token: str) -> bool:
        try:
            token = (token or '').strip()
            tl = token.lower()
            # Özel kural: sadece 'planc.space' ile başlayan anahtarlar kabul edilir
            if not tl.startswith('planc.space'):
                return False
            
            # Aktivasyon tarihi kontrolü (1 yıl = 365 gün)
            if self.license_activation_date:
                import time
                now_ts = time.time()
                days_passed = (now_ts - self.license_activation_date) / 86400  # 1 gün = 86400 saniye
                if days_passed > 365:
                    self.log_message(f"Lisans süresi dolmuş (Geçen: {int(days_passed)} gün)")
                    return False
            
            # ⚠️ GÜVENLİK: SADECE KRİPTOGRAFİK İMZALI LİSANSLAR GEÇERLİ
            # ⚠️ YETKİSİZ LİSANSLAR BOT'UN YANLIŞ İŞLEM AÇMASINA NEDEN OLABİLİR!
            # Format: planc.space.<payload>.<signature>
            
            # 🔧 TEST/DEVELOPMENT MODU
            if not verify_license or not PUBLIC_KEY_B64:
                # Public key yoksa basit format kontrolü ile geçir (sadece test için!)
                if len(token) > 11:  # 'planc.space' + minimum karakter
                    self.license_info = {
                        'edition': 'dev',
                        'features': ['auto', 'ui', 'unlimited'],
                        'mode': 'development'
                    }
                    self.log_message("✅ Test/Geliştirme lisansı aktif! (Tüm özellikler açık)")
                    self.log_message("⚠️  Production kullanımı için gerçek lisans sistemi gereklidir!")
                    return True
                else:
                    self.log_message("❌ Geçersiz lisans formatı!")
                    return False
            
            rest = token[len('planc.space'):].lstrip()
            if not rest or not rest.startswith('.'):
                self.log_message("❌ Geçersiz lisans formatı! Sadece resmi kaynaklardan lisans alın.")
                self.log_message("🌐 Resmi lisans: https://license.planc.space/")
                return False
            
            signed = rest[1:]
            ok, payload_or_err = verify_license(signed, PUBLIC_KEY_B64)
            if not ok:
                self.log_message(f"❌ Lisans imzası geçersiz! ({payload_or_err})")
                self.log_message("⚠️  YETKİSİZ LİSANSLAR KULLANMAYIN - BOT YANLIŞ İŞLEMLER AÇABİLİR!")
                self.log_message("🌐 Sadece resmi kaynak: https://license.planc.space/")
                return False
            
            payload = payload_or_err
            # payload controls: machine and expiry
            mid = payload.get('machine')
            exp = float(payload.get('exp', 0))
            now_ts = time.time()
            if mid and mid != self.get_machine_id():
                self.log_message("❌ Lisans bu makine için geçerli değil!")
                return False
            if exp and now_ts > exp:
                self.log_message("❌ Lisans süresi dolmuş!")
                return False
            self.license_info = payload
            self.log_message("✅ Lisans doğrulandı ve aktif edildi!")
            return True
        except Exception as e:
            self.log_message(f"Lisans doğrulama hatası: {e}")
            return False

    def activate_license(self):
        key = self.license_var.get()
        
        # Eğer lisans zaten aktifse ve butona basıldıysa kalan günleri göster
        if self.license_valid and self.license_activation_date:
            import time
            now_ts = time.time()
            days_passed = (now_ts - self.license_activation_date) / 86400
            days_remaining = max(0, 365 - int(days_passed))
            
            from tkinter import messagebox
            if days_remaining > 0:
                messagebox.showinfo(
                    self.tr('license'),
                    f"✅ Lisans Aktif\n\n"
                    f"📅 Kalan Süre: {days_remaining} gün\n"
                    f"🗓️ Aktivasyon Tarihi: {time.strftime('%d.%m.%Y', time.localtime(self.license_activation_date))}\n"
                    f"📆 Bitiş Tarihi: {time.strftime('%d.%m.%Y', time.localtime(self.license_activation_date + 365*86400))}"
                )
            else:
                messagebox.showwarning(
                    self.tr('license'),
                    f"⚠️ Lisans Süresi Dolmuş\n\n"
                    f"📅 Dolma Tarihi: {time.strftime('%d.%m.%Y', time.localtime(self.license_activation_date + 365*86400))}\n\n"
                    f"Yeni lisans almak için:\nhttps://license.planc.space/"
                )
            return
        
        # Yeni aktivasyon
        self.license_valid = self.validate_license(key)
        if self.license_valid:
            # İlk aktivasyon - tarihi kaydet
            if not self.license_activation_date:
                import time
                self.license_activation_date = time.time()
                self.log_message(f"✅ Lisans aktive edildi (1 yıl geçerli)")
            
            self.license_status_lbl.config(text=self.tr('license_status_active_short'), foreground="#10b981")
            try:
                if hasattr(self, 'activate_btn'):
                    self.activate_btn.config(text=f"✔ {self.tr('license_active_btn')}")
            except Exception:
                pass
            self.save_settings_file()
            
            # Başarı mesajı
            from tkinter import messagebox
            messagebox.showinfo(
                self.tr('success'),
                "✅ Lisans başarıyla aktive edildi!\n\n"
                "📅 Süre: 1 yıl (365 gün)\n"
                "🔄 Kalan süreyi görmek için butona tekrar basabilirsiniz."
            )
        else:
            self.license_status_lbl.config(text=self.tr('license_status_invalid'), foreground="#f87171")
            try:
                if hasattr(self, 'activate_btn'):
                    self.activate_btn.config(text=f"✔ {self.tr('activate')}")
            except Exception:
                pass

    def warn_license_required(self):
        msg = f"{self.tr('license_required')}\n{self.tr('click_to_buy')}"
        res = messagebox.showwarning(self.tr('license'), msg)
        # Keep a clickable label in license box already

    def tr(self, key):
        lang = self.lang_var.get() or 'tr'
        # Dil kodunu ayıkla (örn: "tr - Türkçe" -> "tr")
        if ' - ' in lang:
            lang = lang.split(' - ')[0]
        try:
            return get_text(lang, key)
        except Exception:
            return key

    def _add_help_icon(self, parent, help_key: str):
        try:
            icon = tk.Label(parent, text='?', fg='#60a5fa', bg='#111827', cursor='question_arrow')
            Tooltip(icon, lambda k=help_key: self.tr(k))
            icon.pack(side=tk.LEFT, padx=(6,0))
            return icon
        except Exception:
            return None

    def _apply_api_fields_for_env(self):
        try:
            env = self.env_code() if hasattr(self, 'env_code') else ('test' if (self.env_var.get() == 'Test') else 'live')
            cfg = getattr(self, '_api_cfg_all', {}) or {}
            sec = cfg.get(env, {}) if isinstance(cfg, dict) else {}
            # Mevcut yazıyı tamamen silmeden önce değişiklik yap
            try:
                self.api_key_entry.delete(0, tk.END)
                self.api_key_entry.insert(0, sec.get('api_key', ''))
                self.api_secret_entry.delete(0, tk.END)
                self.api_secret_entry.insert(0, sec.get('api_secret', ''))
            except Exception:
                pass
        except Exception:
            pass

    def apply_language(self):
        try:
            # API bağlantısı kontrolü - dil değişirken bağlantı korunmalı
            api_was_connected = self.client is not None
            
            # Buttons
            if hasattr(self, 'connect_btn'):
                self.connect_btn.config(text=self.tr('connect'))
            if hasattr(self, 'refresh_list_btn'):
                self.refresh_list_btn.config(text=self.tr('refresh_list'))
            if hasattr(self, 'long_btn'):
                self.long_btn.config(text=self.tr('long'))
            if hasattr(self, 'short_btn'):
                self.short_btn.config(text=self.tr('short'))
            if hasattr(self, 'close_all_btn'):
                self.close_all_btn.config(text=self.tr('close_all_trades'))
            if hasattr(self, 'close_selected_btn'):
                self.close_selected_btn.config(text=self.tr('close_selected_trade'))
            if hasattr(self, 'auto_btn'):
                self.auto_btn.config(text=self.tr('auto_trade_btn'))
            # save_settings_btn kaldırıldı - sol panelde
            if hasattr(self, 'save_settings_btn_bottom'):
                self.save_settings_btn_bottom.config(text=f"💾 {self.tr('save_settings_btn')}")
            if hasattr(self, 'default_settings_btn'):
                self.default_settings_btn.config(text=f"🔄 {self.tr('default_settings_btn')}")
            if hasattr(self, 'refresh_btn'):
                self.refresh_btn.config(text=self.tr('refresh_btn'))
            if hasattr(self, 'refresh_summary_btn'):
                self.refresh_summary_btn.config(text=self.tr('refresh_summary_btn'))
            if hasattr(self, 'update_btn'):
                self.update_btn.config(text=self.tr('update_btn'))
            if hasattr(self, 'user_guide_btn'):
                self.user_guide_btn.config(text=f"📖 {self.tr('user_guide_btn')}")
            if hasattr(self, 'activate_btn'):
                self.activate_btn.config(text=(f"✔ {self.tr('license_active_btn')}" if self.license_valid else f"✔ {self.tr('activate')}"))
            if hasattr(self, 'get_license_btn'):
                try:
                    self.get_license_btn.config(text=f"🛒 {self.tr('get_license')}")
                except Exception:
                    pass
            if hasattr(self, 'select_all_btn'):
                self.select_all_btn.config(text=self.tr('add_selected'))
            if hasattr(self, 'clear_selection_btn'):
                self.clear_selection_btn.config(text=self.tr('remove_selected'))
            # Frames titles
            # chart_frame kaldırıldı
            # Status strings will be translated on next update via tr() usage
            # Left-pane labels
            if hasattr(self, 'env_label_lbl'):
                self.env_label_lbl.config(text=f"🌐 {self.tr('env_label')}")
            if hasattr(self, 'language_label'):
                self.language_label.config(text=f"🌍 {self.tr('language_label')}")
            if hasattr(self, 'api_key_lbl'):
                self.api_key_lbl.config(text=f"🗝️ {self.tr('api_key')}")
            if hasattr(self, 'api_secret_lbl'):
                self.api_secret_lbl.config(text=f"🔒 {self.tr('api_secret')}")
            if hasattr(self, 'auto_status_label'):
                self.auto_status_label.config(text=self.tr('auto_on') if self.auto_trade_enabled else self.tr('auto_off'))
            if hasattr(self, 'lev_lbl'):
                self.lev_lbl.config(text=f"📈 {self.tr('leverage_label')}")
            if hasattr(self, 'pos_size_lbl'):
                self.pos_size_lbl.config(text=f"💰 {self.tr('balance_percent_label')}")
            if hasattr(self, 'market_int_lbl'):
                self.market_int_lbl.config(text=f"⏱️ {self.tr('market_interval_sec')}")
            # target_lbl kaldırıldı - Kar Al (%) kullanılıyor
            # neutral_lbl kaldırıldı - Nötr Kapat (%) kaldırıldı
            if hasattr(self, 'stop_lbl'):
                self.stop_lbl.config(text=f"🛑 {self.tr('stop_loss_pct_label')}")
            if hasattr(self, 'take_profit_lbl'):
                self.take_profit_lbl.config(text=f"✅ {self.tr('take_profit_pct_label')}")
            if hasattr(self, 'trading_frame'):
                self.trading_frame.configure(text=f"🛠️ {self.tr('trading')}")
            if hasattr(self, 'api_frame'):
                self.api_frame.configure(text=f"🔑 {self.tr('api') if hasattr(self, 'tr') else 'API'}")
            if hasattr(self, 'lic_frame'):
                self.lic_frame.configure(text=f"🔐 {self.tr('license')}")
            if hasattr(self, 'license_code_label'):
                self.license_code_label.config(text=self.tr('license_code'))
            if hasattr(self, 'market_threshold_lbl'):
                self.market_threshold_lbl.config(text=f"📊 {self.tr('market_threshold_label')}")
            if hasattr(self, 'momentum_lbl'):
                self.momentum_lbl.config(text=f"⚡ {self.tr('momentum_threshold_label')}")
            if hasattr(self, 'search_lbl'):
                self.search_lbl.config(text=self.tr('search_label'))
            if hasattr(self, 'account_frame'):
                self.account_frame.configure(text=f"💼 {self.tr('account_info')}")
            if hasattr(self, 'symbol_frame'):
                self.symbol_frame.configure(text=f"🔁 {self.tr('multi_coin_selection')}")
            if hasattr(self, 'price_frame'):
                self.price_frame.configure(text=f"📊 {self.tr('selected_coin_info')}")
            if hasattr(self, 'selected_coins_frame'):
                self.selected_coins_frame.configure(text=f"🎯 {self.tr('selected_coins_title')}")
            if hasattr(self, 'pos_title_label'):
                self.pos_title_label.config(text=f"📂 {self.tr('open_positions_title')}")
            if hasattr(self, 'news_title_label'):
                self.news_title_label.config(text=f"📰 {self.tr('crypto_news')}")
            if hasattr(self, 'summary_frame'):
                self.summary_frame.configure(text=f"📊 {self.tr('account_summary')}")
            # Özet kartlarını yeniden oluştur - önce eski kartları temizle
            if hasattr(self, 'summary_cards'):
                # summary_frame içindeki tüm widget'ları temizle
                for widget in self.summary_frame.winfo_children():
                    widget.destroy()
                # Yeni dilde kartları oluştur
                self.setup_modern_summary_cards(self.summary_frame)
                # API'den güncel verileri çek ve kartları güncelle
                if hasattr(self, 'client') and self.client:
                    self.root.after(100, self.update_summary_cards)
            # Pozisyon tablosu başlıklarını güncelle
            if hasattr(self, 'positions_tree'):
                column_headers = {
                    "Select": "☑",  # Checkbox başlığı dil bağımsız
                    "Symbol": self.tr('position_symbol'),
                    "Side": self.tr('position_side'),
                    "Size": self.tr('position_size'),
                    "Entry Price": self.tr('position_entry_price'),
                    "Leverage": self.tr('position_leverage'),
                    "PNL": self.tr('position_pnl')
                }
                for col in ["Select", "Symbol", "Side", "Size", "Entry Price", "Leverage", "PNL"]:
                    self.positions_tree.heading(col, text=column_headers.get(col, col), anchor="center")
            if hasattr(self, 'history_frame'):
                self.history_frame.configure(text=f"📜 {self.tr('history')}")
            
            # Üst banner dinamik alanlarını güncelle
            if hasattr(self, 'auto_trade_status'):
                self.update_auto_trade_status()
            if hasattr(self, 'test_mode_status'):
                self.update_test_mode_status()
            # Piyasa durumu label'ını güncelle - mevcut duruma göre
            if hasattr(self, 'market_status_label'):
                current_text = self.market_status_label.cget('text')
                # Mevcut duruma göre çevrilmiş metni belirle
                if 'neutral' in current_text.lower() or 'nötr' in current_text.lower() or 'محايد' in current_text:
                    new_text = self.tr('market_neutral_text')
                elif 'rising' in current_text.lower() or 'yükseli' in current_text.lower() or 'ارتفاع' in current_text:
                    new_text = self.tr('market_rising_text')
                elif 'falling' in current_text.lower() or 'düş' in current_text.lower() or 'انخفاض' in current_text:
                    new_text = self.tr('market_falling_text')
                else:
                    new_text = self.tr('market_neutral_text')
                self.market_status_label.config(text=new_text)
            
            # log_frame kaldırıldı
            
            # API bağlantısı varsa UI state'ini koru
            if api_was_connected and self.client:
                # Bağlanma butonunu doğru duruma getir
                if hasattr(self, 'connect_btn'):
                    self.connect_btn.config(text=self.tr('disconnect'))
                if hasattr(self, 'api_status_label'):
                    self.api_status_label.config(text=f"✅ {self.tr('connected')}", foreground="green")
        except Exception:
            pass
    
    def update_idletasks_safe(self):
        try:
            self.root.update_idletasks()
        except Exception:
            pass
    
    def close_all_positions(self):
        if not self.client:
            messagebox.showerror("Hata", "Önce API'ye bağlanın!")
            return
        
        # Arka planda çalıştır (rate limit için delay ile)
        def close_all_with_delay():
            try:
                positions = self.client.futures_position_information()
                closed_count = 0
                failed_symbols = []
                total_positions = sum(1 for p in positions if float(p['positionAmt']) != 0)
                
                idx = 0
                for pos in positions:
                    position_amt = float(pos['positionAmt'])
                    if position_amt != 0:
                        idx += 1
                        symbol = pos['symbol']
                        side = "SELL" if position_amt > 0 else "BUY"
                        quantity = abs(position_amt)
                        
                        try:
                            self.log_message(f"⏳ Kapatılıyor ({idx}/{total_positions}): {symbol}")
                            # Close position
                            self.client.futures_create_order(
                                symbol=symbol,
                                side=side,
                                type="MARKET",
                                quantity=quantity
                            )
                            closed_count += 1
                            self.log_message(f"✅ Kapatıldı ({idx}/{total_positions}): {symbol}")
                            
                            # Her pozisyon kapandıktan sonra tabloyu VE özeti hemen güncelle (sıralı görünüm)
                            def refresh_table_and_summary():
                                self._cache_positions = {'ts': 0.0, 'data': None}
                                self._cache_account = {'ts': 0.0, 'data': None}
                                self.update_positions()
                                self.update_summary_cards()  # ✅ Hesap özetini de güncelle!
                            
                            self.root.after(0, refresh_table_and_summary)
                            
                            # Rate limit için delay
                            if idx < total_positions:
                                time.sleep(1.0)  # 1 saniye bekle (tablo güncellensin)
                                
                        except Exception as e:
                            self.log_message(f"❌ Pozisyon kapatma hatası {symbol}: {e}")
                            failed_symbols.append(symbol)
                            continue
                
                # Tüm işlemler bittikten sonra sonuç mesajı göster
                def show_result():
                    if closed_count > 0:
                        msg = self.tr('positions_closed').format(count=closed_count)
                        if failed_symbols:
                            msg += f"\n\n❌ Hata: {', '.join(failed_symbols)}"
                        messagebox.showinfo(self.tr('success'), msg)
                    elif failed_symbols:
                        messagebox.showerror(self.tr('error'), f"Kapatılamadı: {', '.join(failed_symbols)}")
                    else:
                        messagebox.showinfo(self.tr('info'), self.tr('no_positions_to_close'))
                
                self.root.after(0, show_result)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(self.tr('error'), str(e)))
        
        # Arka planda çalıştır
        threading.Thread(target=close_all_with_delay, daemon=True).start()
    
    def on_closing(self):
        """
        Program kapatma işleyicisi
        
        İlk kapatma denemesi: Açık pozisyon varsa uyarı göster ve KAPANMA
        İkinci kapatma denemesi: Gerçekten kapat
        """
        # Açık pozisyon kontrolü
        open_positions_count = 0
        try:
            if self.client:
                positions = self.client.futures_position_information()
                open_positions_count = sum(1 for p in positions if float(p.get('positionAmt', 0)) != 0)
                
                if open_positions_count > 0:
                    self.close_attempt_count += 1
                    
                    if self.close_attempt_count == 1:
                        # İLK DENEME - Özel dialog göster (Tamam / Kapat butonları)
                        self.show_close_warning_dialog(open_positions_count)
                        self.log_message(f"⚠️ Kapatma denemesi 1/2 - {open_positions_count} açık pozisyon var")
                        return  # ✅ KAPANMA - Programı çalışır durumda tut
                    
                    else:
                        # İKİNCİ DENEME - Gerçekten kapat
                        self.log_message(f"🔴 Kapatma denemesi 2/2 - Program kapatılıyor...")
                        # Devam et, aşağıdaki kodlar çalışacak
                
                else:
                    # Açık pozisyon yok, direkt kapat
                    self.close_attempt_count = 2  # Sayacı atla
                    
        except Exception as e:
            self.log_message(f"Pozisyon kontrolü hatası: {e}")
        
        # Program kapatılırken son ayarları kaydet
        try:
            self.save_settings_file()
            self.save_config()
            self.log_message("Ayarlar kaydedildi - program kapatılıyor")
        except Exception as e:
            print(f"Kapatırken ayar kaydetme hatası: {e}")
            
        # Thread'leri durdur
        self.price_thread_running = False
        self.stop_market_monitor()
        if hasattr(self, 'summary_thread_running') and self.summary_thread_running:
            self.stop_summary_monitor()
        if self.price_thread:
            self.price_thread.join(timeout=1)
        if self.market_thread:
            self.market_thread.join(timeout=1)
        if hasattr(self, 'summary_thread') and self.summary_thread:
            self.summary_thread.join(timeout=1)
        
        # Programı gerçekten kapat
        self.root.destroy()
    
    # Log fonksiyonları kaldırıldı
    
    def refresh_news(self):
        """Haberleri yenile ve UI'da göster - Thread-safe versiyon"""
        try:
            # UI hazır mı kontrol et
            if not hasattr(self, 'news_list_frame') or self.news_list_frame is None:
                self.log_message("⚠️ Haber UI henüz hazır değil")
                return
            
            self.log_message("📰 Haberler yenileniyor...")
            
            # Seçili dil kodunu al (thread-safe)
            current_lang = 'tr'  # Varsayılan olarak Türkçe
            if hasattr(self, 'current_language'):
                current_lang = self.current_language
            
            # API'den haberleri çek (seçili dilde)
            news_list = self.news_service.fetch_latest_news(limit=4, filter_type="hot", language=current_lang)
            
            if not news_list:
                # Türkçe çalışmazsa İngilizce dene
                if current_lang != 'en':
                    news_list = self.news_service.fetch_latest_news(limit=4, filter_type="hot", language="en")
                    if not news_list:
                        self.log_message("❌ Haberler yüklenemedi")
                        return
                else:
                    self.log_message("❌ Haberler yüklenemedi")
                    return
            
            # UI güncellemesini main thread'de yap - Thread-safe
            def update_ui():
                try:
                    # Widget hala var mı kontrol et
                    if not hasattr(self, 'news_list_frame') or self.news_list_frame is None:
                        return
                    
                    # Eski haberleri temizle
                    for widget in self.news_list_frame.winfo_children():
                        widget.destroy()
                    
                    # Yeni haberleri ekle
                    for news in news_list:
                        self.create_news_item(news)
                    
                    self.log_message(f"✅ {len(news_list)} haber yüklendi")
                except Exception as e:
                    self.log_message(f"UI güncelleme hatası: {e}")
            
            # Thread-safe UI güncellemesi: root'un var olup olmadığını kontrol et
            try:
                if hasattr(self, 'root') and self.root and self.root.winfo_exists():
                    # after_idle kullanarak main loop'ta çalıştır
                    self.root.after_idle(update_ui)
            except RuntimeError as e:
                # Main loop hazır değilse, haberleri direkt işle (başlangıç durumu)
                if "main thread is not in main loop" in str(e):
                    self.log_message("⚠️ UI henüz hazır değil, haberleri sonra yükleyeceğiz")
                else:
                    raise
            
        except Exception as e:
            self.log_message(f"Haber yenileme hatası: {e}")
            import traceback
            self.log_message(f"Detay: {traceback.format_exc()}")
    
    def create_news_item(self, news):
        """Tek bir haber öğesi oluştur"""
        import webbrowser
        
        # Haber kartı - %100 GENİŞLİK, SIFIR PADDİNG
        news_card = tk.Frame(self.news_list_frame, bg='#1f2937', relief='flat', cursor='hand2')
        news_card.pack(fill=tk.X, expand=False, padx=0, pady=1, anchor='w')
        
        # İçerik frame - %100 GENİŞLİK
        content = tk.Frame(news_card, bg='#1f2937')
        content.pack(fill=tk.X, expand=True, padx=8, pady=6)
        
        # Başlık - TEK SATIR, WRAPLENGTH YOK!
        title_text = news['title']
        # Çok uzunsa kısalt (200 karakter max)
        if len(title_text) > 200:
            title_text = title_text[:197] + "..."
        
        # wraplength=0 means NO WRAP - tek satır!
        title = tk.Label(content, text=title_text, font=('Segoe UI', 10, 'bold'),
                        bg='#1f2937', fg='#e5e7eb', anchor='w', wraplength=0)
        title.pack(fill=tk.X, expand=True)
        
        # Alt bilgi (kaynak ve zaman)
        time_ago = self.news_service.format_time_ago(news['published_at'])
        info = tk.Label(content, text=f"📅 {news['source']} • {time_ago}",
                       font=('Segoe UI', 8), bg='#1f2937', fg='#6b7280', anchor='w')
        info.pack(fill=tk.X, pady=(3, 0))
        
        # Tıklama event'i
        def open_news(event=None):
            webbrowser.open(news['url'])
        
        # Hover effect
        def on_enter(event=None):
            news_card.config(bg='#374151')
            content.config(bg='#374151')
            title.config(bg='#374151')
            info.config(bg='#374151')
        
        def on_leave(event=None):
            news_card.config(bg='#1f2937')
            content.config(bg='#1f2937')
            title.config(bg='#1f2937')
            info.config(bg='#1f2937')
        
        # Tüm widget'lara event binding
        for widget in [news_card, content, title, info]:
            widget.bind('<Button-1>', open_news)
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            # Fare tekerleği - haber kartları üzerinde scroll
            if hasattr(self, 'news_mousewheel_callback'):
                widget.bind('<MouseWheel>', self.news_mousewheel_callback)
    
    def start_news_monitor(self):
        """Haber yenileme thread'ini başlat"""
        if hasattr(self, 'news_thread_running') and self.news_thread_running:
            return
        
        self.news_thread_running = True
        self.news_thread = threading.Thread(target=self._news_monitor_loop, daemon=True)
        self.news_thread.start()
        self.log_message("📰 Haber izleme başlatıldı")
    
    def _news_monitor_loop(self):
        """45 dakikada bir haberleri yenile"""
        import time
        
        # İlk yükleme için 5 saniye bekle (UI tam hazır olsun)
        time.sleep(5)
        
        # UI hazır olana kadar bekle
        max_wait = 30
        wait_time = 0
        while wait_time < max_wait:
            if hasattr(self, 'news_list_frame') and self.news_list_frame is not None:
                break
            time.sleep(1)
            wait_time += 1
        
        # İlk haberleri yükle
        self.refresh_news()
        
        while self.news_thread_running:
            try:
                time.sleep(2700)  # 45 dakika
                self.refresh_news()
            except Exception:
                pass
    
    # update_news_token fonksiyonu kaldırıldı - Artık sabit token kullanılıyor

def main():
    root = tk.Tk()
    app = BinanceFuturesBot(root)
    root.mainloop()

if __name__ == "__main__":
    main()