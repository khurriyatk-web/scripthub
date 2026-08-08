#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  ScriptHub — Automated Setup Script (SQLite + FastAPI + Bot + Caddy)
#  Run on your server:  sudo bash setup.sh
#
#  - Installs Python, Caddy, SQLite3
#  - Stops any old project using port 443
#  - Creates SQLite database + all tables automatically
#  - Seeds default categories + admin user
#  - Configures Caddy on port 443 (standard HTTPS)
#  - Creates systemd services for backend + bot
#  - Prompts for BOT_TOKEN, ADMIN_IDS, domain, Vercel URL
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

# ── Colors ─────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC}  $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

INSTALL_DIR="/opt/scripthub"
SERVICE_USER="scripthub"
API_PORT="8000"

info "ScriptHub Setup boshlandi (SQLite + FastAPI + Bot)..."

[[ $EUID -ne 0 ]] && error "Iltimos, root sifatida ishga tushiring: sudo bash setup.sh"

# ── 1. System packages ─────────────────────────────────────────────
info "Tizim yangilanmoqda..."
apt-get update -qq && apt-get upgrade -y -qq
info "Asosiy paketlar o'rnatilmoqda..."
apt-get install -y -qq curl wget git build-essential libssl-dev libffi-dev \
    python3 python3-pip python3-venv python3-dev sqlite3 ufw fail2ban \
    debian-keyring debian-archive-keyring apt-transport-https
ok "Asosiy paketlar o'rnatildi."

# ── 2. Stop old project on port 443 ────────────────────────────────
info "443 portni tekshirish..."
OLD_PID=$(ss -tlnp | grep ':443 ' | grep -oP 'pid=\K[0-9]+' | head -1 || true)
if [[ -n "${OLD_PID}" ]]; then
    OLD_CMD=$(ps -p "${OLD_PID}" -o comm= 2>/dev/null || echo "unknown")
    warn "443 portda ${OLD_CMD} (PID: ${OLD_PID}) ishlamoqda. To'xtatilmoqda..."
    OLD_SERVICE=$(systemctl list-units --type=service --state=running 2>/dev/null | \
        grep -iP "$(ps -p ${OLD_PID} -o args= 2>/dev/null | awk '{print $1}' | xargs basename 2>/dev/null)" | \
        awk '{print $1}' || true)
    if [[ -n "${OLD_SERVICE}" ]]; then
        systemctl stop "${OLD_SERVICE}" || true
        systemctl disable "${OLD_SERVICE}" || true
        warn "${OLD_SERVICE} to'xtatildi."
    else
        kill "${OLD_PID}" 2>/dev/null || true; sleep 2; kill -9 "${OLD_PID}" 2>/dev/null || true
    fi
    ok "Eski loyiha to'xtatildi."
else
    ok "443 port bo'sh."
fi
systemctl is-active --quiet caddy 2>/dev/null && { info "Eski Caddy to'xtatilmoqda..."; systemctl stop caddy; }

# ── 3. Caddy ──────────────────────────────────────────────────────
if ! command -v caddy &>/dev/null; then
    info "Caddy o'rnatilmoqda..."
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list >/dev/null
    apt-get update -qq && apt-get install -y -qq caddy
fi
ok "Candy: $(caddy version 2>&1 | head -1)"

# ── 4. Service user ────────────────────────────────────────────────
if ! id "${SERVICE_USER}" &>/dev/null; then
    useradd --system --create-home --shell /bin/bash "${SERVICE_USER}"
fi
ok "Service user '${SERVICE_USER}' tayyor."

# ── 5. Directory structure ─────────────────────────────────────────
info "Direktoriyalar yaratilmoqda..."
mkdir -p "${INSTALL_DIR}/backend/database" "${INSTALL_DIR}/backend/logs"
mkdir -p "${INSTALL_DIR}/backend/storage"/{projects,images,avatars,documents,videos,backup,temp}
mkdir -p "${INSTALL_DIR}/deploy"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/backend/main.py" ]]; then
    PROJECT_ROOT="${SCRIPT_DIR}"
elif [[ -f "${SCRIPT_DIR}/../backend/main.py" ]]; then
    PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
else
    warn "Backend topilmadi. backend/ va deploy/ ni ${INSTALL_DIR} ga qo'lda ko'chiring."
    PROJECT_ROOT=""
fi

if [[ -n "${PROJECT_ROOT}" ]]; then
    info "Backend fayllari nusxalanmoqda..."
    rsync -a --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' --exclude='*.db' \
        "${PROJECT_ROOT}/backend/" "${INSTALL_DIR}/backend/" 2>/dev/null || \
    cp -a "${PROJECT_ROOT}/backend/"* "${INSTALL_DIR}/backend/" 2>/dev/null || true
    cp -a "${PROJECT_ROOT}/deploy/"* "${INSTALL_DIR}/deploy/" 2>/dev/null || true
fi
chown -R "${SERVICE_USER}:${SERVICE_USER}" "${INSTALL_DIR}"
ok "Direktoriyalar: ${INSTALL_DIR}"

