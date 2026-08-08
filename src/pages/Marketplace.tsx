import { useEffect, useState, useCallback } from 'react'
import { api } from '../api/client'
import type { Project } from '../types'
import ProjectCard from '../components/ProjectCard'
import { useTelegram } from '../hooks/useTelegram'
import './Marketplace.css'

const SORTS = [
  { value: 'new', label: 'Yangi' },
  { value: 'popular', label: 'Mashhur' },
  { value: 'price_low', label: 'Arzon' },
  { value: 'price_high', label: 'Qimmat' },
  { value: 'rating', label: 'Reyting' },
]

const LANGUAGES = ['Python', 'JavaScript', 'TypeScript', 'FastAPI', 'React', 'Node.js', 'Go', 'Rust', 'PHP', 'Java']

export default function Marketplace() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [sort, setSort] = useState('new')
  const [search, setSearch] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [language, setLanguage] = useState('')
  const [priceMin, setPriceMin] = useState('')
  const [priceMax, setPriceMax] = useState('')
  const { haptic } = useTelegram()

  const loadProjects = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({ sort, limit: '50' })
      if (search) params.set('search', search)
      const data = await api.get<{ items: Project[] }>(`/projects?${params.toString()}`)
      let items = data.items || []

      if (language) {
        items = items.filter((p) =>
          p.technologies?.toLowerCase().includes(language.toLowerCase())
        )
      }
      if (priceMin) {
        items = items.filter((p) => p.price >= parseInt(priceMin) * 100)
      }
      if (priceMax) {
        items = items.filter((p) => p.price <= parseInt(priceMax) * 100)
      }

      setProjects(items)
    } catch {
      setProjects([])
    }
    setLoading(false)
  }, [sort, search, language, priceMin, priceMax])

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  const handleSort = (s: string) => {
    setSort(s)
    haptic('light')
  }

  const toggleFilters = () => {
    setShowFilters(!showFilters)
    haptic('light')
  }

  const clearFilters = () => {
    setLanguage('')
    setPriceMin('')
    setPriceMax('')
    setSearch('')
    haptic('light')
  }

  return (
    <div className="marketplace fade-in">
      <header className="market-header">
        <div className="market-header-row">
          <h1>Bozor</h1>
          <button
            className={`filter-toggle-btn ${showFilters ? 'active' : ''}`}
            onClick={toggleFilters}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
            </svg>
            Filtr
          </button>
        </div>
        <div className="search-bar">
          <svg className="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.3-4.3" />
          </svg>
          <input
            type="text"
            placeholder="Loyiha qidirish..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadProjects()}
            className="input search-input"
          />
        </div>
      </header>

      {showFilters && (
        <div className="filters-panel glass">
          <div className="filter-group">
            <label className="filter-label">Kod tili</label>
            <div className="filter-chips">
              <button
                className={`chip ${language === '' ? 'active' : ''}`}
                onClick={() => setLanguage('')}
              >Hammasi</button>
              {LANGUAGES.map((lang) => (
                <button
                  key={lang}
                  className={`chip ${language === lang ? 'active' : ''}`}
                  onClick={() => setLanguage(language === lang ? '' : lang)}
                >{lang}</button>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <label className="filter-label">Narx (so'm)</label>
            <div className="price-range">
              <input
                type="number"
                className="input"
                placeholder="Min"
                value={priceMin}
                onChange={(e) => setPriceMin(e.target.value)}
              />
              <span className="price-separator">—</span>
              <input
                type="number"
                className="input"
                placeholder="Max"
                value={priceMax}
                onChange={(e) => setPriceMax(e.target.value)}
              />
            </div>
          </div>

          <button className="btn btn-ghost btn-sm" onClick={clearFilters}>
            Filtrlarni tozalash
          </button>
        </div>
      )}

      <div className="sort-tabs">
        {SORTS.map((s) => (
          <button
            key={s.value}
            className={`sort-tab ${sort === s.value ? 'active' : ''}`}
            onClick={() => handleSort(s.value)}
          >
            {s.label}
          </button>
        ))}
      </div>

      <div className="project-list">
        {loading && projects.length === 0
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 100, borderRadius: 14 }} />
            ))
          : projects.map((p) => <ProjectCard key={p.id} project={p} />)}
      </div>

      {!loading && projects.length === 0 && (
        <div className="empty-state">
          <span className="empty-icon">📦</span>
          <p>Loyihalar topilmadi</p>
        </div>
      )}
    </div>
  )
}
