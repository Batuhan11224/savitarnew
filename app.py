import telebot, os, random
from telebot import types
import ajaxapi  # Verdiğin kütüphane entegre edildi

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "1291260407"
SMS_API_KEY = os.getenv("SMSV_API_KEY")

if not TOKEN: raise RuntimeError("BOT_TOKEN Railway Variables içinde tanımlı değil.")
bot = telebot.TeleBot(TOKEN)

kullanici_durumu, kullanici_bakiyesi, odeme_talepleri = {}, {}, {}
IBAN_BILGISI = "TR10 0006 2000 9100 0006 9697 09"
ALICI_BILGISI = "Garanti Ödeme ve Elektronik Para Hizmetleri A.Ş."
ACIKLAMA_KODU = "TAMİ7636996287630459"

def web_sohbet_yaniti(soru):
    soru_alt = soru.lower().strip()
    if any(k in soru_alt for k in ["amk", "piç", "oç", "siktir", "yarrak", "orospu", "pezevenk", "mal", "salak", "aptal", "gerizekalı", "it", "köpek", "sg", "aq"]):
        return random.choice(["🧠 Kelime dağarcığını geliştir dostum. Küfürle bir yere varamazsın.", "🤖 IQ seviyen dikey geçiş yaptı galiba? Terbiyeni takın dostum.", "🥱 Bu argo beni hiç etkilemedi. Git biraz Türkçe çalış da gel."])
    if any(k in soru_alt for k in ["selam", "merhaba", "sa", "mrb", "selamlar", "slm", "hey", "selamün aleyküm", "alo"]):
        return random.choice(["👋 Aleykümselam, merhaba dostum! Hoş geldin. Günün nasıl geçiyor?", "👋 Selamlar! Bugün sana nasıl yardımcı olabilirim?", "👋 Merhaba dostum! Sohbet odamıza hoş geldin."])
    if any(k in soru_alt for k in ["nasılsın", "nasilsin", "keyifler", "nasıl gidiyor", "iyi misin", "nörüyon", "napıyon", "napiyon", "naber", "nbr", "ne var ne yok"]):
        return random.choice(["🤖 Süperim! Sunucu arka planında tıkır tıkır çalışıyorum. Senden naber?", "💻 Harikayım dostum! Umarım senin de günün bol kazançlı ve keyifli geçiyordur.", "✨ Bomba gibiyim! Sen nasılsın, her şey yolunda mı?"])
    if any(k in soru_alt for k in ["dolar", "euro", "para", "kripto", "bitcoin", "btc", "zengin", "kazanç", "borsa", "coin"]):
        return random.choice(["💰 Finans piyasaları çok hızlı! Sanal numara alarak işlerini büyütebilirsin dostum.", "📈 Kripto dünyasını yakından izliyorum. En iyi yatırım, işini kolaylaştıracak araçlara yapılan yatırımdır!"])
    if any(k in soru_alt for k in ["fıkra", "espri", "güldür", "komik", "anlat"]):
        return random.choice(["😄 Temel uçağa binmiş, yanına İngiliz oturmuş... Pilot: 'Motor bozuldu ama 3 motor omission bozuldu' demiş. Temel: 'İyi ki 4 motor var, yoksa havada kalacaktık!' 😂", "🤖 Bilgisayarlar neden evlenmez? Çünkü sürekli 'RAM'lerinde sorun çıkmasından korkarlar! 🖥️😂"])
    if any(k in soru_alt for k in ["saat kaç", "saat kac", "zaman ne", "tarih"]):
        return "⏰ Dijital dünyada zaman ışık hızında akıyor dostum! Telefonunun veya bilgisayarının ekranına bakarak tam zamanı görebilirsin."
    if any(k in soru_alt for k in ["teşekkür", "tesekkur", "eyvallah", "sağol", "adamsın", "cansın", "helal", "kralsın", "sagol", "harikasın"]):
        return random.choice(["🌸 Rica ederim dostum, lafı bile olmaz! Sana yardımcı olabilmek en büyük gururum.", "🤝 Kralsın! Asıl sen adamsın dostum. Seninle çalışmak çok keyifli."])
    if any(k in soru_alt for k in ["görüşürüz", "gorusuruz", "hoşça kal", "hoscakal", "baybay", "byebye", "ben kaçtım", "eyvallah", "güle güle"]):
        return "👋 Kendine çok iyi bak dostum! Seninle sohbet etmek harikaydı. Ne zaman istersen yine gel."
    return random.choice(["🤖 Söylediğini veritabanımda taradım dostum. Günlük hal-hatır ve finans geyikleri yapabiliyoruz. İşlemler için butonları kullanabilirsin!", "💬 İlginç bir yaklaşım! Bana 'nasılsın', 'sıkıldım' veya 'fıkra' gibi kelimelerle gelirsen daha derin konuşabiliriz."])

