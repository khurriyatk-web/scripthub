import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTelegram } from '../hooks/useTelegram'
import { api, setToken } from '../api/client'
import type { AuthUser } from '../types'
import './Login.css'

const LOGO_URL = 'https://i.ibb.co/NdfSqDbt/Chat-GPT-Image-8-2026-11-35-54.png'

export default function Login() {
  const { setUser, login: tgLogin } = useAuth() as { setUser: (u: AuthUser) => void; user: AuthUser | null; login: () => Promise<void> }
  const { haptic, hapticNotify, getInitData, getUser } = useTelegram()
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleTelegramLogin = async () => {
    haptic('medium')
    setError('')
    setLoading(true)
    try {
      await tgLogin()
      const initData = getInitData()
      const tgUser = getUser()
      if (initData) {
        const data = await api.post<{ token: string; user: AuthUser }>('/auth/telegram', { init_data: initData })
        setToken(data.token)
        const enriched: AuthUser = {
          ...data.user,
          photo_url: data.user.photo_url || tgUser?.photo_url,
          first_name: data.user.first_name || tgUser?.first_name,
          last_name: data.user.last_name || tgUser?.last_name,
          username: data.user.username || tgUser?.username,
          telegram_id: data.user.telegram_id || tgUser?.id,
        }
        setUser(enriched)
        hapticNotify('success')
        navigate('/')
        return
      }
      const botUsername = import.meta.env.VITE_BOT_USERNAME || 'scripthub_bot'
      window.open(`https://t.me/${botUsername}?start=login`, '_blank')
      setError('Telegram ilovasida davom eting...')
    } catch (err) {
      hapticNotify('error')
      setError((err as Error).message || 'Telegram kirishda xato')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/register'
      const body = mode === 'login'
        ? { email, password }
        : { email, password, full_name: fullName }
      const data = await api.post<{ token: string; user: AuthUser }>(endpoint, body)
      setToken(data.token)
      setUser(data.user)
      hapticNotify('success')
      navigate('/')
    } catch (err) {
      hapticNotify('error')
      setError((err as Error).message || 'Xato yuz berdi')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page fade-in">
      <div className="login-card glass">
        <div className="login-header">
          <div className="login-logo-wrap">
            <img src={LOGO_URL} alt="ScriptHub" className="login-logo-img" />
          </div>
          <h1>ScriptHub</h1>
          <p>{mode === 'login' ? 'Hisobingizga kiring' : "Ro'yxatdan o'ting"}</p>
        </div>

        <button
          className="btn btn-telegram btn-lg btn-block"
          onClick={handleTelegramLogin}
          disabled={loading}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.46-.57 0-7.44 4.86-7.44 4.86L5.4 11.1c-.67-.19-.69-.57.02-.82l11.42-3.61c.47-.14 1.05.12.85.86-.2.74-2.87 10.36-3.03 11.05-.12.5-.5.55-.88.17z" />
          </svg>
          {loading ? 'Yuklanmoqda...' : 'Telegram bilan kiring'}
        </button>

        <div className="login-divider">
          <span>yoki</span>
        </div>

        <div className="login-tabs">
          <button
            className={`login-tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => setMode('login')}
          >Kirish</button>
          <button
            className={`login-tab ${mode === 'register' ? 'active' : ''}`}
            onClick={() => setMode('register')}
          >Ro'yxat</button>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {mode === 'register' && (
            <div className="form-group">
              <label className="form-label">Ism Familiya</label>
              <input
                className="input"
                type="text"
                placeholder="Ali Valiyev"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>
          )}
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              className="input"
              type="email"
              placeholder="ali@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Parol</label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          {error && <div className="login-error">{error}</div>}

          <button
            className="btn btn-primary btn-lg btn-block"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Yuklanmoqda...' : mode === 'login' ? 'Kirish' : "Ro'yxatdan o'tish"}
          </button>
        </form>

        <p className="login-hint">
          {mode === 'login' ? "Hisobingiz yo'qmi? " : "Hisobingiz bormi? "}
          <button
            className="login-switch"
            onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          >
            {mode === 'login' ? "Ro'yxatdan o'ting" : 'Kiring'}
          </button>
        </p>
      </div>
    </div>
  )
}
