from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import random
import time
import uvicorn

app = FastAPI(title="Mock Bank Service")

class PaymentRequest(BaseModel):
    amount: float

@app.post("/charge")
async def charge(
    request: PaymentRequest, 
    x_test_mode: str = Header(default="normal", alias="X-Test-Mode")
):
    """
    Artık tutara değil, 'X-Test-Mode' başlığına göre hata veriyoruz.
    Kullanıcı istediği tutarı girebilir.
    """
    print(f"Banka İsteği Geldi -> Tutar: {request.amount} | Mod: {x_test_mode}")

    # 1. SENARYO: TIMEOUT (RETRY TESTİ İÇİN)
    if x_test_mode == "timeout":
        time.sleep(5) # API timeout'undan (2sn) uzun bekletiyoruz
        raise HTTPException(status_code=408, detail="Banka Sunucusu Yanıt Vermiyor (Timeout)")

    # 2. SENARYO: CRASH (CIRCUIT BREAKER İÇİN)
    if x_test_mode == "crash":
        raise HTTPException(status_code=500, detail="Banka Veritabanı Bağlantı Hatası")

    # 3. NORMAL MOD (RASTGELELİK)
    # %80 Başarılı olsun
    if random.random() < 0.8:
        return {"status": "success", "transaction_id": str(random.randint(10000, 99999))}
    else:
        # Arada sırada gerçekçi hata versin
        raise HTTPException(status_code=500, detail="Bilinmeyen Banka Hatası")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)