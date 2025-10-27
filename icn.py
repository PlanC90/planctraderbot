from PIL import Image
import os

# Giriş ve çıkış dosyaları
input_image = "app.png"
output_icns = "app.icns"

# Gerekli boyutlar
sizes = [16, 32, 64, 128, 256, 512, 1024]

# Geçici klasör oluştur
iconset_dir = "temp.iconset"
os.makedirs(iconset_dir, exist_ok=True)

# Her boyutta PNG oluştur
img = Image.open(input_image)
for size in sizes:
    img_resized = img.resize((size, size), Image.LANCZOS)
    img_resized.save(f"{iconset_dir}/icon_{size}x{size}.png")

# .icns dosyası oluştur (MacOS'ta `iconutil` komutu gerekir)
os.system(f"iconutil -c icns {iconset_dir} -o {output_icns}")

# Geçici dosyaları sil
import shutil
shutil.rmtree(iconset_dir)

print("✅ app.icns başarıyla oluşturuldu!")
