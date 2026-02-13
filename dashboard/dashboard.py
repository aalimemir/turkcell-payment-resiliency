import streamlit as st
import requests
import uuid
import datetime
import pandas as pd # <--- YENİ: Veri analizi ve Excel çıktısı için
import plotly.graph_objects as go # <--- Grafikler için kral kütüphane

# --- AYARLAR ---
st.set_page_config(page_title="GNÇYTNK | Alim Emir Aydoğan Staj Projesi", page_icon="📶", layout="wide")

# --- TURKCELL TEMA & CSS ---
st.markdown("""
<style>
    /* GİZLEME KODLARI */
    header[data-testid="stHeader"], .stDeployButton, footer {visibility: hidden;}
    .block-container {padding-top: 2rem;}

    /* TEMA RENKLERİ */
    .stApp {background: linear-gradient(to bottom, #002855, #001233); color: #FFFFFF;}
    .stTextInput input, .stNumberInput input {
        background-color: #00346b; color: white; border: 1px solid #FFC900; border-radius: 8px;
    }
    
    /* BUTONLAR */
    .stButton>button {
        background-color: #FFC900 !important; color: #000000 !important; font-weight: 800 !important;
        border-radius: 25px !important; border: none !important; height: 3.5em !important;
        font-size: 18px !important; transition: all 0.1s ease;
    }
    .stButton>button:active {transform: scale(0.95);}
    
    /* SEKME (TABS) TASARIMI */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.1); border-radius: 8px; color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFC900 !important; color: black !important; font-weight: bold;
    }

    /* DİĞER BİLEŞENLER */
    [data-testid="stSidebar"] {background-color: #001f3f; border-right: 2px solid #FFC900;}
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px;
    }
    .header-line {height: 4px; background: linear-gradient(90deg, #FFC900, #FFFFFF); margin-bottom: 20px; border-radius: 2px;}
    
    .msg-box {padding: 15px; border-radius: 12px; margin-bottom: 10px; font-size: 16px; border-left: 5px solid;}
</style>
""", unsafe_allow_html=True)

# --- HAFIZA ---
if 'idempotency_key' not in st.session_state:
    st.session_state.idempotency_key = str(uuid.uuid4())
if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- FONKSİYONLAR ---
def new_key():
    st.session_state.idempotency_key = str(uuid.uuid4())

def add_log(title, detail, type="info"):
    # Zaman damgasını ve saniye
    st.session_state.logs.insert(0, {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title, 
        "detail": detail, 
        "type": type, 
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    })

# --- KPI ---
def render_kpis():
    total_tx = len(st.session_state.logs)
    success_tx = len([x for x in st.session_state.logs if x['type'] == 'success'])
    error_tx = len([x for x in st.session_state.logs if x['type'] == 'error'])
    
    success_rate = 0
    if total_tx > 0:
        success_rate = int((success_tx / total_tx) * 100)
        
    color_rate = "#22c55e" if success_rate >= 80 else "#ef4444"
    
    health_status = "MÜKEMMEL 🟢"
    if error_tx > success_tx and total_tx > 5:
        health_status = "KRİTİK 🔴"
    elif error_tx > 2:
        health_status = "RİSKLİ 🟡"

    ph_m1.markdown(f"""
    <div style="background-color: #00346b; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #FFC900;">
        <span style="color: #ccc; font-size: 0.8em;">TOPLAM İŞLEM</span><br>
        <span style="color: white; font-size: 1.5em; font-weight: bold;">{total_tx}</span>
    </div>""", unsafe_allow_html=True)

    ph_m2.markdown(f"""
    <div style="background-color: #00346b; padding: 10px; border-radius: 10px; text-align: center; border-bottom: 4px solid {color_rate};">
        <span style="color: #ccc; font-size: 0.8em;">BAŞARI ORANI</span><br>
        <span style="color: {color_rate}; font-size: 1.5em; font-weight: bold;">%{success_rate}</span>
    </div>""", unsafe_allow_html=True)

    ph_m3.markdown(f"""
    <div style="background-color: #00346b; padding: 10px; border-radius: 10px; text-align: center;">
        <span style="color: #ccc; font-size: 0.8em;">HATALI İŞLEM</span><br>
        <span style="color: #ef4444; font-size: 1.5em; font-weight: bold;">{error_tx}</span>
    </div>""", unsafe_allow_html=True)

    ph_m4.markdown(f"""
    <div style="background-color: #00346b; padding: 10px; border-radius: 10px; text-align: center;">
        <span style="color: #ccc; font-size: 0.8em;">SİSTEM SAĞLIĞI</span><br>
        <span style="color: white; font-size: 1.2em; font-weight: bold;">{health_status}</span>
    </div>""", unsafe_allow_html=True)

