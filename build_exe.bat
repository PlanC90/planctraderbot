@echo off
echo ========================================
echo   Trading Bot - EXE Olusturma Scripti
echo ========================================
echo.

REM Eski build dosyalarini temizle
echo [1/4] Eski build dosyalari temizleniyor...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
echo ✓ Temizlik tamamlandi
echo.

REM PyInstaller kurulu mu kontrol et
echo [2/4] PyInstaller kontrol ediliyor...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller bulunamadi, kuruluyor...
    pip install pyinstaller>=6.0.0
    if errorlevel 1 (
        echo HATA: PyInstaller kurulamadi!
        pause
        exit /b 1
    )
) else (
    echo ✓ PyInstaller hazir
)
echo.

REM EXE olustur
echo [3/4] EXE dosyasi olusturuluyor...
echo Bu islem birkaç dakika surebilir, lutfen bekleyin...
echo.
pyinstaller main.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo HATA: EXE olusturulamadi!
    echo Hata detaylari icin yukaridaki mesajlari kontrol edin.
    pause
    exit /b 1
)
echo.
echo ✓ EXE basariyla olusturuldu
echo.

REM Config dosyasini kopyala
echo [4/4] Config dosyasi kopyalaniyor...
if exist config.json (
    copy config.json dist\config.json >nul 2>&1
    echo ✓ config.json kopyalandi
)
if exist ayarlar.txt (
    copy ayarlar.txt dist\ayarlar.txt >nul 2>&1
    echo ✓ ayarlar.txt kopyalandi
)
if exist coin100.txt (
    copy coin100.txt dist\coin100.txt >nul 2>&1
    echo ✓ coin100.txt kopyalandi
)
echo.

echo ========================================
echo   TAMAMLANDI!
echo ========================================
echo.
echo EXE dosyasi: dist\TradingBot.exe
echo.
echo Programi calistirmak icin:
echo   1. dist klasorune gidin
echo   2. TradingBot.exe dosyasini calistirin
echo.
echo NOT: TradingBot.exe dosyasini baska bir bilgisayara
echo      kopyalayabilirsiniz, Python kurulumu gerekmez!
echo.
pause


