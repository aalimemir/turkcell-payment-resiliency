import sys
import requests
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Depends # <--- Depends eklendi
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from pybreaker import CircuitBreaker, CircuitBreakerError
from loguru import logger 

# --- AYARLAR & LOGLAMA ---
class Settings:
    APP_NAME = "Turkcell Finansal İşlem Merkezi"
    HOST = "127.0.0.1"
    BANK_PORT = 8001
    API_PORT = 8000
    # belirlediğimiz şifre
    API_SECRET = "turkcell-gncytnk-2026-alim"
    
    @property
    def BANK_URL(self):
        return f"http://{self.HOST}:{self.BANK_PORT}/charge"

settings = Settings()

# Log Ayarları:
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>")
logger.add("turkcell_logs.log", rotation="5 MB") # Logları dosyaya da yazar

app = FastAPI(title=settings.APP_NAME)

# HAFIZA & DEVRE KESİCİ 
idempotency_store = {}
breaker = CircuitBreaker(fail_max=5, reset_timeout=15)

class PaymentRequest(BaseModel):
    amount: float

# --- API KEY  ---
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Gelen istekte doğru şifre var mı kontrol eder."""
    if x_api_key != settings.API_SECRET:
        logger.warning(f"⛔ YETKİSİZ GİRİŞ! Yanlış Anahtar: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

# --- BANKA SERVİSİ ---
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_fixed(1),
    retry=retry_if_exception_type((requests.exceptions.RequestException, HTTPException)),
    reraise=True
)
@breaker
def call_bank_service(amount: float, mode: str):
    # Ayarları class'tan çekiyoruz (settings.BANK_URL)
    headers = {"X-Test-Mode": mode}
    
    # Debug logu (Geliştirici için)
    logger.debug(f"Bankaya gidiliyor... Tutar: {amount} TL | Mod: {mode}")
    
    try:
        response = requests.post(settings.BANK_URL, json={"amount": amount}, headers=headers, timeout=2)
        response.raise_for_status()
        
        # Başarılı logu (Yeşil)
        logger.success(f"Bankadan onay alındı! (Tutar: {amount})")
        return response.json()
        
    except requests.exceptions.Timeout:
        logger.warning("⏳ Banka cevap vermedi (Timeout)! Tekrar denenecek...")
        raise HTTPException(status_code=408, detail="Bank Timeout")
        
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        logger.error(f"💥 Banka hatası aldı: {status}")
        raise HTTPException(status_code=status, detail="Bank Error")

# --- ANA ENDPOINT ---
@app.post("/pay")
async def process_payment(
    request: PaymentRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_test_mode: str = Header(default="normal", alias="X-Test-Mode"),
    # YENİ: Güvenlik kontrolünü buraya taktık
    authorized: bool = Depends(verify_api_key) 
):
    # Loglara işlem kodunu (Key) ekliyoruz 
    log = logger.bind(key=idempotency_key[:8])

    # Idempotency Kontrolü
    if idempotency_key in idempotency_store:
        log.info(f"♻️ Tekrarlı işlem yakalandı. Arşivden dönülüyor. (Key: {idempotency_key[:8]}...)")
        cached_result = idempotency_store[idempotency_key]
        return cached_result

    log.info(f"🆕 Yetkili İstek Geldi. Tutar: {request.amount} TL")

    try:
        # Bankayı Çağır
        bank_response = call_bank_service(request.amount, x_test_mode)
        
        # Kaydet
        result = {
            "status": "cached",
            "data": bank_response,
            "message": "Payment successful"
        }
        idempotency_store[idempotency_key] = result
        
        # Cevap Ver
        response_to_user = result.copy()
        response_to_user["status"] = "success"
        
        log.info("✅ İşlem başarıyla tamamlandı ve müşteriye iletildi.")
        return response_to_user

    except CircuitBreakerError:
        log.critical("⛔ CIRCUIT BREAKER AÇIK! Sistem kendini korumaya aldı.")
        raise HTTPException(status_code=503, detail="Circuit Breaker Open")
        
    except HTTPException as e:
        # Buradaki hatayı loglamaya gerek yok, zaten yukarıda logladık
        raise e
        
    except Exception as e:
        log.exception("Beklenmeyen Kritik Hata!")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.API_PORT)