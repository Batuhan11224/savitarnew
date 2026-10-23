import os
import time
import threading
import requests
import telebot
from telebot import types
from dotenv import load_dotenv  

# Hem yereldeki .env dosyasını hem de sunucu paneli (Railway/Render vb.) değişkenlerini yükler
load_dotenv()

# Ortam değişkenlerinden token ve API anahtarlarını çekme
TOKEN = os.getenv("BOT_TOKEN")
SMS_ACTIVATE_KEY = os.getenv("SMS_ACTIVATE_KEY")

print("==================================================")
print(f"📡 [BAŞLANGIÇ KONTROLÜ] BOT_TOKEN Durumu: {'✅ YÜKLENDİ' if TOKEN else '❌ BULUNAMADI!'}")
print(f"📡 [BAŞLANGIÇ KONTROLÜ] SMS_ACTIVATE_KEY Durumu: {'✅ YÜKLENDİ' if SMS_ACTIVATE_KEY else '❌ BULUNAMADI!'}")
print("==================================================")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN ortam değişkeni tanımlı değil. Lütfen panelinize ekleyin.")

bot = telebot.TeleBot(TOKEN)

# API isteklerinin gideceği doğru steward uç noktası
BASE_URL = "https://sms-activate.org"

# Kullanıcı durum takibi
kullanici_durumu = {}

# Orijinal sorgu kütüphaneniz
try:
    import ajaxapi  
except ImportError:
    print("⚠️ UYARI: 'ajaxapi' modülü bulunamadı! Sorgu fonksiyonları çalışmayabilir.")

# --- ✨ YENİ: Gelişmiş Düzenli Rapor Formatlayıcı (Tablo Yapısı) ---
def formatla_sonuc(veri, baslik_turu):
    """Gelen verileri okunaklı, hizalı ve çizgili bir tablo (Rapor) formatına getirir."""
    if not baslik_turu:
        baslik_turu = "DETAY"
        
    metin =  "╔══════════════════════════════════════════════════════════════════════════╗\n"
    metin += f"║ 📊 {baslik_turu.upper().center(68)} ║\n"
    metin += "╚══════════════════════════════════════════════════════════════════════════╝\n\n"
    
    # --- DURUM 1: Birden Fazla Kişi/Kayıt Listesi Gelmişse (Sıralı Tablo) ---
    if isinstance(veri, list):
        for sira, eleman in enumerate(veri, 1):
            metin += f"◤ Kayıt No: #{sira} ───────────────────────────────────────────────────────┐\n"
            if isinstance(eleman, dict):
                max_len = max([len(str(k)) for k in eleman.keys()]) if eleman else 10
                for k, v in eleman.items():
                    anahtar = str(k).replace("_", " ").title()
                    metin += f"  │  • {anahtar.ljust(max_len + 2)} : {v}\n"
            else:
                metin += f"  │  • Bilgi: {eleman}\n"
            metin += f"└────────────────────────────────────────────────────────────────────────┘\n\n"
            
    # --- DURUM 2: Tek Bir Kişiye Ait Detaylı Sözlük Verisi Gelmişse ---
    elif isinstance(veri, dict):
        max_len = max([len(str(k)) for k in veri.keys()]) if veri else 10
        metin += "┌── Bilgiler ─────────────────────────────────────────────────────────────┐\n"
        for k, v in veri.items():
            if isinstance(v, (dict, list)):
                anahtar = str(k).replace("_", " ").title()
                metin += f"│\n├── 📂 {anahtar} Alt Bölümü ──────────────────────────────────────────\n"
                alt_metin = formatla_sonuc(v, "ALT BÖLÜM")
                # Alt metindeki gereksiz başlık çizgilerini kırpıp hizalı şekilde ekler
                kırpılmıs_hatlar = [line for line in alt_metin.split("\n") if "══" not in line and "📊" not in line]
                metin += "\n".join([f"│   {line}" for line in kırpılmıs_hatlar if line.strip()]) + "\n"
            else:
                anahtar = str(k).replace("_", " ").title()
                metin += f"│  • {anahtar.ljust(max_len + 2)} : {v}\n"
        metin += "└─────────────────────────────────────────────────────────────────────────┘\n"
                
    # --- DURUM 3: Düz Metin / Karmaşık String Yapısı Gelmişse ---
    else:
        veri_str = str(veri).strip()
        if "," in veri_str and ":" in veri_str:
            veri_str = veri_str.replace("{", "").replace("}", "").replace("'", "").replace('"', "")
            parcalar = veri_str.split(",")
            metin += "┌─────────────────────────────────────────────────────────────────────────┐\n"
            for p in parcalar:
                if ":" in p:
                    k, v = p.split(":", 1)
                    anahtar = k.strip().replace('_', ' ').title()
                    metin += f"│  • {anahtar.ljust(20)} : {v.strip()}\n"
                else:
                    metin += f"│  • {p.strip()}\n"
            metin += "└─────────────────────────────────────────────────────────────────────────┘\n"
        else:
            metin += f"📝 Sonuç Notu:\n{veri_str}\n"
            
    metin += f"\n👉 Raporlama Sistemi tarafından otomatik üretilmiştir.\n"
    metin += f"🕒 Oluşturulma Tarihi: {time.strftime('%d.%m.%Y %H:%M:%S')}\n"
    return metin

# SMS-Activate API Çağrı Fonksiyonu
def sms_api_call(action, params={}):
    if not SMS_ACTIVATE_KEY:
        return "ERROR_NO_API_KEY"
    
    default_params = {
        'api_key': str(SMS_ACTIVATE_KEY).strip(), 
        'action': action
    }
    default_params.update(params)
    
    try:
        response = requests.get(BASE_URL, params=default_params, timeout=12)
        return response.text.strip()
    except Exception as e:
        return f"ERROR_{str(e)}"