# --- SOL MENÜ ---
with st.sidebar:
    st.markdown("### ⚙️ Kontrol Paneli")
    st.markdown("---")
    
    # Güvenlik
    api_key_input = st.text_input("API Erişim Anahtarı", type="password")
    TARGET_PASSWORD = "turkcell-gncytnk-2026-alim"
    
    if api_key_input == TARGET_PASSWORD:
        st.success("Kilit Açıldı ✅")
    elif api_key_input != "":
        st.error("Erişim Kısıtlı 🔒")
    
    st.markdown("---")

    # Audit Log Export 
    if st.session_state.logs:
        st.write("📂 **Raporlama**")
        df_logs = pd.DataFrame(st.session_state.logs)
        csv = df_logs.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Denetim Kaydı İndir (CSV)",
            data=csv,
            file_name=f'turkcell_audit_log_{datetime.datetime.now().strftime("%H%M%S")}.csv',
            mime='text/csv',
        )
    
    st.markdown("---")

    scenario_map = {
        "🟢 Normal Akış": "normal",
        "🟡 Retry Testi (Timeout)": "timeout",
        "🔴 Circuit Breaker (Crash)": "crash"
    }
    selected_label = st.radio("Test Senaryosu:", list(scenario_map.keys()), on_change=new_key)
    active_mode = scenario_map[selected_label]
    
    st.markdown("---")
    if st.button("🔄 Yeni Müşteri"):
        new_key()
        st.rerun()
    
    st.caption("GNÇYTNK Staj Projesi Alim Emir Aydoğan")

# --- ANA EKRAN ---
st.title(" Turkcell Finansal İşlem Merkezi")
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

# KPI KUTULARI (Placeholder)
m1, m2, m3, m4 = st.columns(4)
ph_m1 = m1.empty()
ph_m2 = m2.empty()
ph_m3 = m3.empty()
ph_m4 = m4.empty()
render_kpis()

st.markdown("###")

# --- SEKMELİ YAPI (YENİ) ---
tab1, tab2 = st.tabs(["💳 ÖDEME TERMİNALİ", "📈 ANALİZ MERKEZİ"])