# ── 6. Python venv + deps ──────────────────────────────────────────
info "Python virtual environment sozlanmoqda..."
[[ ! -d "${INSTALL_DIR}/venv" ]] && python3 -m venv "${INSTALL_DIR}/venv"
chown -R "${SERVICE_USER}:${SERVICE_USER}" "${INSTALL_DIR}/venv"
info "Python bog'liqliklari o'rnatilmoqda..."
sudo -u "${SERVICE_USER}" "${INSTALL_DIR}/venv/bin/pip" install --upgrade pip -q
sudo -u "${SERVICE_USER}" "${INSTALL_DIR}/venv/bin/pip" install -r "${INSTALL_DIR}/backend/requirements.txt" -q
ok "Python bog'liqliklari o'rnatildi."

# ── 7. Prompt for config ───────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${CYAN}  ScriptHub sozlanmalari${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
warn "Telegram Bot Token olish uchun @BotFather ga /newbot yuboring."
read -rp "BOT_TOKEN: " BOT_TOKEN
echo ""
read -rp "Admin Telegram ID (@userinfobot dan oling): " ADMIN_ID
echo ""
warn "Domen nomi (DNS A record shu serverga ishora qilishi kerak)."
read -rp "Domen (masalan: scripthub.techmentor.uz): " DOMAIN
DOMAIN=${DOMAIN:-"scripthub.techmentor.uz"}
echo ""
warn "Vercel frontend URL."
read -rp "Frontend URL (masalan: https://scripthub.vercel.app): " FRONTEND_URL
FRONTEND_URL=${FRONTEND_URL:-"https://scripthub.vercel.app"}
echo ""
warn "To'lovlar uchun do'kon karta ma'lumotlari (keyin o'zgartirish mumkin)."
read -rp "Merchant karta raqami (masalan: 8600 1234 5678 9012): " MERCHANT_CARD
read -rp "Karta egasi F.I.O: " MERCHANT_HOLDER
read -rp "Bank nomi: " MERCHANT_BANK
read -rp "Telefon raqam: " MERCHANT_PHONE
echo ""
warn "Admin login uchun email va parol."
read -rp "Admin email (masalan: admin@scripthub.uz): " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-"admin@scripthub.uz"}
read -rp "Admin parol: " ADMIN_PASSWORD
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"admin123"}

# ── 8. .env file ────────────────────────────────────────────────────
ENV_FILE="${INSTALL_DIR}/backend/.env"
info ".env yaratilmoqda..."
SECRET=$(openssl rand -hex 32)
cat > "${ENV_FILE}" << ENVEOF
# ─── Telegram Bot ───
BOT_TOKEN=${BOT_TOKEN}
ADMIN_IDS=${ADMIN_ID}
BOT_USERNAME=ScriptHubBot

# ─── Web / API ───
BACKEND_URL=https://${DOMAIN}
FRONTEND_URL=${FRONTEND_URL}
API_HOST=127.0.0.1
API_PORT=${API_PORT}

# ─── Database (SQLite) ───
DATABASE_URL=sqlite+aiosqlite:///${INSTALL_DIR}/backend/database/scripthub.db

# ─── Security ───
SECRET_KEY=${SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# ─── Storage ───
STORAGE_PATH=${INSTALL_DIR}/backend/storage
MAX_UPLOAD_MB=200

# ─── Logging ───
LOG_PATH=${INSTALL_DIR}/backend/logs

# ─── Admin ───
ADMIN_EMAIL=${ADMIN_EMAIL}
ADMIN_PASSWORD=${ADMIN_PASSWORD}
ENVEOF
chown "${SERVICE_USER}:${SERVICE_USER}" "${ENV_FILE}"
chmod 600 "${ENV_FILE}"
ok ".env yaratildi."

# ── 9. Auto-create database + tables + seed data ───────────────────
info "SQLite bazasi va jadvallar avtomatik yaratilmoqda..."
DB_PATH="${INSTALL_DIR}/backend/database/scripthub.db"
mkdir -p "$(dirname "${DB_PATH}")"
chown "${SERVICE_USER}:${SERVICE_USER}" "$(dirname "${DB_PATH}")"

# Run init + seed via Python
sudo -u "${SERVICE_USER}" "${INSTALL_DIR}/venv/bin/python" -c "
import asyncio, sys, os
sys.path.insert(0, '${INSTALL_DIR}/backend')
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///${DB_PATH}'
os.environ['STORAGE_PATH'] = '${INSTALL_DIR}/backend/storage'
os.environ['LOG_PATH'] = '${INSTALL_DIR}/backend/logs'

async def main():
    from database import init_db, async_session_maker
    await init_db()
    print('Jadvallar yaratildi.')

    from services.seed_service import seed_defaults
    await seed_defaults()
    print('Seed ma\\'lumotlar kiritildi.')

    # Create admin user with email/password
    from sqlalchemy import select
    from models.user import User, Role
    from utils.security import hash_password
    import secrets
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.email == '${ADMIN_EMAIL}'))
        if not result.scalar_one_or_none():
            admin = User(
                email='${ADMIN_EMAIL}',
                password_hash=hash_password('${ADMIN_PASSWORD}'),
                role=Role.admin,
                full_name='Administrator',
                referral_code=secrets.token_urlsafe(6),
            )
            db.add(admin)
            await db.commit()
            print('Admin foydalanuvchi yaratildi.')

    # Store settings with merchant card
    from models.store_settings import StoreSettings
    async with async_session_maker() as db:
        result = await db.execute(select(StoreSettings).limit(1))
        s = result.scalar_one_or_none()
        if s:
            s.merchant_card_number = '${MERCHANT_CARD}'
            s.merchant_card_holder = '${MERCHANT_HOLDER}'
            s.merchant_bank = '${MERCHANT_BANK}'
            s.merchant_phone = '${MERCHANT_PHONE}'
            await db.commit()
            print('Do\\'kon karta ma\\'lumotlari saqlandi.')

