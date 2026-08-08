import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api } from '../api/client'
import { useTelegram } from '../hooks/useTelegram'
import { formatUZS } from '../utils/format'
import './Profile.css'

interface Stats {
  downloads: number
  favorites: number
  orders: number
  reviews: number
  totalSpent: number
}

interface ReferralInfo {
  code: string
  count: number
  earned: number
}

export default function Profile() {
  const { user, logout, login } = useAuth()
  const { haptic, hapticNotify, getUser } = useTelegram()
  const tgUser = getUser()
  const [stats, setStats] = useState<Stats>({ downloads: 0, favorites: 0, orders: 0, reviews: 0, totalSpent: 0 })
  const [referral, setReferral] = useState<ReferralInfo | null>(null)
  const [showRefModal, setShowRefModal] = useState(false)
  const [copied, setCopied] = useState(false)
  const [editingBio, setEditingBio] = useState(false)
  const [bioText, setBioText] = useState(user?.bio || '')
  const [savingBio, setSavingBio] = useState(false)

  useEffect(() => {
    if (!user) return
    setBioText(user.bio || '')
    Promise.all([
      api.get<{ items: { project_id: string }[] }>('/users/downloads'),
      api.get<{ items: { project_id: string }[] }>('/users/favorites'),
      api.get<{ items: { id: string; amount: number }[] }>('/orders'),
    ]).then(([d, f, o]) => {
      const orders = o.items || []
      const spent = orders.reduce((sum, ord) => sum + (ord.amount || 0), 0)
      setStats({
        downloads: d.items?.length || 0,
        favorites: f.items?.length || 0,
        orders: orders.length,
        reviews: 0,
        totalSpent: spent,
      })
    }).catch(() => {})

    if (user.referral_code) {
      setReferral({
        code: user.referral_code,
        count: 0,
        earned: 0,
      })
    }
  }, [user])

  const displayName = user?.full_name || `${tgUser?.first_name || ''} ${tgUser?.last_name || ''}`.trim() || user?.username || 'Mehmon'
  const initial = displayName[0]?.toUpperCase() || '?'
  const photoUrl = user?.photo_url || tgUser?.photo_url || null
  const username = user?.username || tgUser?.username || null
  const language = user?.language_code || tgUser?.language_code || null
  const tgId = user?.telegram_id || tgUser?.id || null
  const isPremium = Boolean(user?.is_premium)
  const joinDate = user?.created_at ? new Date(user.created_at).toLocaleDateString('uz-UZ', { year: 'numeric', month: 'long', day: 'numeric' }) : null
  const isDev = user?.role === 'developer' || user?.role === 'admin'
  const isAdmin = user?.role === 'admin'

  const copyReferral = useCallback(() => {
    if (!referral) return
    const link = `https://t.me/${import.meta.env.VITE_BOT_USERNAME || 'scripthub_bot'}?start=ref_${referral.code}`
    navigator.clipboard?.writeText(link).then(() => {
      setCopied(true)
      hapticNotify('success')
      setTimeout(() => setCopied(false), 2000)
    }).catch(() => {})
  }, [referral, hapticNotify])

  const shareReferral = useCallback(() => {
    if (!referral) return
    const link = `https://t.me/${import.meta.env.VITE_BOT_USERNAME || 'scripthub_bot'}?start=ref_${referral.code}`
    const text = `ScriptHub bozoriga qoshil! Loyihalar sotib olish va sotish uchun eng zo'r platforma.\n${link}`
    if (navigator.share) {
      navigator.share({ title: 'ScriptHub', text, url: link }).catch(() => {
        copyReferral()
      })
    } else {
      copyReferral()
    }
  }, [referral, copyReferral])

  const saveBio = useCallback(async () => {
    if (!user) return
    setSavingBio(true)
    try {
      await api.put('/users/me', { bio: bioText })
      hapticNotify('success')
      setEditingBio(false)
    } catch {
      hapticNotify('error')
    } finally {
      setSavingBio(false)
    }
  }, [user, bioText, hapticNotify])

  const handleLogin = () => {
    haptic('medium')
    login()
  }

  const achievements = [
    { icon: '🎯', label: 'Birinchi xarid', unlocked: stats.orders > 0 },
    { icon: '📚', label: '10 yuklama', unlocked: stats.downloads >= 10 },
    { icon: '❤️', label: '5 sevimli', unlocked: stats.favorites >= 5 },
    { icon: '💰', label: '100k sotuv', unlocked: stats.totalSpent >= 10000000 },
    { icon: '⭐', label: 'Sharh yozdi', unlocked: stats.reviews > 0 },
    { icon: '🔥', label: 'Faol azo', unlocked: joinDate !== null },
  ]

  return (
    <div className="profile fade-in">
      {/* ═══════════════════════════════════════════════════════════════
          HEADER CARD
          ═══════════════════════════════════════════════════════════════ */}
      <div className="profile-header glass">
        <div className="profile-header-bg" />
        <div className="profile-header-grid" />

        <div className="profile-brand-row">
          <span className="brand-pill">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.46-.57 0-7.44 4.86-7.44 4.86L5.4 11.1c-.67-.19-.69-.57.02-.82l11.42-3.61c.47-.14 1.05.12.85.86-.2.74-2.87 10.36-3.03 11.05-.12.5-.5.55-.88.17z" />
            </svg>
            Telegram
          </span>
          {isPremium && <span className="brand-pill premium">PREMIUM</span>}
          {isAdmin && <span className="brand-pill admin">ADMIN</span>}
        </div>

        <div className="avatar-section">
          <div className="avatar-ring">
            {photoUrl ? (
              <img src={photoUrl} alt={displayName} className="avatar-img" />
            ) : (
              <div className="avatar-fallback">{initial}</div>
            )}
            <span className="avatar-status" />
          </div>
          <div className="avatar-info">
            <h2 className="profile-name">{displayName}</h2>
            {username && <span className="profile-username">@{username}</span>}
            <div className="role-badges">
              {user ? (
                <span className={`role-badge ${isAdmin ? 'admin' : isDev ? 'dev' : 'member'}`}>
                  {isAdmin ? 'Administrator' : user.is_verified_developer ? 'Tasdiqlangan dasturchi' : 'Azo'}
                </span>
              ) : (
                <span className="role-badge guest">Mehmon</span>
              )}
            </div>
          </div>
        </div>

        {/* Telegram data pills */}
        <div className="tg-data-row">
          {tgId && (
            <div className="tg-data-pill">
              <span className="tg-data-icon">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M16 3h5v5"/><path d="M21 3l-7 7"/><path d="M8 21H3v-5"/><path d="M3 21l7-7"/></svg>
              </span>
              <div className="tg-data-content">
                <span className="tg-data-label">ID</span>
                <span className="tg-data-value">{tgId}</span>
              </div>
            </div>
          )}
          {language && (
            <div className="tg-data-pill">
              <span className="tg-data-icon">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              </span>
              <div className="tg-data-content">
                <span className="tg-data-label">Til</span>
                <span className="tg-data-value">{language.toUpperCase()}</span>
              </div>
            </div>
          )}
          {joinDate && (
            <div className="tg-data-pill">
              <span className="tg-data-icon">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
              </span>
              <div className="tg-data-content">
                <span className="tg-data-label">Azo</span>
                <span className="tg-data-value">{joinDate}</span>
              </div>
            </div>
          )}
        </div>

        {/* Bio */}
        {user && (
          <div className="bio-section">
            {editingBio ? (
              <div className="bio-edit">
                <textarea
                  className="input bio-textarea"
                  placeholder="Ozingiz haqida qisqacha yozing..."
                  value={bioText}
                  onChange={(e) => setBioText(e.target.value)}
                  maxLength={200}
                  rows={2}
                />
                <div className="bio-edit-actions">
                  <button className="btn btn-ghost btn-sm" onClick={() => { setEditingBio(false); setBioText(user.bio || '') }}>
                    Bekor
                  </button>
                  <button className="btn btn-primary btn-sm" onClick={saveBio} disabled={savingBio}>
                    {savingBio ? 'Saqlanmoqda...' : 'Saqlash'}
                  </button>
                </div>
              </div>
            ) : (
              <button className="bio-display" onClick={() => { setEditingBio(true); haptic('light') }}>
                <span className="bio-text">{user.bio || 'Bio qoshish uchun bosing...'}</span>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
              </button>
            )}
          </div>
        )}
      </div>

      {/* ═══════════════════════════════════════════════════════════════
          GUEST STATE — Sign-in CTA
          ═══════════════════════════════════════════════════════════════ */}
      {!user && (
        <div className="guest-cta glass">
          <div className="guest-cta-icon">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.4 5.4 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M4 16a2 2 0 0 0 2 2"/></svg>
          </div>
          <h3>Tizimga kiring</h3>
          <p>Yuklamalar, sevimlilar, xaridlar va referral dasturiga kirish uchun Telegram orqali tizimga kiring.</p>
          <button className="btn btn-primary btn-lg guest-login-btn" onClick={handleLogin}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.46-.57 0-7.44 4.86-7.44 4.86L5.4 11.1c-.67-.19-.69-.57.02-.82l11.42-3.61c.47-.14 1.05.12.85.86-.2.74-2.87 10.36-3.03 11.05-.12.5-.5.55-.88.17z"/></svg>
            Telegram bilan kiring
          </button>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════
          BALANCE CARD
          ═══════════════════════════════════════════════════════════════ */}
      {user && (
        <div className="balance-card">
          <div className="balance-card-bg" />
          <div className="balance-card-content">
            <div className="balance-top">
              <div className="balance-info">
                <span className="balance-label">Hamyon balansi</span>
                <span className="balance-amount">{formatUZS(user.balance)}</span>
              </div>
              <div className="balance-card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
              </div>
            </div>
            <div className="balance-actions">
              <button className="balance-btn" onClick={() => haptic('light')}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14"/></svg>
                To'ldirish
              </button>
              <button className="balance-btn" onClick={() => haptic('light')}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                Yechish
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════
          STATS GRID
          ═══════════════════════════════════════════════════════════════ */}
      {user && (
        <div className="stats-grid">
          <Link to="/downloads" className="stat-tile glass" onClick={() => haptic('light')}>
            <span className="stat-tile-icon blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            </span>
            <span className="stat-tile-value">{stats.downloads}</span>
            <span className="stat-tile-label">Yuklamalar</span>
          </Link>
          <Link to="/favorites" className="stat-tile glass" onClick={() => haptic('light')}>
            <span className="stat-tile-icon rose">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
            </span>
            <span className="stat-tile-value">{stats.favorites}</span>
            <span className="stat-tile-label">Sevimlilar</span>
          </Link>
          <div className="stat-tile glass">
            <span className="stat-tile-icon amber">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
            </span>
            <span className="stat-tile-value">{stats.orders}</span>
            <span className="stat-tile-label">Xaridlar</span>
          </div>
          <div className="stat-tile glass">
            <span className="stat-tile-icon green">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            </span>
            <span className="stat-tile-value-sm">{formatUZS(stats.totalSpent)}</span>
            <span className="stat-tile-label">Sarflandi</span>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════
          ACHIEVEMENTS
          ═══════════════════════════════════════════════════════════════ */}
      {user && (
        <div className="section-block">
          <div className="section-header-row">
            <h3>Yutuqlar</h3>
            <span className="section-count">{achievements.filter(a => a.unlocked).length}/{achievements.length}</span>
          </div>
          <div className="achievements-row glass">
            {achievements.map((a, i) => (
              <div key={i} className={`achievement ${a.unlocked ? 'unlocked' : 'locked'}`}>
                <span className="achievement-icon">{a.icon}</span>
                <span className="achievement-label">{a.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════
          REFERRAL CARD
          ═══════════════════════════════════════════════════════════════ */}
      {user && referral && (
        <div className="referral-card glass">
          <div className="referral-top">
            <div className="referral-icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <div className="referral-info">
              <h4>Referral dasturi</h4>
              <p>Dostlarni taklif qiling va 10% bonus oling!</p>
            </div>
          </div>
          <div className="referral-stats">
            <div className="referral-stat">
              <span className="referral-stat-value">{referral.count}</span>
              <span className="referral-stat-label">Taklif qilingan</span>
            </div>
            <div className="referral-divider" />
            <div className="referral-stat">
              <span className="referral-stat-value">{formatUZS(referral.earned)}</span>
              <span className="referral-stat-label">Daromad</span>
            </div>
          </div>
          <div className="referral-actions">
            <button className="btn btn-ghost btn-sm referral-copy-btn" onClick={copyReferral}>
              {copied ? (
                <><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg> Nusxalandi!</>
              ) : (
                <><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg> Havolani nusxalash</>
              )}
            </button>
            <button className="btn btn-primary btn-sm" onClick={shareReferral}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
              Ulashish
            </button>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════
          QUICK ACTIONS
          ═══════════════════════════════════════════════════════════════ */}
      {user && (
        <div className="section-block">
          <div className="section-header-row">
            <h3>Tezkor amallar</h3>
          </div>
          <div className="quick-actions glass">
            <Link to="/marketplace" className="quick-action" onClick={() => haptic('light')}>
              <span className="qa-icon qa-blue"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg></span>
              <span className="qa-label">Bozor</span>
            </Link>
            <Link to="/cart" className="quick-action" onClick={() => haptic('light')}>
              <span className="qa-icon qa-cyan"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg></span>
              <span className="qa-label">Savatcha</span>
            </Link>
            <Link to="/support" className="quick-action" onClick={() => haptic('light')}>
              <span className="qa-icon qa-amber"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/></svg></span>
              <span className="qa-label">Yordam</span>
            </Link>
            {isDev && (
              <Link to="/developer" className="quick-action" onClick={() => haptic('light')}>
                <span className="qa-icon qa-green"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/></svg></span>
                <span className="qa-label">Panel</span>
              </Link>
            )}
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════
          SETTINGS MENU
          ═══════════════════════════════════════════════════════════════ */}
      {user && (
        <div className="section-block">
          <div className="section-header-row">
            <h3>Sozlamalar</h3>
          </div>
          <div className="settings-menu">
            <button className="settings-item glass" onClick={() => haptic('light')}>
              <span className="settings-icon settings-blue"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg></span>
              <span className="settings-text">Profil sozlamalari</span>
              <span className="settings-arrow"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6"/></svg></span>
            </button>
            <button className="settings-item glass" onClick={() => haptic('light')}>
              <span className="settings-icon settings-amber"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg></span>
              <span className="settings-text">Bildirishnomalar</span>
              <span className="settings-toggle"><span className="toggle-track active"><span className="toggle-thumb" /></span></span>
            </button>
            <button className="settings-item glass" onClick={() => haptic('light')}>
              <span className="settings-icon settings-cyan"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg></span>
              <span className="settings-text">Ilova haqida</span>
              <span className="settings-version">v1.0.0</span>
            </button>
            <Link to="/support" className="settings-item glass" onClick={() => haptic('light')}>
              <span className="settings-icon settings-rose"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/></svg></span>
              <span className="settings-text">Qollab-quvvatlash</span>
              <span className="settings-arrow"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6"/></svg></span>
            </Link>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════
          LOGOUT
          ═══════════════════════════════════════════════════════════════ */}
      {user && (
        <button className="logout-btn glass" onClick={() => { haptic('medium'); logout() }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Tizimdan chiqish
        </button>
      )}

      {/* ═══════════════════════════════════════════════════════════════
          REFERRAL MODAL
          ═══════════════════════════════════════════════════════════════ */}
      {showRefModal && referral && (
        <div className="modal-overlay" onClick={() => setShowRefModal(false)}>
          <div className="modal-content glass" onClick={(e) => e.stopPropagation()}>
            <h3>Referral havola</h3>
            <p className="modal-ref-code">{referral.code}</p>
            <button className="btn btn-primary btn-lg" onClick={copyReferral}>
              {copied ? 'Nusxalandi!' : 'Havolani nusxalash'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
