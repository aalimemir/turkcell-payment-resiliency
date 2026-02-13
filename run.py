import subprocess
import time
import os
import webbrowser

def run_system():
    print("🚀 TURKCELL FINANSAL ISLEM MERKEZI BASLATILIYOR...")
    print("---------------------------------------------------")
    

    cwd = os.path.dirname(os.path.abspath(__file__))

    print("🏦 Banka Servisi açılıyor...")
    subprocess.Popen("start cmd /k uvicorn backend.bank_service:app --port 8001", shell=True, cwd=cwd)
    
    print("⚙️  Backend API açılıyor...")
    subprocess.Popen("start cmd /k uvicorn backend.payment_api:app --port 8000", shell=True, cwd=cwd)

    time.sleep(3)

    print("📊 Dashboard yükleniyor...")
    
    subprocess.Popen("streamlit run dashboard/dashboard.py", shell=True, cwd=cwd)

    print("\n✅ SİSTEM BAŞLATILDI!")
    print("Terminal pencerelerini kapatarak sistemi durdurabilirsin.")

if __name__ == "__main__":
    run_system()