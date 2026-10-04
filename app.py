import os
import time
import threading
import requests
import telebot
from telebot import types
import ajaxapi  # Orijinal sorgu kütüphaneniz

# .env dosyasından token ve API anahtarlarını yükleme
TOKEN = os.getenv("BOT_TOKEN")
SMS_ACTIVATE_KEY = os.getenv("SMS_ACTIVATE_KEY")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN ortam değişkeni tanımlı değil.")

bot = telebot.TeleBot(TOKEN)
BASE_URL = "https://sms-activate.org"

# Kullanıcı durum takibi
kullanici_durumu = {}

# SMS-Activate Yardımcı Fonksiyonları
def sms_api_call(action, params={}):
    """SMS-Activate API'sine güvenli istek atar."""
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
    """Arka planda SMS kodunu bekleyen fonksiyon (Thread)."""
    bot.send_message(chat_id, "⏳ Numara alındı! SMS kodu bekleniyor... (Maksimum 3 dakika)")
    
    for _ in range(36):  # 36 * 5 saniye = 3 dakika kontrol döngüsü
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
    kullanici_durumu[message.chat.id] = None  # Durumu sıfırla
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    buton1 = types.KeyboardButton('📸 Fotoğraf Bakma')
    buton2 = types.KeyboardButton('🔍 Sorgulama Yap')
    buton3 = types.KeyboardButton('📱 Sanal Numara Al')
    buton4 = types.KeyboardButton('❓ Yardım')
    
    markup.add(buton1, buton2, buton3, buton4)
    bot.send_message(message.chat.id, "👋 Merhaba! Yapmak istediğiniz işlemi seçin:", reply_markup=markup)

# 2. MESAJ VE MENÜ YÖNETİMİ
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text

    # Ana Menü Butonları
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
        # SMS-Activate Bakiye kontrolü yapıp alt menüyü açıyoruz
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
        bot.send_message(chat_id, "ℹ️ *Yardım Menüsü*\n\nİstediğiniz sorgu butonuna tıkladıktan sonra botun sizden istediği bilgileri doğru formatta yazmanız yeterlidir.\n\nSanal numara aldığınızda sistem otomatik kodu bekler.", parse_mode="Markdown")

    elif text == '🔙 Ana Menüye Dön':
        send_welcome(message)

    # --- SANAL NUMARA ALMA TETİKLEYİCİLERİ ---
    elif text in ['🤖 Telegram Numarası (tg)', '💬 WhatsApp Numarası (wa)']:
        service_code = "tg" if "Telegram" in text else "wa"
        bot.send_message(chat_id, "⚡ Numara talep ediliyor, lütfen bekleyin...")
        
        # Rusya (country=0) varsayılan olarak seçilmiştir, ihtiyaca göre değiştirilebilir
        res = sms_api_call("getNumber", {'service': service_code, 'country': 0})
        
        if "ACCESS_NUMBER" in res:
            # Örn yanıt: ACCESS_NUMBER:aktivasyon_id:telefon_numarasi
            _, activation_id, phone_number = res.split(":")
            bot.send_message(chat_id, f"📱 **Numaranız Hazır!**\n\n📞 Numara: `{phone_number}`\n\nLütfen bu numarayı ilgili uygulamaya girin.", parse_mode="Markdown")
            
            # Arka planda kodu beklemek için yeni bir thread başlatıyoruz (Bot kilitlenmesin diye)
            threading.Thread(target=sms_kod_takip, args=(chat_id, activation_id), daemon=True).start()
        else:
            bot.send_message(chat_id, f"❌ Numara alınamadı. Servis yanıtı:\n`{res}`", parse_mode="Markdown")

    # --- ALT SORGU SEÇENEKLERİNİN TETİKLENMESİ ---
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

    # --- SORGU SONUÇLARININ HESAPLANMASI ---
    else:
        durum = kullanici_durumu.get(chat_id)
        if durum is None:
            bot.send_message(chat_id, "⚠️ Lütfen önce menüden bir işlem seçin veya /start yazın.")
            return

        bot.send_message(chat_id, "⏳ Sorgulanıyor, lütfen bekleyin...")
        try:
            if durum == '🆔 TC Sorgu': sonuc = ajaxapi.tc(text)
            elif durum == '💎 TC Pro Sorgu': sonuc = ajaxapi.tc_pro(text)
            elif durum == '👨‍👩‍👧‍👦 Aile Sorgu': sonuc = ajaxapi.aile(text)
            elif durum == '🌳 Sülale Sorgu': sonuc = ajaxapi.sulale(text)
            elif durum == '📱 TC -> GSM Sorgu': sonuc = ajaxapi.tc_gsm(text)
            elif durum == '🏫 E-Okul Sorgu': sonuc = ajaxapi.eokul(text)
            elif durum == '🏠 Adres Sorgu': sonuc = ajaxapi.adres(text)
            elif durum == '📜 Tapu Sorgu': sonuc = ajaxapi.tapu(text)
            elif durum == '📞 GSM -> TC Sorgu': sonuc = ajaxapi.gsm_tc(text)
            elif durum == '👤 Ad Soyad Sorgu':
                parcalar = text.split(" ", 1)
                sonuc = ajaxapi.ad_soyad(parcalar[0], parcalar[1] if len(parcalar) > 1 else "")
            elif durum == '🗺️ Ada Parsel Sorgu':
                parcalar = text.split(",", 1)
                sonuc = ajaxapi.ada_parsel(parcalar[0].strip(), parcalar[1].strip() if len(parcalar) > 1 else "")

            temiz_durum = durum.replace("🆔 ", "").replace("💎 ", "").replace("👤 ", "").replace("👨‍👩‍👧‍👦 ", "").replace("🌳 ", "").replace("📱 ", "").replace("📞 ", "").replace("🏫 ", "").replace("🏠 ", "").replace("📜 ", "").replace("🗺️ ", "").replace(" ", "_")
            dosya_adi = f"{chat_id}_{temiz_durum}.txt"
            
            with open(dosya_adi, "w", encoding="utf-8") as f:
                f.write(f"--- {durum} SONUCU ---\n\n")
                f.write(str(sonuc))
            
            with open(dosya_adi, "rb") as doc:
                bot.send_document(chat_id, doc, caption=f"📊 *{durum}* işleminiz tamamlandı. Sonuç dosyası ektedir.", parse_mode="Markdown")
            
            if os.path.exists(dosya_adi):
                os.remove(dosya_adi)
            
        except Exception as e:
            bot.send_message(chat_id, f"❌ Sorgu sırasında bir hata oluştu veya kütüphane yanıt vermedi.\nHata: {str(e)}")
        
        kullanici_durumu[chat_id] = None

print("Telegram Botu Aktif! Sanal numara ve gelişmiş sorgu modülleri yüklendi...")
bot.infinity_polling()