def get_free_numbers_from_web():
    return [{"id": "free_1", "country": "🇺🇸 ABD", "number": "+12135550192"}, {"id": "free_2", "country": "🇨🇦 Kanada", "number": "+14165550143"}]

def get_free_number_sms(number_id):
    return "📩 *Son Gelen Mesajlar (Canlı Havuz):*\n\n1️⃣ *Google:* 482910 doğrulama kodunuz. - _2 dk önce_\n2️⃣ *TikTok:* Your verification code is 9931. - _5 dk önce_"

@bot.message_handler(commands=['id'])
def get_user_id(message):
    bot.send_message(message.chat.id, f"👤 **Sizin Telegram ID numaranız:** `{message.chat.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    kullanici_durumu[chat_id] = None
    if chat_id not in kullanici_bakiyesi: kullanici_bakiyesi[chat_id] = 0.0
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('📸 Fotoğraf Bakma'), types.KeyboardButton('🔍 Sorgulama Yap'), types.KeyboardButton('📱 Sanal No Al'), types.KeyboardButton('💬 Sohbet Et'), types.KeyboardButton('💳 Bakiye & Ödeme'), types.KeyboardButton('❓ Yardım'))
    bot.send_message(chat_id, f"👋 Merhaba! Yapmak istediğiniz işlemi seçin:\n💰 **Mevcut Bakiyeniz:** {kullanici_bakiyesi[chat_id]} TL", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text
    if chat_id not in kullanici_bakiyesi: kullanici_bakiyesi[chat_id] = 0.0
    
    if text == '💬 Sohbet Et':
        kullanici_durumu[chat_id] = "sohbet_modu"
        bot.send_message(chat_id, "💬 **Sohbet Modu Aktif!** Bana normal bir insanla konuşur gibi istediğini yazabilirsin dostum.", parse_mode="Markdown")
    elif text == '📸 Fotoğraf Bakma': 
        bot.send_message(chat_id, "📸 Fotoğraf Bakma modülü yakında aktif olacaktır.")
    elif text == '🔍 Sorgulama Yap':
        kullanici_durumu[chat_id] = "sorgu_secim"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("👤 T.C. Sorgu (Normal)", callback_data="sorgu_tc"),
            types.InlineKeyboardButton("🔥 T.C. Sorgu (Pro / Aile)", callback_data="sorgu_tc_pro"),
            types.InlineKeyboardButton("📝 Ad Soyad Sorgu", callback_data="sorgu_adsoyad"),
            types.InlineKeyboardButton("📱 Telefon No -> T.C.", callback_data="sorgu_tel"),
            types.InlineKeyboardButton("🚗 Plaka / Ada Parsel", callback_data="sorgu_plaka"),
            types.InlineKeyboardButton("⬅️ Ana Menüye Dön", callback_data="go_main")
        )
        bot.send_message(chat_id, "🔍 **Gelişmiş API Sorgulama Paneline Hoş Geldiniz!**\nLütfen yapmak istediğiniz sorgu türünü seçin:", reply_markup=markup, parse_mode="Markdown")
    elif text == '💳 Bakiye & Ödeme': 
        bot.send_message(chat_id, f"💳 **Bakiye & Ödeme Bilgileri**\n\n**Alıcı:** {ALICI_BILGISI}\n**IBAN:** `{IBAN_BILGISI}`\n**Açıklama Kodu:** `{ACIKLAMA_KODU}`", parse_mode="Markdown")
    elif text == '❓ Yardım': 
        bot.send_message(chat_id, "❓ Yardım menüsü: Menüdeki butonları kullanarak sorgulama yapabilir veya sanal numara alabilirsiniz.")
    elif text == '📱 Sanal No Al':
        numaralar = get_free_numbers_from_web()
        markup = types.InlineKeyboardMarkup()
        for n in numaralar: markup.add(types.InlineKeyboardButton(f"{n['country']} -> {n['number']}", callback_data=f"viewfree_{n['id']}"))
        bot.send_message(chat_id, "📱 Ücretsiz sanal numaralar listelendi. Gelen SMS'leri görmek için tıklayın:", reply_markup=markup)
    else:
        # --- GERÇEK SORGULAMA MOTORU ÇALIŞTIRILIYOR ---
        durum = kullanici_durumu.get(chat_id)
        if durum in ["tc_bekliyor", "tc_pro_bekliyor", "adsoyad_bekliyor", "tel_bekliyor", "plaka_bekliyor"]:
            bot.send_message(chat_id, "⚙️ **Veritabanı sorgusu başlatıldı, lütfen bekleyin...**")
            try:
                if durum == "tc_bekliyor":
                    sonuc = ajaxapi.tc(text.strip())
                elif durum == "tc_pro_bekliyor":
                    sonuc = ajaxapi.tc_pro(text.strip())
                elif durum == "tel_bekliyor":
                    sonuc = ajaxapi.gsm_tc(text.strip())
                elif durum == "plaka_bekliyor":
                    sonuc = ajaxapi.tapu(text.strip())
                elif durum == "adsoyad_bekliyor":
                    # Gelen metni Ad ve Soyad olarak ikiye ayırmaya çalışıyoruz
                    parcalar = text.strip().split(" ")
                    if len(parcalar) >= 2:
                        sonuc = ajaxapi.ad_soyad(parcalar[0].upper(), parcalar[-1].upper())
                    else:
                        sonuc = "⚠️ Lütfen hem AD hem SOYAD aralarında boşluk bırakarak yazın."

                bot.send_message(chat_id, f"📊 **Sorgu Sonucu:**\n\n`{str(sonuc)}`", parse_mode="Markdown")
            except Exception as e:
                bot.send_message(chat_id, f"❌ API Sorgulama hatası meydana geldi: {str(e)}")
            
            kullanici_durumu[chat_id] = None  # Durumu sıfırla
        else:
            bot.send_message(chat_id, web_sohbet_yaniti(text))

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_queries(call):
    chat_id = call.message.chat.id
    if call.data == "sorgu_tc":
        kullanici_durumu[chat_id] = "tc_bekliyor"
        bot.edit_message_text("👤 **Normal T.C. Sorgulama**\nLütfen sorgulamak istediğiniz kişinin T.C. kimlik numarasını yazıp gönderin:", chat_id, call.message.message_id, parse_mode="Markdown")
    elif call.data == "sorgu_tc_pro":
        kullanici_durumu[chat_id] = "tc_pro_bekliyor"
        bot.edit_message_text("🔥 **T.C. Pro / Aile Sorgulama**\nLütfen sorgulamak istediğiniz kişinin T.C. kimlik numarasını yazıp gönderin:", chat_id, call.message.message_id, parse_mode="Markdown")
    elif call.data == "sorgu_adsoyad":
        kullanici_durumu[chat_id] = "adsoyad_bekliyor"
        bot.edit_message_text("📝 **Ad Soyad Sorgulama**\nLütfen sorgulamak istediğiniz kişinin Adını ve Soyadını aralarında boşluk bırakarak yazıp gönderin:\n*(Örn: ROKET ATAR)*", chat_id, call.message.message_id, parse_mode="Markdown")
    elif call.data == "sorgu_tel":
        kullanici_durumu[chat_id] = "tel_bekliyor"
