import { useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useTelegram } from '../hooks/useTelegram'
import './Support.css'

export default function Support() {
  const { user } = useAuth()
  const { haptic, hapticNotify } = useTelegram()
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user) return
    haptic('medium')
    try {
      await api.put('/users/me', { bio: `${subject}: ${message}` })
      hapticNotify('success')
      setSent(true)
      setSubject('')
      setMessage('')
    } catch {
      hapticNotify('error')
    }
  }

  return (
    <div className="support fade-in">
      <h1 className="page-title">Yordam</h1>
      <p className="support-intro">Savol yoki muammo bormi? Xabar yuboring, tez orada javob beramiz.</p>

      {sent && (
        <div className="support-success glass">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          Xabaringiz yuborildi! Tez orada javob beramiz.
        </div>
      )}

      <form className="support-form glass" onSubmit={handleSubmit}>
        <label className="form-label">Mavzu</label>
        <input
          className="input"
          placeholder="Muammoning qisqa tavsifi"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          required
        />
        <label className="form-label">Xabar</label>
        <textarea
          className="input"
          placeholder="Muammoni batafsil yozing..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={5}
          required
        />
        <button type="submit" className="btn btn-primary btn-lg">Xabar yuborish</button>
      </form>

      <div className="support-faq glass">
        <h3>Tez javoblar</h3>
        <div className="faq-item">
          <p className="faq-q">Qanday qilib kod sotib olaman?</p>
          <p className="faq-a">Bozorni ko'ring, loyihani tanlang va "Sotib olish" tugmasini bosing.</p>
        </div>
        <div className="faq-item">
          <p className="faq-q">Qanday qilib kod sotaman?</p>
          <p className="faq-a">Profildan dasturchi huquqi oling, keyin loyihalar qo'shing.</p>
        </div>
        <div className="faq-item">
          <p className="faq-q">Pul qaytarish shartlari?</p>
          <p className="faq-a">Xariddan keyin 24 soat ichida yordam bilan bog'laning.</p>
        </div>
      </div>
    </div>
  )
}
