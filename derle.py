import os
import platform
import subprocess
import shutil
import sys

# GitHub repo URL
GITHUB_REPO = "https://github.com/PlanC90/plancbinance.git"

def safe_rmtree(path):
    """Klasörü güvenli biçimde siler (izin hatalarını atlar)."""
    if os.path.exists(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                try:
                    os.chmod(os.path.join(root, name), 0o777)
                    os.remove(os.path.join(root, name))
                except Exception:
                    pass
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except Exception:
                    pass
        try:
            os.rmdir(path)
        except Exception:
            pass

print("🚀 Çoklu platform derleme başlatılıyor...")

# Ortak klasörleri temizle
for folder in ["build", "dist"]:
    safe_rmtree(folder)

# İşletim sistemi belirleme
os_type = platform.system().lower()
print(f"💻 İşletim sistemi: {os_type}")

# İkon dosyası seçimi
icon = None
if os_type == "windows":
    icon = "app.ico"
    cmd = f'pyinstaller --onefile --noconsole main.py --icon={icon}'
elif os_type == "darwin":  # macOS
    icon = "app.icns"
    cmd = f'pyinstaller --onefile --windowed main.py --icon={icon}'
elif os_type == "linux":
    icon = "app.png"
    cmd = f'pyinstaller --onefile main.py --icon={icon}'
else:
    print("❌ Desteklenmeyen platform!")
    sys.exit(1)

print(f"🏗️ Derleme başlatılıyor: {cmd}")
os.system(cmd)

# Çıktı dosyası adını belirleme
dist_path = "dist"
output_files = os.listdir(dist_path) if os.path.exists(dist_path) else []
print("\n✅ Derleme tamamlandı!")

for file in output_files:
    print(f"📦 Çıktı dosyası: {dist_path}/{file}")

# GitHub'a yükleme adımları
print("\n🌐 GitHub’a yükleniyor...")

try:
    os.system("git init")
    os.system("git add .")
    os.system('git commit -m "🚀 Otomatik derleme ve yükleme"')
    os.system(f"git remote add origin {GITHUB_REPO}")
    os.system("git branch -M main")
    os.system("git push -f origin main")
    print("✅ GitHub’a başarıyla yüklendi!")
except Exception as e:
    print(f"❌ GitHub yükleme hatası: {e}")

print("\n🎉 Tüm işlemler tamamlandı!")
