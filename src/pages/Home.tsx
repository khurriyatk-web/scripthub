import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Project } from '../types'
import ProjectCard from '../components/ProjectCard'
import './Home.css'

const HERO_IMG = 'https://i.ibb.co/GfZwbfYn/photo-9-2026-08-05-22-37-08.jpg'
const LOGO_URL = 'https://i.ibb.co/NdfSqDbt/Chat-GPT-Image-8-2026-11-35-54.png'

export default function Home() {
  const [trending, setTrending] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get<{ items: Project[] }>('/projects?sort=popular&limit=4')
      .then((data) => {
        setTrending(data.items || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  return (
    <div className="home fade-in">
      <section className="hero">
        <div className="hero-bg" style={{ backgroundImage: `url(${HERO_IMG})` }} />
        <div className="hero-overlay" />
        <div className="hero-glow" />
        <div className="hero-content">
          <div className="hero-logo-wrap">
            <img src={LOGO_URL} alt="ScriptHub" className="hero-logo" />
          </div>
          <div className="hero-badge">
            <span className="hero-badge-dot" />
            10,000+ dasturchilar ishonadi
          </div>
          <h1 className="hero-title">
            <span className="text-gradient">Manba kod</span> xavfsiz sotuvda
          </h1>
          <p className="hero-subtitle">
            Premium shablonlar, botlar va to'liq ilovalar tasdiqlangan dasturchilardan.
          </p>
          <div className="hero-actions">
            <Link to="/marketplace" className="btn btn-primary btn-lg">
              Bozorni ko'rish
            </Link>
            <Link to="/developer" className="btn btn-ghost btn-lg">
              Sotishni boshlash
            </Link>
          </div>
        </div>
        <div className="hero-orb hero-orb-1" />
        <div className="hero-orb hero-orb-2" />
      </section>

      <section className="stats-strip">
        <div className="stat-item">
          <span className="stat-value">2,400+</span>
          <span className="stat-label">Mahsulot</span>
        </div>
        <div className="stat-divider" />
        <div className="stat-item">
          <span className="stat-value">10K+</span>
          <span className="stat-label">Dasturchi</span>
        </div>
        <div className="stat-divider" />
        <div className="stat-item">
          <span className="stat-value">98%</span>
          <span className="stat-label">Mamnunlik</span>
        </div>
      </section>

      <section className="features">
        <Link to="/marketplace" className="feature-card glass">
          <div className="feature-icon-wrap feature-icon-blue">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z" />
              <path d="M3 6h18" />
              <path d="M16 10a4 4 0 0 1-8 0" />
            </svg>
          </div>
          <div className="feature-body">
            <span className="feature-title">Bozor</span>
            <span className="feature-desc">Kod sotib olish</span>
          </div>
        </Link>

        <Link to="/developer" className="feature-card glass">
          <div className="feature-icon-wrap feature-icon-cyan">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m16 18 6-6-6-6" />
              <path d="m8 6-6 6 6 6" />
            </svg>
          </div>
          <div className="feature-body">
            <span className="feature-title">Kod sotish</span>
            <span className="feature-desc">Loyihalaringizni joylang</span>
          </div>
        </Link>

        <Link to="/favorites" className="feature-card glass">
          <div className="feature-icon-wrap feature-icon-rose">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
            </svg>
          </div>
          <div className="feature-body">
            <span className="feature-title">Sevimlilar</span>
            <span className="feature-desc">Keyinroq uchun saqlash</span>
          </div>
        </Link>

        <Link to="/support" className="feature-card glass">
          <div className="feature-icon-wrap feature-icon-amber">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z" />
            </svg>
          </div>
          <div className="feature-body">
            <span className="feature-title">Yordam</span>
            <span className="feature-desc">Har doim yordam</span>
          </div>
        </Link>
      </section>

      <section className="home-trending">
        <div className="section-header">
          <h2>Mashhurlar</h2>
          <Link to="/marketplace" className="see-all">Barchasi →</Link>
        </div>
        <div className="project-grid">
          {loading
            ? Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 160, borderRadius: 14 }} />
              ))
            : trending.length > 0
              ? trending.map((p) => <ProjectCard key={p.id} project={p} />)
              : <p className="empty-inline">Hozircha loyihalar yo'q</p>}
        </div>
      </section>
    </div>
  )
}
