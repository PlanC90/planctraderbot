import os
import sys
import subprocess
import requests
import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import tempfile
import shutil
import zipfile
from datetime import datetime

# i18n support
try:
    from locales.langs import get_text
except Exception:
    def get_text(lang, key):
        return key

class SoftwareUpdater:
    def __init__(self, repo_owner="PlanC90", repo_name="plancbinance", branch="main", current_version="1.0.0", lang='tr'):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.branch = branch
        self.current_version = current_version
        self.lang = lang
        self.github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.download_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/{branch}.zip"
    
    def tr(self, key):
        """Translation helper"""
        return get_text(self.lang, key)
        
    def get_latest_commit_info(self):
        """GitHub'dan son commit bilgisini al"""
        try:
            url = f"{self.github_api_url}/commits/{self.branch}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                commit_data = response.json()
                return {
                    'sha': commit_data['sha'][:8],
                    'date': commit_data['commit']['committer']['date'],
                    'message': commit_data['commit']['message']
                }
        except Exception as e:
            print(self.tr('commit_info_failed') + f": {e}")
        return None
    
    def get_local_commit_info(self):
        """Yerel git commit bilgisini al"""
        try:
            # Git kurulu mu kontrol et
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return None
                
            # Mevcut commit hash
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                commit_hash = result.stdout.strip()[:8]
                
                # Commit tarihi
                date_result = subprocess.run(['git', 'log', '-1', '--format=%ci'], 
                                           capture_output=True, text=True, timeout=5)
                commit_date = date_result.stdout.strip() if date_result.returncode == 0 else ""
                
                return {
                    'sha': commit_hash,
                    'date': commit_date
                }
        except FileNotFoundError:
            # Git kurulu değil - sessizce devam et
            pass
        except Exception as e:
            # Sadece kritik hatalar için log yaz
            if "WinError" not in str(e):
                print(self.tr('local_git_info_failed') + f": {e}")
        
        # Git yoksa, version.txt dosyasından oku
        try:
            if os.path.exists('version.txt'):
                with open('version.txt', 'r', encoding='utf-8') as f:
                    version = f.read().strip()
                    return {
                        'sha': version,
                        'date': ''
                    }
        except Exception:
            pass
        
        return None
    
    def check_for_updates(self):
        """Güncelleme kontrolü yap"""
        try:
            remote_info = self.get_latest_commit_info()
            local_info = self.get_local_commit_info()
            
            if not remote_info:
                return False, self.tr('version_info_failed')
            
            if not local_info:
                # Local info yoksa güncelleme var
                return True, self.tr('new_update_message').format(message=remote_info['message'][:50]+"...")
            
            # SHA veya mesaj farklıysa güncelleme var
            if remote_info['sha'] != local_info['sha']:
                return True, self.tr('new_update_message').format(message=remote_info['message'][:50]+"...")
            
            return False, self.tr('software_is_uptodate')
            
        except Exception as e:
            return False, self.tr('update_check_error_msg').format(error=e)
    
    def save_current_version(self, commit_hash):
        """Mevcut sürümü version.txt dosyasına kaydet"""
        try:
            with open('version.txt', 'w', encoding='utf-8') as f:
                f.write(commit_hash)
        except Exception:
            pass
    
    def _create_apply_bat(self, current_dir):
        """Yeni dosyaları (.new uzantılı) asıl dosyalarla değiştir"""
        bat_content = f"""@echo off
chcp 65001 >nul
echo ========================================
echo   Güncelleme uygulanıyor...
echo ========================================
timeout /t 3 /nobreak >nul

cd /d "{current_dir}"

for /r %%F in (*.new) do (
    if exist "%%F" (
        set "oldfile=%%F"
        setlocal enabledelayedexpansion
        set "newfile=!oldfile:.new=!"
        echo Değiştiriliyor: !newfile!
        if exist "!newfile!" (
            del /f /q "!newfile!"
        )
        move /y "!oldfile!" "!newfile!" >nul
        endlocal
    )
)

echo.
echo ========================================
echo   Güncelleme tamamlandı!
echo ========================================
timeout /t 2 /nobreak >nul
del /q "%~f0" >nul 2>&1
""".strip()
        
        bat_path = os.path.join(current_dir, 'apply_update.bat')
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(bat_content)
    
    def download_update(self, progress_callback=None):
        """Güncellemeyi indir ve uygula"""
        try:
            # Geçici dizin oluştur
            temp_dir = tempfile.mkdtemp(prefix="update_")
            zip_path = os.path.join(temp_dir, "update.zip")
            
            # Güncellemeyi indir
            if progress_callback:
                progress_callback(self.tr('downloading_update'))
            
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 50  # %50'ye kadar indirme
                            progress_callback(f"İndiriliyor... {progress:.1f}%")
            
            if progress_callback:
                progress_callback(self.tr('extracting_archive'))
            
            # ZIP dosyasını aç
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Ana dizini bul (tradebot-master)
            extracted_folders = os.listdir(extract_dir)
            if not extracted_folders:
                raise Exception("Arşiv içinde dosya bulunamadı")
            
            source_dir = os.path.join(extract_dir, extracted_folders[0])
            current_dir = os.getcwd()
            
            if progress_callback:
                progress_callback(self.tr('updating_files'))
            
            # Dosyaları güncelle (git ile çakışmaması için .git hariç)
            files_updated = 0
            failed_files = []
            
            for root, dirs, files in os.walk(source_dir):
                # .git dizinini atla
                if '.git' in dirs:
                    dirs.remove('.git')
                    
                rel_path = os.path.relpath(root, source_dir)
                target_dir = os.path.join(current_dir, rel_path) if rel_path != '.' else current_dir
                
                # Hedef dizini oluştur
                os.makedirs(target_dir, exist_ok=True)
                
                # Dosyaları kopyala
                for file in files:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    
                    # __pycache__ ve .pyc dosyalarını atla
                    if '__pycache__' in source_file or file.endswith('.pyc'):
                        continue
                    
                    try:
                        # Önce dosyayı kopyala, eğer kilitli ise yeni isimle kaydet
                        if os.path.exists(target_file):
                            try:
                                shutil.copy2(source_file, target_file)
                                files_updated += 1
                            except PermissionError:
                                # Dosya kilitli - yeni isimle kaydet
                                backup_file = target_file + '.new'
                                shutil.copy2(source_file, backup_file)
                                files_updated += 1
                                # Bat dosyası ile değiştirilecek
                                if not os.path.exists(os.path.join(current_dir, 'apply_update.bat')):
                                    self._create_apply_bat(current_dir)
                        else:
                            shutil.copy2(source_file, target_file)
                            files_updated += 1
                            
                    except OSError as e:
                        failed_files.append(target_file)
                    
                    if progress_callback:
                        progress = 50 + (files_updated * 50 / 100)  # %50-100 arası
                        progress_callback(f"Güncelleniyor... {min(progress, 99):.1f}%")
            
            # Kilitli dosyalar varsa uyarı ver
            if failed_files:
                return False, self.tr('update_file_locked').format(count=len(failed_files))
            
            # Geçici dosyaları temizle
            shutil.rmtree(temp_dir)
            
            # Eğer .new dosyaları varsa, bat dosyasını çalıştır
            new_files = []
            for root, dirs, files in os.walk(current_dir):
                for file in files:
                    if file.endswith('.new'):
                        new_files.append(os.path.join(root, file))
            
            if new_files and os.path.exists(os.path.join(current_dir, 'apply_update.bat')):
                # Kullanıcıya bilgi ver
                if progress_callback:
                    progress_callback(self.tr('update_restart_required'))
                import subprocess
                # Bat dosyasını arka planda çalıştır
                subprocess.Popen([os.path.join(current_dir, 'apply_update.bat')], 
                               shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True, self.tr('update_will_complete_on_restart')
            
            # Güncel commit'i version.txt'ye kaydet
            remote_info = self.get_latest_commit_info()
            if remote_info:
                self.save_current_version(remote_info['sha'])
            
            if progress_callback:
                progress_callback(self.tr('update_complete'))
            
            return True, self.tr('files_updated').format(count=files_updated)
            
        except Exception as e:
            return False, self.tr('update_error_msg').format(error=e)

class UpdateDialog:
    def __init__(self, parent, updater):
        self.parent = parent
        self.updater = updater
        self.dialog = None
        self.progress_var = None
        self.status_label = None
    
    def tr(self, key):
        """Translation helper"""
        return self.updater.tr(key)
        
    def show_update_dialog(self, update_available, message):
        """Güncelleme diyaloğunu göster"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.tr('software_update_title'))
        self.dialog.geometry("400x200")
        self.dialog.configure(bg='#1e1e1e')
        self.dialog.resizable(False, False)
        
        # Merkeze al
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Ana frame
        main_frame = tk.Frame(self.dialog, bg='#1e1e1e', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        if update_available:
            # Güncelleme mevcut
            tk.Label(main_frame, text=self.tr('new_update_available'), 
                    bg='#1e1e1e', fg='#10b981', font=('Segoe UI', 12, 'bold')).pack(pady=(0,10))
            
            tk.Label(main_frame, text=message, 
                    bg='#1e1e1e', fg='#e5e7eb', wraplength=350).pack(pady=(0,20))
            
            # Progress bar
            self.progress_var = tk.StringVar(value=self.tr('ready'))
            self.status_label = tk.Label(main_frame, textvariable=self.progress_var,
                                       bg='#1e1e1e', fg='#9ca3af')
            self.status_label.pack(pady=(0,10))
            
            # Butonlar
            btn_frame = tk.Frame(main_frame, bg='#1e1e1e')
            btn_frame.pack(fill=tk.X)
            
            update_btn = tk.Button(btn_frame, text=self.tr('update'), 
                                 command=self.start_update,
                                 bg='#10b981', fg='white', font=('Segoe UI', 10),
                                 padx=20, pady=8)
            update_btn.pack(side=tk.LEFT, padx=(0,10))
            
            cancel_btn = tk.Button(btn_frame, text=self.tr('cancel'),
                                 command=self.dialog.destroy,
                                 bg='#6b7280', fg='white', font=('Segoe UI', 10),
                                 padx=20, pady=8)
            cancel_btn.pack(side=tk.LEFT)
            
        else:
            # Güncelleme yok
            tk.Label(main_frame, text=self.tr('software_uptodate'),
                    bg='#1e1e1e', fg='#10b981', font=('Segoe UI', 12, 'bold')).pack(pady=(0,10))
            
            tk.Label(main_frame, text=message,
                    bg='#1e1e1e', fg='#e5e7eb').pack(pady=(0,20))
            
            tk.Button(main_frame, text=self.tr('ok'),
                     command=self.dialog.destroy,
                     bg='#3b82f6', fg='white', font=('Segoe UI', 10),
                     padx=30, pady=8).pack()
    
    def start_update(self):
        """Güncelleme işlemini başlat"""
        def update_progress(message):
            if self.progress_var:
                self.progress_var.set(message)
                self.dialog.update()
        
        def do_update():
            success, message = self.updater.download_update(progress_callback=update_progress)
            
            self.dialog.after(0, lambda: self.update_completed(success, message))
        
        # Butonları deaktive et
        for widget in self.dialog.winfo_children():
            if isinstance(widget, tk.Frame):
                for btn in widget.winfo_children():
                    if isinstance(btn, tk.Frame):  # btn_frame
                        for button in btn.winfo_children():
                            if isinstance(button, tk.Button):
                                button.config(state='disabled')
        
        # Thread'de güncellemeyi başlat
        threading.Thread(target=do_update, daemon=True).start()
    
    def update_completed(self, success, message):
        """Güncelleme tamamlandığında çağrılır"""
        if success:
            # Başarılı
            messagebox.showinfo(self.tr('update_completed'), 
                              f"{message}\n\n{self.tr('program_will_restart')}",
                              parent=self.dialog)
            self.dialog.destroy()
            
            # Programı yeniden başlat
            python = sys.executable
            subprocess.Popen([python] + sys.argv)
            self.parent.quit()
            
        else:
            # Hata
            messagebox.showerror(self.tr('update_error_title'), message, parent=self.dialog)
            self.dialog.destroy()

# Test fonksiyonu
def test_updater():
    """Updater'ı test et"""
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    
    updater = SoftwareUpdater()
    dialog = UpdateDialog(root, updater)
    
    # Güncelleme kontrol et
    has_update, message = updater.check_for_updates()
    dialog.show_update_dialog(has_update, message)
    
    root.mainloop()

if __name__ == "__main__":
    test_updater()