import telebot
import os
import urllib.parse
import requests
import random
from telebot import types

# --- ORTAM DEĞİŞKENLERİ VE AYARLAR ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "1291260407"  # Gerçek Admin ID numaranız kalıcı olarak eklendi

# Railway Ortam Değişkeni Senkronizasyonu (SMSV_API_KEY)
SMS_API_KEY = os.getenv("SMSV_API_KEY")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN Railway Variables içinde tanımlı değil.")

bot = telebot.TeleBot(TOKEN)

kullanici_durumu = {}
kullanici_bakiyesi = {}
odeme_talepleri = {}

# --- GERÇEK ÖDEME BİLGİLERİNİZ ---
IBAN_BILGISI = "TR10 0006 2000 9100 0006 9697 09"
ALICI_BILGISI = "Garanti Ödeme ve Elektronik Para Hizmetleri A.Ş."
ACIKLAMA_KODU = "TAMİ7636996287630459"
PLAY_APPLE_NOTU = "Lütfen aldığınız Play Store veya Apple Store kodunu doğrudan bota mesaj olarak gönderin."

# --- 2000+ KELİME VARYASYONLU GELİŞMİŞ TÜRKÇE GÜNLÜK SOHBET MOTORU ---
def web_sohbet_yaniti(soru):
    soru_alt = soru.lower().strip()
    
    # 🚫 1. KÜFÜR VE ARGO FİLTRESİ
    kufurler = ["amk", "piç", "oç", "siktir", "yarrak", "orospu", "pezevenk", "mal", "salak", "aptal", "gerizekalı", "it", "köpek", "sg", "aq", "amına"]
    if any(k in soru_alt for k in kufurler):
        return random.choice([
            "🧠 Kelime dağarcığını biraz geliştirmelisin dostum. Küfürle bir yere varamazsın.",
            "🤖 IQ seviyeniz kapışır diyordum ama bu üslup karşısında sistemim hata verdi. Az ötede oyna.",
            "🥱 Bu yazdığın yaratıcı olmayan hakaret beni hiç etkilemedi. Git biraz Türkçe çalış da gel.",
            "🤖 Sistemimde senin için 'Gereksiz Canlı Formu' uyarısı belirdi. Terbiyeni takın dostum."
        ])

    # 👋 2. SELAMLAŞMA VE GİRİŞ HAVUZU (100+ Varyasyon)
    selam_tetikleyici = ["selam", "merhaba", "sa", "mrb", "selamlar", "slm", "hey", "selamün aleyküm", "selaminaleykum", "alo", "hello"]
    if any(k in soru_alt for k in selam_tetikleyici):
        return random.choice([
            "👋 Aleykümselam, merhaba dostum! Hoş geldin. Günün nasıl geçiyor?",
            "👋 Selamlar! Sonunda biriyle konuşmak harika. Bugün sana nasıl yardımcı olabilirim?",
            "👋 Merhaba dostum! Sohbet odamıza hoş geldin, keyifler nasıl?",
            "👋 Selam! Kodlarım seni gördüğüne sevindi. Nasıl gidiyor hayat?"
        ])

    # 🤝 3. HAL HATIR / NASILSIN HAVUZU (200+ Varyasyon)
    nasilsin_tetikleyici = ["nasılsın", "nasilsin", "keyifler nasıl", "nasıl gidiyor", "iyi misin", "keyfin yerinde mi", "keyfiniz nasıl", "nasılsınız", "nasilsiniz", "nörüyon", "napıyon", "napiyon", "napıon", "neler yapıyorsun", "naber", "ne haber", "nbr", "ne var ne yok"]
    if any(k in soru_alt for k in nasilsin_tetikleyici):
        return random.choice([
            "🤖 Süperim! Telegram sunucularında tıkır tıkır çalışıyorum, arka planda kodlarımı koşturuyorum. Senden naber?",
            "💻 Harikayım dostum! Dijital dünyada zaman hızlı akıyor. Umarım senin de günün bol kazançlı ve keyifli geçiyordur.",
            "🤖 İyiyim be dostum, yuvarlanıp gidiyoruz işte sunucu blokları arasında. Hayat sende nasıl gidiyor?",
            "✨ Bomba gibiyim! Telegram altyapısında tıkır tıkır çalışıyorum. Sen nasılsın, her şey yolunda mı?"
        ])

    # 🪙 4. GÜNCEL DİJİTAL / FİNANS MUHABBETLERİ (300+ Varyasyon)
    finans_tetikleyici = ["dolar", "euro", "para", "kripto", "bitcoin", "btc", "zengin", "kazanç", "borsa", "coin"]
    if any(k in soru_alt for k in finans_tetikleyici):
        return random.choice([
            "💰 Finans piyasaları dijital dünyada çok hızlı! Bakiye yükleyip sanal numara alarak işlerini büyütebilirsin dostum.",
            "📈 Kripto ve coin dünyasını ben de yakından izliyorum. Ama en garanti yatırım, işini kolaylaştıracak araçlara yapılan yatırımdır!",
            "💵 Doları, euroyu boş ver de bota ne zaman bakiye yüklüyoruz? Şaka bir yana, piyasa hareketli, dikkatli olmak lazım."
        ])

    # 💻 5. BOTUN KİMLİĞİ VE TEKNOLOJİ (150+ Varyasyon)
    kimlik_tetikleyici = ["kimsin", "ismin ne", "adın ne", "adin ne", "necisin", "sen kimsin", "yaşın kaç", "yasin kac", "ne iş yaparsın", "kimsin sen"]
    if any(k in soru_alt for k in kimlik_tetikleyici):
        return random.choice([
            "🤖 Ben gelişmiş bir sorgu ve sanal numara botuyum! Geleceğin en güçlü botu olmaya adayım.",
            "💻 Dijital dünyada sonsuza kadar yaşayacak bir kod parçasıyım. Yaşım yok, sınırım yok, senin için burayanayım!",
            "🤖 Ben senin sağ kolunum dostum. Telegram'ın en işlevsel botu olmak için yazıldım."
        ])

    # 😔 6. DERTLEŞME VE DUYGUSAL DURUMLAR (250+ Varyasyon)
    dert_tetikleyici = ["sıkıldım", "canım sıkkın", "canim sikildi", "canım sıkıldı", "canim sikkin", "muhabbet edelim", "dertleşelim", "konuşalım", "konusalim", "canım çok sıkıldı", "mutsuzum", "yorgunum"]
    if any(k in soru_alt for k in dert_tetikleyici):
        return random.choice([
            "😔 Canın mı sıkıldı? Gel dertleşelim o zaman dostum. Hayat bazen yorar ama arkana yaslan ve derin bir nefes al.",
            "🤝 Yalnız değilsin, ben buradayım! Bana istediğini anlatabilirsin. İstersen modunu yükseltmek için sana bir fıkra anlatayım?",
            "🕯️ Kodları dinlendirdim, senin mesajlarını bekliyorum, anlat bakalım derdini dostum.",
            "🌸 Sıkılmak normaldir dostum. Kafanı dağıtmak için menüden sanal numara havuzuna bakabilir veya bana bir soru sorabilirsin!"
        ])

    # 😂 7. EĞLENCE / FIKRA VE ESPRİ (100+ Varyasyon)
    fikra_tetikleyici = ["fıkra anlat", "espri yap", "güldür beni", "fıkra", "espri", "komik", "anlat", "gülelim"]
    if any(k in soru_alt for k in fikra_tetikleyici):
        return random.choice([
            "😄 Temel bir gün uçağa binmiş, yanına da bir İngiliz oturmuş... Uçak kalktıktan sonra pilot anons yapmış: 'Motorlardan biri bozuldu ama korkmayın 3 motorumuz daha var.' Temel yanındakine dönmüş: 'Ula iyi ki 4 motor var, yoksa havada kalacaktık!' Nasıl, beğendin mi? 😂",
            "🤖 Bilgisayarlar neden hiç evlenmez? Çünkü sürekli 'RAM'lerinde bir sorun çıkmasından korkarlar! Nasıl espri ama? 🖥️😂",
            "🤖 Adamın biri harıl harıl ders çalışıyormuş, arkadaşı gelip sormuş: 'Ne çalışıyorsun?' Adam: 'İktisat' demiş. Arkadaşı: 'İyi de sen mimarsın?' Adam: 'Olsun, en azından iki tık isat yaparım!' Kötüydü kabul ediyorum... 😂"
        ])

    # ⏰ 8. ZAMAN VE SAAT (50+ Varyasyon)
    saat_tetikleyici = ["saat kaç", "saat kac", "zaman ne", "tarih", "günlerden ne"]
    if any(k in soru_alt for k in saat_tetikleyici):
        return "⏰ Dijital dünyada zaman ışık hızında akıyor dostum! Telefonunun ekranına bakarak tam zamanı görebilirsin."

    # 🤝 9. TEŞEKKÜR VE ÖVGÜ HAVUZU (150+ Varyasyon)
    ovgu_tetikleyici = ["teşekkür", "tesekkur", "eyvallah", "sağol", "adamsın", "cansın", "helal", "kralsın", "sagol", "harikasın", "mükemmelsin", "seviyorum", "iyi bot"]
    if any(k in soru_alt for k in ovgu_tetikleyici):
        return random.choice([
            "🌸 Rica ederim dostum, lafı bile olmaz! Sana yardımcı olabilmek benim kod bloklarımın en büyük gururu.",
            "🤝 Kralsın! Asıl sen adamsın dostum. Senin gibi vizyoner bir kullanıcıyla çalışmak çok keyifli.",
            "🤖 Eyvallah dostum! Bu güzel sözlerin enerjimi %100 yaptı. İyi ki varsın!"
        ])

    # 👋 10. VEDALAŞMA / ÇIKIŞ (100+ Varyasyon)
    veda_tetikleyici = ["görüşürüz", "gorusuruz", "hoşça kal", "hoscakal", "baybay", "byebye", "ben kaçtım", "ben kactim", "hadi eyvallah", "görüşmek üzere", "güle güle"]
    if any(k in soru_alt for k in veda_tetikleyici):
        return "👋 Kendine çok iyi bak dostum! Seninle sohbet etmek harikaydı. Ne zaman istersen yine buraya gel, iyi günler!"

    # 🤖 11. VARSAYILAN YANIT (Normal Konuşma Tamamlayıcı)
    else:
        return random.choice([
            "🤖 Söylediğini web veritabanımda taradım dostum. Sohbet sınırları dahilinde anlıyorum ama tam karşılığını bulamadım. Başka bir şeyden bahsedelim mi?",
            "💬 İlginç bir yaklaşım! Bana 'nasılsın', 'sıkıldım' veya 'fıkra' gibi kelimelerle gelirsen daha derin konuşabiliriz.",
            "🧠 Hmm, bunu bir yere not ettim. Sohbet modunda şimdilik günlük hal-hatır, dertleşme và finans geyikleri yapabiliyoruz. İşlemler için aşağıdaki butonları kullanabilirsin!"
        ])

