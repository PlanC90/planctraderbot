# 🚀 Trading Bot - EXE Oluşturma Rehberi

## 📋 Gereksinimler

- Python 3.8 veya üzeri
- Tüm bağımlılıklar yüklü olmalı

## ⚡ Hızlı Başlangıç

### Windows için:

```batch
build_exe.bat
```

Bu komut otomatik olarak:
1. ✅ Eski build dosyalarını temizler
2. ✅ PyInstaller'ı kontrol eder/yükler
3. ✅ EXE dosyasını oluşturur
4. ✅ Config dosyalarını kopyalar

### Manuel Yöntem:

#### 1. PyInstaller'ı Yükleyin
```bash
pip install pyinstaller>=6.0.0
```

#### 2. Tüm Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

#### 3. EXE Oluşturun
```bash
pyinstaller main.spec --clean --noconfirm
```

## 📦 Çıktı

EXE dosyası şurada oluşturulur:
```
dist/TradingBot.exe
```

## 🎯 Kullanım

### 1. İlk Çalıştırma
- `dist` klasörüne gidin
- `TradingBot.exe` dosyasını çift tıklayın
- Program başlayacak ve GUI açılacak

### 2. Dağıtım
- Tüm `dist` klasörünü başka bir bilgisayara kopyalayabilirsiniz
- Hedef bilgisayarda **Python kurulumu gerekmez**
- Sadece Windows 10/11 gereklidir

## 📁 Oluşturulan Dosyalar

```
dist/
├── TradingBot.exe        # Ana program
├── assets/               # Resim dosyaları
│   ├── banner_logo.jpg
│   └── advertisement.jpg
├── locales/              # Dil dosyaları
│   └── langs.py
├── config.json           # Ayarlar (otomatik kopyalanır)
├── ayarlar.txt          # Kullanıcı ayarları
└── coin100.txt          # Top 100 coin listesi
```

## 🔧 Özelleştirmeler

### Icon Değiştirme
1. Bir `.ico` dosyası hazırlayın (örn: `icon.ico`)
2. `main.spec` dosyasında şu satırı değiştirin:
   ```python
   icon=None,  # Buraya 'icon.ico' yazın
   ```

### Uygulama Adı Değiştirme
`main.spec` dosyasında:
```python
name='TradingBot',  # Buraya istediğiniz adı yazın
```

### Konsol Gösterme/Gizleme
`main.spec` dosyasında:
```python
console=False,  # True yaparsanız konsol görünür (debug için yararlı)
```

## ⚠️ Bilinen Sorunlar

### 1. Antivirüs Uyarıları
- Bazı antivirüs programları exe'yi zararlı olarak işaretleyebilir
- **Çözüm:** Antivirüste istisna ekleyin veya exe'yi dijital olarak imzalayın

### 2. Boyut Büyük
- EXE dosyası ~50-100 MB olabilir
- **Neden:** Python runtime ve tüm kütüphaneler dahil edilir
- **Çözüm:** Normal, endişelenmeyin

### 3. Yavaş Başlangıç
- İlk açılış biraz yavaş olabilir
- **Neden:** Geçici dosyalar çıkarılıyor
- **Çözüm:** Normal, 2. açılıştan sonra hızlanır

## 🛠️ Sorun Giderme

### Build Hatası
```bash
# Eski dosyaları manuel temizleyin
rmdir /s /q build dist
del *.spec

# Yeniden spec oluşturun
pyi-makespec main.py

# Tekrar build edin
pyinstaller main.spec
```

### ModuleNotFoundError
`main.spec` dosyasındaki `hiddenimports` listesine eksik modülü ekleyin:
```python
hiddenimports=[
    'binance',
    'requests',
    # Eksik modülü buraya ekleyin
],
```

### Assets Bulunamıyor
`main.spec` dosyasındaki `datas` listesini kontrol edin:
```python
datas=[
    ('assets/banner_logo.jpg', 'assets'),
    ('assets/advertisement.jpg', 'assets'),
    # Eksik dosyayı buraya ekleyin
],
```

## 📊 Build Zamanları

| Sistem | Süre |
|--------|------|
| i5 + HDD | ~5-8 dakika |
| i5 + SSD | ~2-4 dakika |
| i7 + SSD | ~1-2 dakika |

## 🎨 Gelişmiş Seçenekler

### UPX Sıkıştırma (Daha Küçük EXE)
```python
upx=True,  # main.spec içinde
```

### Tek Dosya vs Klasör
**Şu anki:** Tek dosya (--onefile)
**Avantaj:** Taşınması kolay
**Dezavantaj:** Yavaş başlangıç

### Debug Modu
Build sırasında hata ayıklama için:
```bash
pyinstaller main.spec --clean --noconfirm --debug all
```

## 📝 Notlar

- ✅ EXE dosyası portable'dır (USB'den çalışır)
- ✅ Python kurulumu gerektirmez
- ✅ Tüm kütüphaneler dahildir
- ✅ Windows 10/11 ile uyumludur
- ❌ Linux/Mac için ayrı build gerekir

## 🔗 Yararlı Linkler

- [PyInstaller Dokümantasyonu](https://pyinstaller.org/)
- [Python Binance](https://python-binance.readthedocs.io/)

---

**Son Güncelleme:** 2025-01-23  
**Versiyon:** 5.0