# --- TAB 1: TERMİNAL & LOGLAR (Eski Ana Ekran) ---
with tab1:
    col_main, col_right = st.columns([2, 1])

    with col_main:
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            amount = c1.number_input("Tutar (TL)", value=150.0, step=50.0, on_change=new_key)
            c2.text_input("Idempotency Key", value=st.session_state.idempotency_key, disabled=True)
            
            st.markdown("###")
            btn_pay = st.button("TURKCELL PAY İLE ÖDE", type="primary")

        if btn_pay:
            status_placeholder = st.empty()
            with status_placeholder.status("🚀 İşlem Buluta İletiliyor...", expanded=True) as status:
                try:
                    headers = {
                        "Idempotency-Key": st.session_state.idempotency_key,
                        "X-Test-Mode": active_mode,
                        "X-API-Key": api_key_input 
                    }
                    response = requests.post("http://127.0.0.1:8000/pay", json={"amount": amount}, headers=headers)
                    
                    msg_html = ""
                    if response.status_code == 200:
                        data = response.json()
                        status.update(label="İşlem Başarılı!", state="complete", expanded=False)
                        if data.get("status") == "cached":
                            msg = "🛡️ ÇİFTE ÖDEME KORUMASI"
                            desc = "Tekrarlı işlem engellendi."
                            add_log(msg, desc, "warning")
                            msg_html = f'<div class="msg-box warning" style="background-color: rgba(234, 179, 8, 0.2); border-color: #FFC900; color: #fef08a;"><b>{msg}</b><br>{desc}</div>'
                        else:
                            msg = "✅ ÖDEME ONAYLANDI"
                            desc = f"Tutar: {amount} TL başarıyla çekildi."
                            add_log(msg, desc, "success")
                            msg_html = f'<div class="msg-box success" style="background-color: rgba(34, 197, 94, 0.2); border-color: #22c55e; color: #dcfce7;"><b>{msg}</b><br>{desc}</div>'
                    elif response.status_code == 401:
                        status.update(label="YETKİSİZ", state="error", expanded=False)
                        msg = "⛔ GÜVENLİK UYARISI"
                        desc = "Geçersiz Anahtar!"
                        add_log(msg, desc, "error")
                        msg_html = f'<div class="msg-box error" style="background-color: rgba(239, 68, 68, 0.2); border-color: #ef4444; color: #fee2e2;"><b>{msg}</b><br>{desc}</div>'
                    elif response.status_code == 503:
                        status.update(label="SİSTEM KAPALI", state="error", expanded=False)
                        msg = "⚡ CIRCUIT BREAKER AÇILDI"
                        desc = "Sistem koruma modunda."
                        add_log(msg, desc, "error")
                        msg_html = f'<div class="msg-box error" style="background-color: rgba(239, 68, 68, 0.2); border-color: #ef4444; color: #fee2e2;"><b>{msg}</b><br>{desc}</div>'
                    else:
                        status.update(label="HATA", state="error", expanded=False)
                        msg = f"❌ HATA ({response.status_code})"
                        desc = "İşlem başarısız."
                        add_log(msg, desc, "error")
                        msg_html = f'<div class="msg-box error" style="background-color: rgba(239, 68, 68, 0.2); border-color: #ef4444; color: #fee2e2;"><b>{msg}</b><br>{desc}</div>'
                    
                    render_kpis()
                    st.markdown(msg_html, unsafe_allow_html=True)
                except Exception as e:
                    st.error("Backend'e ulaşılamadı!")

    with col_right:
        st.subheader("📊 Canlı Log Akışı")
        if not st.session_state.logs:
            st.info("İşlem bekleniyor...")
        for log in st.session_state.logs:
            border = "#22c55e" if log["type"]=="success" else "#ef4444" if log["type"]=="error" else "#FFC900"
            icon = "✅" if log["type"]=="success" else "⚡" if log["type"]=="error" else "🛡️"
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.05); border-left: 4px solid {border}; padding: 10px; margin-bottom: 8px; border-radius: 5px;">
                <small style="color: #ccc;">{log['time']}</small><br>
                <b style="color: white;">{icon} {log['title']}</b><br>
                <span style="font-size: 0.9em; color: #ddd;">{log['detail']}</span>
            </div>""", unsafe_allow_html=True)


# --- TAB 2: ANALİZ MERKEZİ (YENİ GRAFİK EKRANI) ---
with tab2:
    st.subheader("📈 İşlem Dağılım Analizi")
    
    if len(st.session_state.logs) > 0:
        # Veriyi Hazırla
        df = pd.DataFrame(st.session_state.logs)
        
        # Grafiğe az, tabloya çok yer verelim ([1, 2] oranı)
        col_chart1, col_chart2 = st.columns([1, 2])
        
        with col_chart1:
            with col_chart1:
             st.markdown("##### İşlem Tipi Dağılımı")
            
            
            # 1. Veriyi hazırla
            counts = df['type'].value_counts()
            
            # 2. Renkleri duruma göre eşle (Turkcell renk paleti)
            color_map = {
                'success': '#22c55e', # Yeşil
                'warning': '#FFC900', # Sarı
                'error': '#ef4444'    # Kırmızı
            }
            # Mevcut verilere göre renk listesi oluştur
            colors = [color_map.get(x, '#cccccc') for x in counts.index]

            # 3. Grafiği oluştur
            fig = go.Figure(data=[go.Pie(
                labels=counts.index.str.upper(), # Etiketler (SUCCESS, WARNING vb.)
                values=counts.values,            # Değerler
                hole=.5,                         # Ortası delik olsun (Donut)
                marker=dict(colors=colors, line=dict(color='#001f3f', width=2)), # Kenarlık rengi
                textinfo='label+percent',        # Üstünde ne yazsın
                textfont_size=14,
                hoverinfo='label+value+percent'  # Üzerine gelince ne çıksın
            )])

            # 4. Grafiğin arka planını şeffaf yap ve düzenle
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h", # Yatay lejant
                    yanchor="bottom", y=-0.2,
                    xanchor="center", x=0.5,
                    font=dict(color="white")
                ),
                paper_bgcolor='rgba(0,0,0,0)', # Şeffaf arka plan
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=50, l=0, r=0), # Kenar boşlukları
                height=350
            )

            # 5. Ekrana bas
            st.plotly_chart(fig, use_container_width=True)
            
            
        with col_chart2:
            st.markdown("##### Detaylı İşlem Dökümü")
            
            
            
            display_df = df[['time', 'title', 'detail', 'type']].copy()
            display_df.columns = ['Saat', 'İşlem Başlığı', 'Detay', 'Durum']
            
            #  Pandas Styler ile boyama işlemi
            styled_table = display_df.style.set_properties(**{
                # Hücrelerin içi 
                'background-color': '#001f3f',
                'color': '#e0e0e0', # Hafif kırık beyaz yazı
                'border-bottom': '1px solid #00346b' # Satır aralarına ince çizgi
            }).set_table_styles([
                # Başlık Satırı Tasarımı
                {'selector': 'th', 'props': [
                    ('background-color', '#002855'), # Başlık daha koyu lacivert
                    ('color', '#FFC900'),            # Başlık yazısı Turkcell Sarısı
                    ('font-weight', 'bold'),
                    ('border-bottom', '3px solid #FFC900') # Başlığın altına kalın sarı çizgi
                ]},
                # Fare ile üzerine gelince (Hover) parlasın
                {'selector': 'tbody tr:hover', 'props': [
                    ('background-color', '#00346b !important') 
                ]}
            ])
            
            # 3. Süslenmiş tabloyu ekrana basalım
            st.dataframe(
                styled_table, 
                use_container_width=True,
                height=400,     # Yükseklik sınırı (scroll çıkar)
                hide_index=True # En baştaki 0,1,2 numaralarını gizle
            )
            # ===============================================================
            
    else:
        st.info("Analiz için henüz yeterli veri yok. Lütfen işlem yapınız.")