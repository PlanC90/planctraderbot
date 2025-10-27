# 🚀 Binance Futures Trading Bot v5

**Profesyonel seviye otomatik trading botu** - Modern GUI, çoklu dil desteği ve akıllı strateji sistemi ile donatılmış Binance Futures trading platformu.

![Version](https://img.shields.io/badge/version-5.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-Commercial-orange)
![Languages](https://img.shields.io/badge/languages-31-purple)

---

## ✨ Özellikler

### 🎨 Modern Kullanıcı Arayüzü
- ⚫ **Koyu Tema**: Göz yormayan modern dark mode arayüz
- 📊 **Gerçek Zamanlı Fiyat Kartları**: Seçili coinler için canlı fiyat ve değişim takibi
- 💰 **Hesap Özeti Kartları**: PNL, toplam fee, işlem sayısı, long/short pozisyonlar
- 📈 **Pozisyon Tablosu**: Tüm açık pozisyonlarınızı detaylı görüntüleme
- 🔔 **Durum Banner'ı**: Auto trade, test/live mode ve piyasa durumu göstergesi
- 💡 **Tooltip Yardım**: Her ayar için detaylı açıklamalar

### 🌍 Çoklu Dil Desteği (31 Dil)
```
🇹🇷 Türkçe    🇬🇧 English   🇸🇦 العربية    🇨🇳 中文      🇷🇺 Русский
🇪🇸 Español   🇫🇷 Français  🇩🇪 Deutsch    🇵🇹 Português 🇮🇳 हिन्दी
🇯🇵 日本語    🇰🇷 한국어     🇮🇹 Italiano   🇳🇱 Nederlands 🇵🇱 Polski
🇮🇷 فارسی     🇮🇩 Indonesia 🇹🇭 ไทย       🇻🇳 Tiếng Việt 🇺🇦 Українська
```
...ve 11 dil daha!

### 🤖 Otomatik Trading Stratejisi
- **Market Breadth Analizi**: Top 100 coin'in 1 saatlik hareketlerini analiz eder
- **3-Coin Rule**: Seçili coinlerde 3 tanesi aynı yönde hareket edince trend yakalar
- **Akıllı Pozisyon Açma**: Piyasa yükselişinde LONG, düşüşünde SHORT pozisyon açar
- **Otomatik Kapama**: Target PNL, Stop Loss veya Neutral Close koşullarında pozisyon kapatır

### 📊 Gelişmiş Risk Yönetimi
- 🎯 **Target PNL**: Hedef kar seviyesine ulaşınca otomatik kapat
- 🛑 **Stop Loss (%)**: Belirlediğiniz zarar yüzdesinde pozisyonu kapat
- ⚖️ **Neutral Close (%)**: Piyasa nötrken aşırı değişimlerde kapat
- 💵 **Auto Balance (%)**: Bakiyenizin belirli yüzdesini otomatik kullan
- 🔒 **Leverage Kontrolü**: 1x - 20x arası kaldıraç ayarı (lisanslı kullanıcılar için)

### 🎮 Çoklu Coin Yönetimi
- **100+ Coin Listesi**: Top 100 kripto para birimi desteği
- **Çoklu Seçim**: Birden fazla coin'i aynı anda takip edin
- **Arama Filtresi**: Hızlıca istediğiniz coin'i bulun
- **Dinamik Kartlar**: Seçili coinler için gerçek zamanlı fiyat kartları

### 🔐 Lisanslama Sistemi
- **Ed25519 Dijital İmza**: Güvenli lisans doğrulama
- **Makine Kilitleme**: Her lisans tek cihaza özel
- **365 Gün Geçerlilik**: 1 yıllık kullanım süresi
- **Kaldıraç Kısıtlaması**: Lisanssız kullanıcılar max 1x leverage

### 🔄 Otomatik Güncelleme
- **GitHub Entegrasyonu**: Otomatik güncelleme kontrolü
- **Tek Tık Güncelleme**: Yeni sürümleri otomatik indir ve kur
- **Commit Takibi**: Git commit hash karşılaştırması ile versiyon kontrolü

### 🌐 Test/Live Ortam Desteği
- **Test Mode**: Binance Testnet ile risk almadan test edin
- **Live Mode**: Gerçek para ile trading yapın
- **Otomatik Bağlantı**: Kaydedilmiş API anahtarları ile otomatik giriş
- **Dual Config**: Test ve Live için ayrı API key yönetimi

### 📁 Veri Yönetimi
- **Trading Geçmişi**: Tüm işlemler CSV dosyasında saklanır
- **PNL Takibi**: Toplam kar/zarar hesaplamaları
- **Fee Hesaplama**: Komisyon özetleri
- **Ayar Kaydetme**: Tüm ayarlar otomatik kaydedilir (`ayarlar.txt`)

---

## 📦 Kurulum

### 1️⃣ Gereksinimleri Yükleyin

```bash
pip install -r requirements.txt
```

**Bağımlılıklar:**
```
python-binance>=1.0.19    # Binance API client
requests>=2.31.0          # HTTP istekleri
pillow>=10.0.0            # Görsel işleme
pynacl>=1.5.0             # Ed25519 kriptografi
```

### 2️⃣ Bot'u Başlatın

```bash
python main.py
```

### 3️⃣ İlk Kurulum (Otomatik)

Bot ilk açıldığında:
1. ✅ Ayar dosyaları otomatik oluşturulur (`config.json`, `ayarlar.txt`)
2. ✅ Top 100 coin listesi yüklenir (`coin100.txt`)
3. ✅ Dil seçimi varsayılan olarak Türkçe
4. ✅ Test mode aktif olarak başlar (güvenlik için)

---

## 🎯 Hızlı Başlangıç Rehberi

### Adım 1: API Anahtarlarınızı Hazırlayın

#### Binance Testnet (Test için - Önerilen)
1. [Binance Testnet](https://testnet.binancefuture.com/) adresine gidin
2. GitHub hesabınızla giriş yapın
3. Test API Key ve Secret oluşturun
4. **10,000 USDT test parası** otomatik verilir

#### Binance Mainnet (Gerçek para ile)
1. [Binance](https://www.binance.com/) hesabınıza giriş yapın
2. **API Management** → **Create API**
3. **İzinler:**
   - ✅ Enable Reading
   - ✅ Enable Futures
   - ❌ Enable Withdrawals (GÜVENLİK!)
4. IP kısıtlaması ekleyin (isteğe bağlı ama önerilen)

### Adım 2: Bot'a Bağlanın

1. **Test/Gerçek** seçimini yapın (üst kısımda)
2. **API Key** ve **Secret** girin
3. **"Bağlan"** butonuna tıklayın
4. ✅ Bağlantı başarılı olursa bakiyeniz görünür

### Adım 3: Coin Seçin

1. **"Listeyi Yenile"** ile 100+ coin listesini yükleyin
2. **Arama** kutusundan coin arayın (örn: BTC, ETH)
3. İstediğiniz coinleri **seçin** (checkbox)
4. **"Seçilenleri Ekle"** ile kartları oluşturun

### Adım 4: Trading Ayarlarını Yapın

```
💵 Pozisyon Boyutu: 100 USDT      # Her işlemde kullanılacak miktar
📈 Kaldıraç: 5x                   # 1-20x arası (lisanslı kullanıcılar)
🎯 Hedef PNL: 20 USDT             # Bu kara ulaşınca kapat
🛑 Stop Loss: 10%                 # %10 zarar olursa kapat
⚖️ Nötr Kapat: 2%                 # Piyasa nötrken %2 değişimde kapat
💰 Oto Bakiye: 0%                 # 0 ise sabit miktar kullanır
```

### Adım 5: Manuel veya Otomatik İşlem

#### Manuel Trading:
1. Bir coin kartına tıklayın
2. **LONG** (yükseliş) veya **SHORT** (düşüş) butonuna basın
3. Pozisyon anında açılır

#### Otomatik Trading:
1. **">> Oto Trade"** butonuna tıklayın
2. Bot piyasayı analiz eder (30 saniyede bir)
3. Uygun koşullarda otomatik pozisyon açar/kapatır
4. **Tekrar basarak** durdurabilirsiniz

---

## 🛠️ Detaylı Kullanım

### Otomatik Trading Mantığı

Bot şu stratejiye göre çalışır:

```python
# 1. Market Breadth Analizi
Top 100 coin → 1 saatlik değişim hesapla
Yükselen > 50 → Piyasa yükseliyor 📈
Düşen > 50   → Piyasa düşüyor 📉
Diğer        → Piyasa nötr ⚖️

# 2. 3-Coin Rule (Trend Latching)
Seçili coinlerden 3 tanesi aynı yönde → Trend latch
Örnek: BTC ↑, ETH ↑, SOL ↑ → LONG pozisyon aç

# 3. Otomatik Pozisyon Açma
IF piyasa_yukseliyor AND long_pozisyon_yok:
    → LONG aç
    
IF piyasa_dusuyor AND short_pozisyon_yok:
    → SHORT aç

# 4. Otomatik Kapama
IF kar >= hedef_pnl:
    → Pozisyonu kapat (kar al)
    
IF zarar >= stop_loss:
    → Pozisyonu kapat (zararı durdur)
    
IF piyasa_notr AND degisim > neutral_close:
    → Pozisyonu kapat (risk azalt)
```

### Piyasa Kontrol Aralığı

```
⏱️ Min: 30 saniye  (API rate limit koruması)
⏱️ Önerilen: 30-60 saniye
⏱️ Güncelleme: Ayarlardan değiştirilebilir
```

### Pozisyon Yönetimi

- **Pozisyon Tablosu**: Tüm açık pozisyonlar gerçek zamanlı görünür
- **Tek Tıkla Kapat**: Bir pozisyonu seçip "Seçiliyi Kapat"
- **Toplu Kapat**: "Tüm İşlemleri Kapat" ile hepsini kapat
- **PNL Göstergesi**: Her pozisyonun anlık kar/zarar durumu

---

## 🔐 Güvenlik Önlemleri

### ⚠️ ÖNEMLİ: API Güvenliği

```bash
# 1. config.json dosyasını asla paylaşMAYIN!
# 2. .gitignore'a ekleyin:
echo "config.json" >> .gitignore
echo "ayarlar.txt" >> .gitignore
echo "*.csv" >> .gitignore

# 3. Binance API ayarlarında:
✅ Enable Reading
✅ Enable Futures
❌ Enable Withdrawals (KAPALI TUTUN!)
✅ IP Restriction (Önerilen)
```

### 🔒 Lisans Güvenliği

- **Ed25519 Dijital İmza**: Sahte lisanslar çalışmaz
- **Makine Kilitleme**: Windows MachineGuid kontrolü
- **Süre Kontrolü**: 365 gün sonra yenileme gerekir

### 🛡️ Risk Yönetimi

```
⚠️ UYARILAR:
1. Küçük miktarlarla başlayın (100-500 USDT)
2. Yüksek kaldıraçtan kaçının (max 5-10x)
3. Her zaman Stop Loss kullanın
4. Bakiyenizin sadece %1-2'sini riske edin
5. İlk önce TEST modunda pratik yapın
```

---

## 📁 Proje Yapısı

```
v5/
├── api/                          # API katmanı
│   └── clients.py               # Binance client yönetimi
├── core/                         # Temel sistem
│   ├── config.py                # Yapılandırma yönetimi
│   └── logging.py               # Log buffer sistemi
├── services/                     # İş mantığı
│   ├── account.py               # Hesap servisi (cache'li)
│   └── market.py                # Piyasa veri servisi
├── tools/                        # Yardımcı araçlar
│   └── generate_license.py      # Lisans üreticisi
├── licenses/                     # Lisans sistemi
│   └── verify.py                # Ed25519 doğrulama
├── locales/                      # Çoklu dil
│   └── langs.py                 # 31 dil çevirisi
├── main.py                       # Ana uygulama (4550 satır)
├── updater.py                    # Otomatik güncelleme
├── config.json                   # API anahtarları (GİZLİ!)
├── ayarlar.txt                   # Kullanıcı ayarları
├── coin100.txt                   # Top 100 coin listesi
├── requirements.txt              # Python bağımlılıkları
├── trades_history.csv            # İşlem geçmişi
├── trades_history_test.csv       # Test işlem geçmişi
├── totals_history.csv            # Toplam PNL geçmişi
└── README.md                     # Bu dosya
```

---

## 🌐 Dil Değiştirme

```
1. Sol üst köşedeki "Dil / Language" menüsünü açın
2. İstediğiniz dili seçin
3. Tüm arayüz anında güncellenir
```

**Desteklenen 31 Dil:**
İngilizce, Türkçe, Arapça, Çince, Rusça, İspanyolca, Fransızca, Almanca, Portekizce, Hintçe, Japonca, Korece, İtalyanca, Hollandaca, Lehçe, Farsça, Endonezce, Tayca, Vietnamca, Ukraynaca, Romence, Çekçe, İsveççe, Yunanca, İbranice, Macarca, Bengalce, Malayca, Tamilce, Urduca, Rusça

---

## 🔄 Otomatik Güncelleme

Bot başlatıldığında otomatik olarak güncellemeleri kontrol eder.

### Manuel Güncelleme:
1. **"[↓] Güncelle"** butonuna tıklayın
2. Yeni sürüm varsa bildirim gelir
3. **"Güncelle"** ile kurulum başlar
4. Program otomatik yeniden başlar

### GitHub Repo:
```
https://github.com/PlanC90/tradebot
```

---

## ❓ Sık Sorulan Sorular (SSS)

### Bağlantı Sorunları

**S: "API connection error" hatası alıyorum?**
- API Key ve Secret doğru mu kontrol edin
- Futures Trading izninin açık olduğundan emin olun
- Test/Live ortam seçimini doğrulayın
- İnternet bağlantınızı kontrol edin

**S: "Insufficient margin" hatası?**
- Bakiyenizde yeterli USDT var mı?
- Pozisyon boyutu çok büyük olabilir
- Kaldıraç ayarını düşürün

### Trading Sorunları

**S: Otomatik trade çalışmıyor?**
- En az 3 coin seçili olmalı (3-coin rule için)
- Market interval min 30 saniye olmalı
- Piyasa durumu değişmeden pozisyon açılmaz

**S: Pozisyon açılmıyor?**
- Minimum order miktarını karşılıyor musunuz?
- Rate limit'e takılmış olabilirsiniz (30sn bekleyin)
- Symbol için futures trading aktif mi?

### Lisans Sorunları

**S: 3x üzeri kaldıraç kullanamıyorum?**
- Aktif lisans gereklidir
- Lisans satın almak için: `https://license.planc.space/`

**S: Lisans sürem doldu?**
- "Lisans Al" butonundan yeni lisans alın
- Yıllık yenileme gereklidir

---

## 📊 Performans İpuçları

### API Optimizasyonu
```python
# Bot otomatik cache kullanır:
Account Data: 30 saniye cache
Positions: 5 saniye cache
Market Data: Ayarlanabilir interval (min 30s)
```

### CPU/RAM Kullanımı
```
Normal: ~50-100 MB RAM
Thread sayısı: 3 (price, market, summary)
GUI güncellemeleri: Thread-safe batch işleme
```

---

## 🚨 Sorumluluk Reddi

```
⚠️ ÖNEMLİ UYARILAR:

1. Bu yazılım SADECE EĞİTİM AMAÇLIDIR
2. Finansal tavsiye DEĞİLDİR
3. Gerçek para kaybı riski vardır
4. Kripto piyasaları YÜKSEK RİSKLİDİR
5. Sadece kaybetmeyi göze alabileceğiniz para ile işlem yapın
6. Yazılım geliştiricisi hiçbir kayıptan sorumlu değildir
7. Kendi araştırmanızı yapın (DYOR)
8. Profesyonel finansal danışman görüşü alın

KENDİ SORUMLULUĞUNUZDA KULLANIN!
```

---

## 📞 Destek ve İletişim

- 🌐 **Web**: [https://planc.space](https://planc.space)
- 📧 **Email**: Destek için web sitesinden iletişime geçin
- 📝 **Lisans**: [https://license.planc.space/](https://license.planc.space/)
- 🐛 **Bug Report**: GitHub Issues

---

## 📄 Lisans

**Commercial License** - Ticari kullanım için lisans gereklidir.

---

## 🎉 Teşekkürler

Bu projeyi kullandığınız için teşekkür ederiz! 

**💰 İyi Ticaretler!**

---

<div align="center">

**Made with ❤️ by PlanC.Space**

[🌐 Website](https://planc.space) • [📦 Lisans Al](https://license.planc.space/) • [🔄 Güncellemeler](https://github.com/PlanC90/tradebot)

</div>