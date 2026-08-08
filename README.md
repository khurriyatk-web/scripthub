# ScriptHub — Telegram Marketplace

Zamonaviy, xavfsur va kengaytiriladigan source-code marketplace tizimi.

## Arxitektura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Telegram Bot   │     │  Mini App (Vite) │     │  Admin Panel    │
│  (Aiogram)      │     │  Vercel          │     │  (FastAPI+Jinja)│
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                        │                         │
         └────────────────────────┼─────────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │     Caddy (Reverse Proxy)  │
                    │  scripthub.techmentor.uz  │
                    │         Port 3443         │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   FastAPI Backend (uvicorn)│
                    │   Port 8000 (internal)     │
                    ├────────────────────────────┤
                    │   SQLite (SQLAlchemy)      │
                    │   File Storage             │
                    │   Telegram Bot (polling)   │
                    └────────────────────────────┘
```

## Serverga o'rnatish

```bash
# 1. Loyihani serverga ko'chiring
git clone <repo> /opt/scripthub
cd /opt/scripthub

# 2. Setup skriptini ishga tushuring
sudo bash deploy/setup.sh
```

Setup.sh avtomatik:
- Python 3.13 o'rnatadi
- Caddy reverse proxy sozlaydi (port 3443, auto-SSL)
- Virtual environment yaratadi
- Barcha Python kutubxonalarini o'rnatadi
- `.env` faylini sozlaydi (bot token, admin ID so'raydi)
- systemd servislarini yaratadi
- Firewall sozlaydi
- Backendni ishga tushiradi

## DNS sozlash

`scripthub.techmentor.uz` uchun A record ni serveringiz IP'siga qo'ying.

## Frontend (Vercel)

```bash
cd frontend
npm install
npm run build
# Vercel'ga deploy qiling
```

## API hujjatlari

Backend ishga tushgandan so'ng:
- Swagger UI: `https://scripthub.techmentor.uz:3443/api/docs`
- ReDoc: `https://scripthub.techmentor.uz:3443/api/redoc`
- Health: `https://scripthub.techmentor.uz:3443/health`

## Loyiha strukturasi

```
backend/
├── config/          # Sozlamalar
├── database.py      # SQLAlchemy engine + session
├── models/          # ORM modellar (14 ta jadval)
├── services/        # Business logic
├── routes/          # FastAPI routerlar (REST API)
├── handlers/        # Telegram bot handlerlari
├── keyboards/       # Bot klavaturalari
├── utils/           # Yordamchi funksiyalar (JWT, hashing)
├── storage/         # Fayl saqlash
├── logs/            # Log fayllari
└── main.py          # FastAPI app + bot startup

deploy/
├── setup.sh         # Avtomatik o'rnatish
└── Caddyfile        # Reverse proxy sozlamasi
```

## Texnologiyalar

- **Backend:** Python 3.13, FastAPI, Aiogram 3.x, SQLAlchemy, Pydantic
- **Database:** SQLite (PostgreSQL'ga o'tish oson)
- **Proxy:** Caddy (auto-HTTPS)
- **Auth:** JWT + Telegram WebApp validation
- **Storage:** Local filesystem (UUID + SHA256 dedup)

## Boshqarish

```bash
systemctl status scripthub     # Holatni ko'rish
systemctl restart scripthub    # Qayta ishga tushirish
journalctl -u scripthub -f     # Loglarni ko'rish
systemctl restart caddy        # Proxy qayta ishga tushirish
```

## Litsenziya

MIT
