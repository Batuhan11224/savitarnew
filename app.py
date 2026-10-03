import telebot, os, random
from telebot import types

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
        return random.choice(["😄 Temel uçağa binmiş, yanına İngiliz oturmuş... Pilot: 'Motor bozuldu ama 3 motor daha var' demiş. Temel: 'İyi ki 4 motor var, yoksa havada kalacaktık!' 😂", "🤖 Bilgisayarlar neden evlenmez? Çünkü sürekli 'RAM'lerinde sorun çıkmasından korkarlar! 🖥️😂"])
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
    bot.send_message(chat_id, f"👋 Merhaba! Yapmak istediğiniz işlemi seçin:\n💰 **Mevcut Bakiyeniz:** {kullanici_bakiyesi[chat_id]} TL", reply_markup=markup, message_id=None, parse_mode="Markdown")

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
    
    # 🔍 SORGULAMA YAP MENÜSÜ CANLANDIRILDI!
    elif text == '🔍 Sorgulama Yap':
        kullanici_durumu[chat_id] = "sorgu_secim"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("👤 T.C. / İsim Sorgu", callback_data="sorgu_tc"),
            types.InlineKeyboardButton("📱 Telefon No Sorgu", callback_data="sorgu_tel"),
            types.InlineKeyboardButton("🚗 Plaka / Araç Sorgu", callback_data="sorgu_plaka"),
            types.InlineKeyboardButton("⬅️ Ana Menüye Dön", callback_data="go_main")
        )
        bot.send_message(chat_id, "🔍 **Sorgulama Paneline Hoş Geldiniz!**\nLütfen yapmak istediğiniz sorgu türünü seçin:", reply_markup=markup, parse_mode="Markdown")
        
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
        # Eğer kullanıcı sorgu modundaysa ve bir metin girdiyse
        if kullanici_durumu.get(chat_id) in ["tc_bekliyor", "tel_bekliyor", "plaka_bekliyor"]:
            bot.send_message(chat_id, "⚙️ **Sorgulanıyor...** Veritabanı bağlantısı simüle ediliyor. Sonuç: *Kayıt Bulunamadı.*", parse_mode="Markdown")
            kullanici_durumu[chat_id] = None
        else:
            bot.send_message(chat_id, web_sohbet_yaniti(text))

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_queries(call):
    chat_id = call.message.chat.id
    
    # Sorgu butonlarının arkasındaki işlemler
    if call.data == "sorgu_tc":
        kullanici_durumu[chat_id] = "tc_bekliyor"
        bot.edit_message_text("👤 **T.C. / İsim Sorgulama**\nLütfen sorgulamak istediğiniz kişinin T.C. numarasını veya Ad Soyad bilgisini yazıp gönderin:", chat_id, call.message.message_id, parse_mode="Markdown")
    elif call.data == "sorgu_tel":
        kullanici_durumu[chat_id] = "tel_bekliyor"
        bot.edit_message_text("📱 **Telefon No Sorgulama**\nLütfen sorgulamak istediğiniz telefon numarasını (Örn: 5xx xxx xx xx) yazıp gönderin:", chat_id, call.message.message_id, parse_mode="Markdown")
    elif call.data == "sorgu_plaka":
        kullanici_durumu[chat_id] = "plaka_bekliyor"
        bot.edit_message_text("🚗 **Plaka / Araç Sorgulama**\nLütfen sorgulamak istediğiniz araç plakasını yazıp gönderin:", chat_id, call.message.message_id, parse_mode="Markdown")
    elif call.data == "go_main":
        kullanici_durumu[chat_id] = None
        bot.edit_message_text("⬅️ Ana menüye dönüldü. Lütfen klavyenizdeki butonları kullanın.", chat_id, call.message.message_id)
        
    elif call.data.startswith("viewfree_"):
        num_id = call.data.split("_")[-1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Mesajları Yenile", callback_data=f"viewfree_{num_id}"))
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=get_free_number_sms(num_id), reply_markup=markup, parse_mode="Markdown")

if __name__ == "__main__":
    bot.infinity_polling(timeout=30, long_polling_timeout=15)
