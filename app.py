import os
import time
import threading
import requests
import telebot
from telebot import types
from dotenv import load_dotenv  # Çevre değişkenlerini zorla yüklemek için eklendi
import ajaxapi  # Orijinal sorgu kütüphaneniz

# Hem yereldeki .env dosyasını hem de Railway Variables panelini koda yükler
load_dotenv()

# .env veya Railway panelinden token ve API anahtarlarını çekme
TOKEN = os.getenv("BOT_TOKEN")
SMS_ACTIVATE_KEY = os.getenv("SMS_ACTIVATE_KEY")

print("==================================================")
print(f"📡 [BAŞLANGIÇ KONTROLÜ] BOT_TOKEN Durumu: {'✅ YÜKLENDİ' if TOKEN else '❌ BULUNAMADI!'}")
print(f"📡 [BAŞLANGIÇ KONTROLÜ] SMS_ACTIVATE_KEY Durumu: {'✅ YÜKLENDİ' if SMS_ACTIVATE_KEY else '❌ BULUNAMADI!'}")
print("==================================================")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN ortam değişkeni tanımlı değil. Lütfen Railway paneline ekleyin.")

bot = telebot.TeleBot(TOKEN)
BASE_URL = "https://sms-activate.org"

# Kullanıcı durum takibi
kullanici_durumu = {}

# --- Gelişmiş Dosya İçeriği Düzenleyici (Formatlayıcı) ---
def formatla_sonuc(veri, baslik_turu):
    """Gelen karmaşık sözlük (dict), liste (list) veya string veriyi sıralı ve okunaklı hale getirir."""
    metin = f"=========================================\n"
    metin += f"📊 {baslik_turu.upper()} SORGULAMA SONUCU\n"
    metin += f"=========================================\n\n"
    
    # Eğer veri bir liste ise (Örn: Aile/Sülale listesi gelmişse)
    if isinstance(veri, list):
        for sira, eleman in enumerate(veri, 1):
            metin += f"📌 [{sira}] KİŞİ / KAYIT BİLGİSİ:\n"
            if isinstance(eleman, dict):
                for k, v in eleman.items():
                    anahtar = str(k).replace("_", " ").title()
                    metin += f"   • {anahtar}: {v}\n"
            else:
                metin += f"   • {eleman}\n"
            metin += f"{'-'*40}\n"
            
    # Eğer veri bir sözlük/JSON ise (Örn: Tek bir TC veya Adres sonucu gelmişse)
    elif isinstance(veri, dict):
        for k, v in veri.items():
            # Eğer iç içe liste veya sözlük varsa
            if isinstance(v, (dict, list)):
                anahtar = str(k).replace("_", " ").title()
                metin += f"\n📂 {anahtar} BÖLÜMÜ:\n"
                metin += formatla_sonuc(v, "")  # İç içe yapıyı temizle
            else:
                anahtar = str(k).replace("_", " ").title()
                metin += f"• {anahtar}: {v}\n"
                
    # Eğer düz metin geldiyse ancak içinde virgüller/süslü parantezler varsa temizle
    else:
        veri_str = str(veri).strip()
        # Basit string temizleme ve alt alta sıralama denemesi
        if "," in veri_str and ":" in veri_str:
            veri_str = veri_str.replace("{", "").replace("}", "").replace("'", "").replace('"', "")
            parcalar = veri_str.split(",")
            for p in parcalar:
                if ":" in p:
                    k, v = p.split(":", 1)
                    metin += f"• {k.strip().replace('_', ' ').title()}: {v.strip()}\n"
                else:
                    metin += f"• {p.strip()}\n"
        else:
            metin += f"{veri_str}\n"
            
    metin += f"\n=========================================\n"
    metin += f"Oluşturulma Tarihi: {time.strftime('%d.%m.%Y %H:%M:%S')}\n"
    return metin

# SMS-Activate Yardımcı Fonksiyonları
def sms_api_call(action, params={}):
    if not SMS_ACTIVATE_KEY:
        return "ERROR_NO_API_KEY"
    default_params = {'api_key': SMS_ACTIVATE_KEY, 'action': action}
    default_params.update(params)
    try:
        response = requests.get(BASE_URL, params=default_params, timeout=10)
        return response.text
    except Exception as e:
        return f"ERROR_{str(e)}"

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
        types.KeyboardButton('📸 Fotoğraf Bakma'), types.KeyboardButton('🔍 Sorgulama Yap'),
        types.KeyboardButton('📱 Sanal Numara Al'), types.KeyboardButton('❓ Yardım')
    )
    bot.send_message(message.chat.id, "👋 Merhaba! Yapmak istediğiniz işlemi seçin:", reply_markup=markup)

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
        bot.send_message(chat_id, "📝 Lütfen sorgulanacak **GSM Numarasını** yazın\n_(Örn: 5550000000)_:", parse_mode="Markdown")

    elif text == '🗺️ Ada Parsel Sorgu':
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, "📝 Lütfen İl ve İlçe bilgisini aralarında virgül bırakarak yazın\n_(Örn: İSTANBUL, KADIKÖY)_:")

    else:
        durum = kullanici_durumu.get(chat_id)
        if durum is None:
            bot.send_message(chat_id, "⚠️ Lütfen önce menüden bir işlem seçin veya /start yazın.")
            return

        kullanici_durumu[chat_id] = None
        dosya_adi = None

        try:
            # Girdi doğrulamaları
            if durum in ['🆔 TC Sorgu', '💎 TC Pro Sorgu', '👨‍👩‍👧‍👦 Aile Sorgu', '🌳 Sülale Sorgu', '📱 TC -> GSM Sorgu', '🏫 E-Okul Sorgu', '🏠 Adres Sorgu', '📜 Tapu Sorgu']:
                if len(text.strip()) != 11 or not text.strip().isdigit():
                    bot.send_message(chat_id, "❌ Hata: Lütfen geçerli bir **11 haneli sayısal** TC Kimlik Numarası girin.", parse_mode="Markdown")
                    return
            elif durum == '📞 GSM -> TC Sorgu':
                if not text.strip().isdigit() or len(text.strip()) < 10:
                    bot.send_message(chat_id, "❌ Hata: Lütfen geçerli bir GSM numarası girin.")
                    return
            elif durum == '👤 Ad Soyad Sorgu':
                parcalar = text.strip().split(" ", 1)
