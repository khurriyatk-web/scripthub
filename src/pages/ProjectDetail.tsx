import { useParams, useNavigate, Link } from 'react-router-dom'
import { useEffect, useState, useRef } from 'react'
import { api } from '../api/client'
import type { Project, Review } from '../types'
import { useTelegram } from '../hooks/useTelegram'
import { useAuth } from '../context/AuthContext'
import { formatUZS } from '../utils/format'
import './ProjectDetail.css'

interface MerchantCard {
  merchant_card_number: string
  merchant_card_holder: string
  merchant_bank: string
  merchant_phone: string
}

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { haptic, hapticNotify, tg } = useTelegram()
  const { user } = useAuth()
  const [project, setProject] = useState<Project | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [purchased, setPurchased] = useState(false)
  const [isFavorite, setIsFavorite] = useState(false)
  const [showPayment, setShowPayment] = useState(false)
  const [merchantCard, setMerchantCard] = useState<MerchantCard | null>(null)
  const [cardNumber, setCardNumber] = useState('')
  const [cardHolder, setCardHolder] = useState('')
  const [paying, setPaying] = useState(false)
  const [orderId, setOrderId] = useState<string | null>(null)
  const [screenshotFile, setScreenshotFile] = useState<File | null>(null)
  const [screenshotPreview, setScreenshotPreview] = useState<string | null>(null)
  const [paymentSubmitted, setPaymentSubmitted] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!id) return
    Promise.all([
      api.get<Project>(`/projects/${id}`),
      api.get<{ items: Review[] }>(`/reviews/${id}`),
    ]).then(([p, r]) => {
      setProject(p)
      setReviews(r.items || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (!project || !user) return
    api.get<{ items: { project_id: string }[] }>('/orders').then(({ items }) => {
      setPurchased(items?.some((o) => o.project_id === project.id) || false)
    }).catch(() => {})

    api.get<{ items: { project_id: string }[] }>('/users/favorites').then(({ items }) => {
      setIsFavorite(items?.some((f) => f.project_id === project.id) || false)
    }).catch(() => {})
  }, [project, user])

  const handleBuy = async () => {
    if (!project || !user) return
    haptic('medium')
    try {
      const order = await api.post<{ id: string; status: string; amount: number }>('/orders', { project_id: project.id })
      if (order.status === 'completed') {
        hapticNotify('success')
        setPurchased(true)
      } else {
        setOrderId(order.id)
        const mc = await api.get<MerchantCard>('/payments/merchant-card')
        setMerchantCard(mc)
        setShowPayment(true)
      }
    } catch (e) {
      hapticNotify('error')
      alert((e as Error).message)
    }
  }

  const handleScreenshotSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setScreenshotFile(file)
    setScreenshotPreview(URL.createObjectURL(file))
    haptic('light')
  }

  const handleCardPay = async () => {
    if (!orderId || !cardNumber || !cardHolder) return
    haptic('medium')
    setPaying(true)
    try {
      await api.post('/payments/card', {
        order_id: orderId,
        buyer_card_number: cardNumber,
        buyer_card_holder: cardHolder,
      })

      if (screenshotFile) {
        const formData = new FormData()
        formData.append('file', screenshotFile)
        formData.append('order_id', orderId)
        try {
          await api.upload('/upload/payment-screenshot', formData)
        } catch { /* screenshot optional */ }
      }

      hapticNotify('success')
      setShowPayment(false)
      setPaymentSubmitted(true)
    } catch (e) {
      hapticNotify('error')
      alert((e as Error).message)
    } finally {
      setPaying(false)
    }
  }

  const handleCancelPayment = () => {
    haptic('light')
    setShowPayment(false)
    setCardNumber('')
    setCardHolder('')
    setScreenshotFile(null)
    setScreenshotPreview(null)
  }

  const handleDownload = () => {
    haptic('medium')
    if (project?.github_link) {
      const base = import.meta.env.VITE_API_BASE?.replace('/api', '') || 'https://scripthub.techmentor.uz'
      tg?.openLink?.(`${base}/static/${project.github_link}`)
    }
  }

  const toggleFavorite = async () => {
    if (!project || !user) return
    haptic('light')
    try {
      if (isFavorite) {
        await api.delete(`/users/favorites/${project.id}`)
        setIsFavorite(false)
      } else {
        await api.post(`/users/favorites/${project.id}`)
        setIsFavorite(true)
      }
    } catch { /* ignore */ }
  }

  if (loading) {
    return (
      <div className="detail-loading">
        <div className="skeleton" style={{ height: 200, borderRadius: 14, marginBottom: 16 }} />
        <div className="skeleton" style={{ height: 60, borderRadius: 14, marginBottom: 8 }} />
        <div className="skeleton" style={{ height: 120, borderRadius: 14 }} />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="empty-state">
        <div className="empty-icon-wrap">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 8v4" />
            <path d="M12 16h.01" />
          </svg>
        </div>
        <p>Loyiha topilmadi</p>
        <Link to="/marketplace" className="btn btn-primary" style={{ marginTop: 16 }}>Bozorga qaytish</Link>
      </div>
    )
  }

  const price = project.discount_percent && project.discount_percent > 0
    ? Math.round(project.price * (1 - project.discount_percent / 100))
    : project.price
  const isFree = price === 0
  const hasDiscount = project.discount_percent && project.discount_percent > 0

  return (
    <div className="project-detail fade-in">
      <button className="back-btn" onClick={() => navigate(-1)}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="19" y1="12" x2="5" y2="12" />
          <polyline points="12 19 5 12 12 5" />
        </svg>
        Orqaga
      </button>

      <div className="detail-hero glass">
        <div className="detail-hero-glow" />
        <div className="detail-icon-wrap">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="16 18 22 12 16 6" />
            <polyline points="8 6 2 12 8 18" />
          </svg>
        </div>
        <h1 className="detail-title">{project.name}</h1>
        <p className="detail-short">{project.short_description}</p>
        <div className="detail-stats">
          <div className="detail-stat">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
            {Number(project.rating_avg).toFixed(1)}
            <span className="detail-stat-sub">({project.rating_count})</span>
          </div>
          <div className="detail-stat">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            {project.sales_count} sotuv
          </div>
        </div>
      </div>

      <div className="detail-section glass">
        <h3>Tavsif</h3>
        <p className="detail-full">{project.full_description || project.short_description}</p>
      </div>

      {project.technologies && (
        <div className="detail-section glass">
          <h3>Texnologiyalar</h3>
          <div className="tech-tags">
            {project.technologies.split(',').map((t) => (
              <span key={t.trim()} className="tag">{t.trim()}</span>
            ))}
          </div>
        </div>
      )}

      {project.requirements && (
        <div className="detail-section glass">
          <h3>Talablar</h3>
          <p className="detail-full">{project.requirements}</p>
        </div>
      )}

      {project.license && (
        <div className="detail-section glass">
          <h3>Litsenziya</h3>
          <div className="file-format-badge">{project.license}</div>
        </div>
      )}

      <div className="detail-section glass">
        <h3>Sharhlar ({reviews.length})</h3>
        {reviews.length === 0 ? (
          <p className="no-reviews">Sharhlar yoq. Birinchi boling!</p>
        ) : (
          <div className="review-list">
            {reviews.map((r) => (
              <div key={r.id} className="review-item">
                <div className="review-stars">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <svg key={i} width="14" height="14" viewBox="0 0 24 24" fill={i < r.rating ? 'var(--warning)' : 'none'} stroke="var(--warning)" strokeWidth="2">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                  ))}
                </div>
                <p className="review-comment">{r.comment || 'Sharhsiz'}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {paymentSubmitted && (
        <div className="payment-success-banner glass">
          <div className="payment-success-icon">✅</div>
          <h3>Tolov yuborildi!</h3>
          <p>Admin tasdiqlashini kuting. Tez orada loyihani yuklab olishingiz mumkin boladi.</p>
        </div>
      )}

      {showPayment && merchantCard && (
        <div className="payment-modal-overlay" onClick={() => setShowPayment(false)}>
          <div className="payment-modal glass" onClick={(e) => e.stopPropagation()}>
            <h2>Karta tolovi</h2>
            <p className="payment-hint">Pulni quyidagi kartaga otkazing:</p>
            <div className="merchant-card-info">
              <div className="merchant-card-row">
                <span>Karta raqami:</span>
                <strong>{merchantCard.merchant_card_number}</strong>
              </div>
              <div className="merchant-card-row">
                <span>Egasi:</span>
                <strong>{merchantCard.merchant_card_holder}</strong>
              </div>
              {merchantCard.merchant_bank && (
                <div className="merchant-card-row">
                  <span>Bank:</span>
                  <strong>{merchantCard.merchant_bank}</strong>
                </div>
              )}
              {merchantCard.merchant_phone && (
                <div className="merchant-card-row">
                  <span>Telefon:</span>
                  <strong>{merchantCard.merchant_phone}</strong>
                </div>
              )}
            </div>

            <p className="payment-hint">Otkazishni tasdiqlash uchun karta raqamingizni kiriting:</p>
            <input
              className="input"
              placeholder="8600 1234 5678 9012"
              value={cardNumber}
              onChange={(e) => setCardNumber(e.target.value)}
              maxLength={19}
            />
            <input
              className="input"
              placeholder="KARTA EGASI F.I.O"
              value={cardHolder}
              onChange={(e) => setCardHolder(e.target.value)}
            />

            <p className="payment-hint">To'lov chekini (screenshot) yuklang:</p>
            <div className="screenshot-upload" onClick={() => fileRef.current?.click()}>
              {screenshotPreview ? (
                <img src={screenshotPreview} alt="Chek" className="screenshot-preview" />
              ) : (
                <div className="screenshot-placeholder">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
                    <circle cx="9" cy="9" r="2" />
                    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
                  </svg>
                  <span>Chek rasmini tanlang</span>
                </div>
              )}
            </div>
            <input ref={fileRef} type="file" accept="image/*" onChange={handleScreenshotSelect} hidden />

            <div className="payment-actions">
              <button
                className="btn btn-ghost btn-lg"
                onClick={handleCancelPayment}
              >
                Bekor qilish
              </button>
              <button
                className="btn btn-primary btn-lg"
                onClick={handleCardPay}
                disabled={paying || !cardNumber || !cardHolder}
              >
                {paying ? 'Yuborilmoqda...' : 'Tasdiqlash'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="detail-actions">
        <button className="btn btn-ghost fav-btn" onClick={toggleFavorite}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill={isFavorite ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
          </svg>
        </button>
        {purchased || isFree ? (
          <button className="btn btn-primary buy-btn" onClick={handleDownload}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Yuklab olish
          </button>
        ) : (
          <button className="btn btn-primary buy-btn" onClick={handleBuy}>
            {hasDiscount && <span className="buy-original">{formatUZS(project.price)}</span>}
            Sotib olish {formatUZS(price)}
          </button>
        )}
      </div>
    </div>
  )
}