asyncio.run(main())
" 2>&1
ok "SQLite baza: ${DB_PATH}"

# ── 10. Caddy config (port 443) ────────────────────────────────────
info "Caddy sozlanmoqda (port 443)..."
cat > /etc/caddy/Caddyfile << CADDYEOF
{
	email admin@${DOMAIN}
}

https://${DOMAIN} {
	encode gzip zstd

	@cors method OPTIONS
	handle @cors {
		header {
			Access-Control-Allow-Origin "*"
			Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
			Access-Control-Allow-Headers "Content-Type, Authorization, X-Client-Info, Apikey"
			Access-Control-Max-Age "86400"
		}
		respond 204
	}

	@static path /static/*
	handle @static {
		root * ${INSTALL_DIR}/backend/storage
		uri strip_prefix /static
		file_server
	}

	reverse_proxy 127.0.0.1:${API_PORT} {
		header_up X-Real-IP {remote_host}
		header_up X-Forwarded-For {remote_host}
		header_up X-Forwarded-Proto {scheme}
	}

	header {
		Strict-Transport-Security "max-age=31536000; includeSubDomains"
		X-Content-Type-Options "nosniff"
		X-Frame-Options "DENY"
		Referrer-Policy "strict-origin-when-cross-origin"
	}
}

http://${DOMAIN} {
	redir https://${DOMAIN}{uri} 308
}
CADDYEOF
ok "Caddyfile o'rnatildi (port 443)."

# ── 11. systemd service ────────────────────────────────────────────
info "systemd service yaratilmoqda..."
cat > /etc/systemd/system/scripthub.service << EOF
[Unit]
Description=ScriptHub Backend (FastAPI + Aiogram Bot)
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${INSTALL_DIR}/backend
EnvironmentFile=${INSTALL_DIR}/backend/.env
ExecStart=${INSTALL_DIR}/venv/bin/uvicorn main:app --host 127.0.0.1 --port ${API_PORT} --workers 1
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable scripthub caddy
ok "Service yaratildi."

# ── 12. Firewall ───────────────────────────────────────────────────
info "Firewall sozlanmoqda..."
ufw --force reset -q
ufw default deny incoming -q
ufw default allow outgoing -q
ufw allow 22/tcp -q
ufw allow 80/tcp -q
ufw allow 443/tcp -q
ufw --force enable -q
ok "Firewall: SSH(22), HTTP(80), HTTPS(443)"

# ── 13. Start services ─────────────────────────────────────────────
info "Xizmatlar ishga tushirilmoqda..."
systemctl restart caddy
systemctl restart scripthub
sleep 3

if systemctl is-active --quiet scripthub; then
    ok "ScriptHub backend ishlamoqda!"
else
    error "Backend ishga tushmadi: journalctl -u scripthub -f"
fi
if systemctl is-active --quiet caddy; then
    ok "Caddy ishlamoqda (port 443)!"
else
    warn "Candy ishga tushmadi: journalctl -u caddy -f"
fi

# ── 14. Summary ────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}  ✅ ScriptHub o'rnatish tugadi!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  Backend:     http://127.0.0.1:${API_PORT}"
echo "  Public API:  https://${DOMAIN}"
echo "  Health:      https://${DOMAIN}/health"
echo "  API Docs:    https://${DOMAIN}/api/docs"
echo "  Admin login: ${ADMIN_EMAIL}"
echo ""
echo "  Bot:         @ScriptHubBot (polling mode)"
echo "  Frontend:    ${FRONTEND_URL}"
echo ""
echo "  Buyruqlar:"
echo "    systemctl status scripthub    # Backend holati"
echo "    systemctl restart scripthub   # Backend qayta ishga tushirish"
echo "    journalctl -u scripthub -f    # Loglar"
echo "    systemctl restart caddy       # Caddy qayta ishga tushirish"
echo ""
warn "  DNS A record ${DOMAIN} -> shu server IP'siga ishora qilishi kerak."
warn "  Caddy birinchi so'rovda SSL sertifikatni avtomatik oladi."
echo ""
