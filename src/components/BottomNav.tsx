import { NavLink } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import { useAuth } from '../context/AuthContext'
import './BottomNav.css'

const HomeIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />
    <path d="M9 22V12h6v10" />
  </svg>
)

const ShopIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z" />
    <path d="M3 6h18" />
    <path d="M16 10a4 4 0 0 1-8 0" />
  </svg>
)

const HeartIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
  </svg>
)

const DownloadIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
)

const ProfileIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
)

const items = [
  { to: '/', icon: <HomeIcon />, label: 'Bosh' },
  { to: '/marketplace', icon: <ShopIcon />, label: 'Bozor' },
  { to: '/favorites', icon: <HeartIcon />, label: 'Sevim' },
  { to: '/downloads', icon: <DownloadIcon />, label: 'Fayl' },
]

export default function BottomNav() {
  const { haptic } = useTelegram()
  const { user } = useAuth()
  const tg = window.Telegram?.WebApp
  const tgUser = tg?.initDataUnsafe?.user
  const photoUrl = user?.photo_url || tgUser?.photo_url || null
  const initial = (user?.full_name || tgUser?.first_name || '?')[0]?.toUpperCase()

  return (
    <div className="bottom-nav-wrapper">
      <nav className="bottom-nav">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            onClick={() => haptic('light')}
          >
            <span className="nav-icon-bg" />
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
        <NavLink
          to="/profile"
          className={({ isActive }) => `nav-item nav-profile ${isActive ? 'active' : ''}`}
          onClick={() => haptic('light')}
        >
          <span className="nav-icon-bg" />
          <span className="nav-icon nav-profile-icon">
            {photoUrl ? (
              <img src={photoUrl} alt="Profil" className="nav-avatar" />
            ) : (
              <span className="nav-avatar-fallback">{initial}</span>
            )}
          </span>
          <span className="nav-label">Profil</span>
        </NavLink>
      </nav>
    </div>
  )
}
