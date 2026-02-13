🚀 Resilient Payment \& Backend Architecture

Bu proje, yüksek erişilebilirlik ve hata toleransı (fault-tolerance) prensipleriyle geliştirilmiş bir Ödeme Sistemi Simülasyonudur. Mikroservis mimarilerinde, dış servislerin (banka servisleri gibi) kesintiye uğradığı veya yavaşladığı senaryolarda sistemin nasıl ayakta kaldığını ve veri tutarlılığını nasıl koruduğunu gösteren uçtan uca bir mühendislik çalışmasıdır.



🛠️ Teknik Özellikler \& Tasarım Desenleri

Sistem, modern backend dünyasında kritik öneme sahip şu mekanizmalar üzerine inşa edilmiştir:



Idempotency (Mükerrer İşlem Koruması): Kullanıcının yanlışlıkla arka arkaya ödeme yapması veya ağ kopması durumunda aynı işlemin çift kez gerçekleşmesini engeller.



Circuit Breaker (Sigorta Mekanizması): Sürekli hata veren dış servisleri tespit eder ve sistemi yormamak adına trafiği otomatik olarak keserek "fail-fast" prensibini uygular.



Retry Policy (Akıllı Yeniden Deneme): Geçici ağ hatalarında, işlemi belirli zaman aralıklarıyla otomatik olarak tekrar dener.



Structured Logging: Loguru entegrasyonu ile tüm işlem akışı, hata senaryoları ve sistem durumları detaylı ve izlenebilir formatta kaydedilir.



🏗️ Mimari Yapı

Proje üç ana bileşenden oluşur:



Payment API (FastAPI): Tüm iş mantığının ve hata toleransı desenlerinin uygulandığı ana servis.



Mock Bank Service (FastAPI): Rastgele gecikmeler ve hatalar üreterek gerçek dünya senaryolarını simüle eden test servisi.



Interactive Dashboard (Streamlit): Sistemin durumunu, log akışını ve işlem sonuçlarını anlık izleyebileceğiniz görsel arayüz.



🔍 Proje Detayları ve Mantığı

Bu çalışma, dağıtık sistemlerde oluşabilecek "zincirlemeleme hataları" (cascading failures) önlemek amacıyla tasarlanmıştır.



Hata Yönetimi: Sistem, dış servisten gelen 500 hatalarını veya zaman aşımlarını (timeout) anlık olarak izler. Belirlenen hata eşiği aşıldığında Circuit Breaker "Open" (Açık) konumuna geçer. Bu durumda, sisteme gelen yeni istekler bankaya gönderilmeden doğrudan reddedilir, böylece hem banka servisinin toparlanmasına izin verilir hem de sistem kaynakları boşa harcanmaz.



Veri Tutarlılığı: Her işleme özel üretilen benzersiz anahtarlar sayesinde, ağda yaşanan bir kopukluk sonrası aynı isteğin tekrar gönderilmesi durumunda sistem bunu fark eder ve işlemi mükerrer olarak işlemez.



Gözlemlenebilirlik: Geliştirilen Dashboard, arka planda çalışan karmaşık retry ve breaker mekanizmalarını görselleştirerek, sistemin o anki "sağlık durumunu" son kullanıcıya veya operatöre şeffaf bir şekilde yansıtır.



🚀 Kurulum ve Çalıştırma

1\. Kütüphaneleri Yükleyin

Bash

pip install -r requirements.txt

2\. Yapılandırma (Önemli)

Sistemin çalışması için gereken API anahtarı kod içerisinde şu şekilde tanımlanmışıtr:

API\_SECRET\_KEY: turkcell-gncytnk-2026-alim



3\. Sistemi Tek Tıkla Başlatın

Proje klasöründeki otomasyon dosyasını çalıştırarak tüm servisleri (Bank, API, Dashboard) otomatik olarak ayrı pencerelerde ayağa kaldırabilirsiniz:



Bash

python run.py



⭐ Bu proje, dayanıklı backend mimarilerinin önemini ve uygulama yöntemlerini vurgulamak için geliştirilmiştir.