# SMS Kod Takip Arka Plan İşlemi
def sms_kod_takip(chat_id, activation_id):
    bot.send_message(chat_id, "⏳ Numara alındı! SMS kodu bekleniyor... (Maksimum 3 dakika)")
    for _ in range(36):
        time.sleep(5)
        res = sms_api_call("getStatus", {'id': activation_id})
        if "STATUS_OK" in res:
            kod = res.split(":")[1]
            bot.send_message(chat_id, f"✅ **SMS KODU GELDİ!**\n\n🔑 Kodunuz: `{kod}`", parse_mode="Markdown")
            return
        elif "STATUS_WAIT_CODE" not in res:
            bot.send_message(chat_id, f"⚠️ SMS durumu değişti veya iptal edildi: {res}")
            return
    bot.send_message(chat_id, "❌ 3 dakika boyunca SMS kodu gelmedi. İşlem zaman aşımına uğradı.")

# 1. ANA MENÜ (/start)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    kullanici_durumu[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('📸 Fotoğraf Bakma'),
        types.KeyboardButton('🔍 Sorgulama Yap'),
        types.KeyboardButton('📱 Sanal Numara Al'),
        types.KeyboardButton('❓ Yardım')
    )
    bot.send_message(
        message.chat.id,
        "👋 Merhaba! Yapmak istediğiniz işlemi seçin:",
        reply_markup=markup
    )

# 2. MESAJ VE MENÜ YÖNETİMİ
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text

    if text == '📸 Fotoğraf Bakma':
        bot.send_message(chat_id, "📸 Fotoğraf bakma menüsündesiniz. Lütfen bir görsel gönderin.")
        
    elif text in ['🔍 Sorgulama Yap', '🔙 Sorgu Menüsüne Dön']:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(
            types.KeyboardButton('🆔 TC Sorgu'), types.KeyboardButton('💎 TC Pro Sorgu'),
            types.KeyboardButton('👤 Ad Soyad Sorgu'), types.KeyboardButton('👨‍👩‍👧‍👦 Aile Sorgu'),
            types.KeyboardButton('🌳 Sülale Sorgu'), types.KeyboardButton('📱 TC -> GSM Sorgu'),
            types.KeyboardButton('📞 GSM -> TC Sorgu'), types.KeyboardButton('🏫 E-Okul Sorgu'),
            types.KeyboardButton('🏠 Adres Sorgu'), types.KeyboardButton('📜 Tapu Sorgu'),
            types.KeyboardButton('🗺️ Ada Parsel Sorgu'), types.KeyboardButton('🔙 Ana Menüye Dön')
        )
        bot.send_message(chat_id, "🔍 Lütfen yapmak istediğiniz detaylı sorgu türünü seçin:", reply_markup=markup)

    elif text == '📱 Sanal Numara Al':
        bakiye_res = sms_api_call("getBalance")
        bakiye = bakiye_res.split(":")[1] if "ACCESS_BALANCE" in bakiye_res else "0.00"
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(
            types.KeyboardButton('🤖 Telegram Numarası (tg)'),
            types.KeyboardButton('💬 WhatsApp Numarası (wa)'),
            types.KeyboardButton('🔙 Ana Menüye Dön')
        )
        bot.send_message(chat_id, f"💳 **SMS-Activate Bakiyeniz:** {bakiye} RUB\n\nLütfen numara almak istediğiniz servisi seçin:", parse_mode="Markdown", reply_markup=markup)

    elif text == '❓ Yardım':
        bot.send_message(chat_id, "ℹ️ *Yardım Menüsü*\n\nİstediğiniz sorgu butonuna tıkladıktan sonra botun sizden istediği bilgileri doğru formatta yazmanız yeterlidir.", parse_mode="Markdown")

    elif text == '🔙 Ana Menüye Dön':
        send_welcome(message)

    elif text in ['🤖 Telegram Numarası (tg)', '💬 WhatsApp Numarası (wa)']:
        service_code = "tg" if "Telegram" in text else "wa"
        bot.send_message(chat_id, "⚡ Numara talep ediliyor, lütfen bekleyin...")
        res = sms_api_call("getNumber", {'service': service_code, 'country': 0})
        if "ACCESS_NUMBER" in res:
            _, activation_id, phone_number = res.split(":")
            bot.send_message(chat_id, f"📱 **Numaranız Hazır!**\n\n📞 Numara: `{phone_number}`\n\nLütfen bu numarayı ilgili uygulamaya girin.", parse_mode="Markdown")
            threading.Thread(target=sms_kod_takip, args=(chat_id, activation_id), daemon=True).start()
        else:
            bot.send_message(chat_id, f"❌ Numara alınamadı. Servis yanıtı:\n`{res}`", parse_mode="Markdown")

    elif text in ['🆔 TC Sorgu', '💎 TC Pro Sorgu', '👨‍👩‍👧‍👦 Aile Sorgu', '🌳 Sülale Sorgu', '📱 TC -> GSM Sorgu', '🏫 E-Okul Sorgu', '🏠 Adres Sorgu', '📜 Tapu Sorgu']:
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, f"📝 Lütfen sorgulanacak **11 haneli TC Kimlik Numarasını** yazın:", parse_mode="Markdown")

    elif text == '👤 Ad Soyad Sorgu':
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, "📝 Lütfen aralarında bir boşluk bırakarak **AD SOYAD** yazın\n_(Örn: ROKET ATAR)_:", parse_mode="Markdown")

    elif text == '📞 GSM -> TC Sorgu':
        kullanici_durumu[chat_id] = text

if __name__ == "__main__":
    print("🤖 Telegram botu başlatılıyor...")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