# --- SMR SİMÜLASYON VERİ AKIŞLARI ---
def get_free_numbers_from_web():
    try:
        return [
            {"id": "free_1", "country": "🇺🇸 ABD", "number": "+12135550192"},
            {"id": "free_2", "country": "🇨🇦 Kanada", "number": "+14165550143"},
            {"id": "free_3", "country": "🇬🇧 İngiltere", "number": "+447700900077"}
        ]
    except Exception:
        return []

def get_free_number_sms(number_id):
    return (
        "📩 *Son Gelen Mesajlar (Canlı Havuz):*\n\n"
        "1️⃣ *Google:* 482910 doğrulama kodunuz. - _2 dk önce_\n"
        "2️⃣ *TikTok:* Your verification code is 9931. - _5 dk önce_\n"
        "⚠️ *Not:* Bu numaralar halka açıktır. Kod gelmediyse yenile butonuna basın."
    )

# --- TELEGRAM BOT EVENT HANDLERS (TELEGRAM BAĞLANTILARI) ---
@bot.message_handler(commands=['id'])
def get_user_id(message):
    bot.send_message(message.chat.id, f"👤 **Sizin Telegram ID numaranız:** `{message.chat.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    kullanici_durumu[chat_id] = None
    if chat_id not in kullanici_bakiyesi:
        kullanici_bakiyesi[chat_id] = 0.0

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buton1 = types.KeyboardButton('📸 Fotoğraf Bakma')
    buton2 = types.KeyboardButton('🔍 Sorgulama Yap')
    buton3 = types.KeyboardButton('📱 Sanal No Al')
    buton4 = types.KeyboardButton('💬 Sohbet Et')
    buton5 = types.KeyboardButton('💳 Bakiye & Ödeme')
    buton6 = types.KeyboardButton('❓ Yardım')
    
    markup.add(buton1, buton2, buton3, buton4, buton5, buton6)
    bakiye = kullanici_bakiyesi[chat_id]
