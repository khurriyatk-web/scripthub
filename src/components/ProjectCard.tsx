import { Link } from 'react-router-dom'
import type { Project } from '../types'
import { useTelegram } from '../hooks/useTelegram'
import { formatUZS } from '../utils/format'
import './ProjectCard.css'

const GRADIENTS = [
  'linear-gradient(135deg, #0ea5e9 0%, #22d3ee 100%)',
  'linear-gradient(135deg, #6366f1 0%, #818cf8 100%)',
  'linear-gradient(135deg, #f43f5e 0%, #fb7185 100%)',
  'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
  'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
  'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
]

function getGradient(id: string): string {
  let hash = 0
  for (let i = 0; i < id.length; i++) {
    hash = id.charCodeAt(i) + ((hash << 5) - hash)
  }
  return GRADIENTS[Math.abs(hash) % GRADIENTS.length]
}

export default function ProjectCard({ project }: { project: Project }) {
  const { haptic } = useTelegram()

  const price = project.discount_percent && project.discount_percent > 0
    ? Math.round(project.price * (1 - project.discount_percent / 100))
    : project.price
  const isFree = price === 0
  const hasDiscount = project.discount_percent && project.discount_percent > 0
  const gradient = getGradient(project.id)
  const initial = project.name[0]?.toUpperCase() || '?'

  return (
    <Link
      to={`/project/${project.id}`}
      className="project-card glass"
      onClick={() => haptic('light')}
    >
      <div className="card-thumb" style={{ background: gradient }}>
        <span className="card-thumb-letter">{initial}</span>
        <div className="card-thumb-overlay" />
        {project.is_featured && <span className="badge-featured">Tavsiya</span>}
        {hasDiscount && <span className="badge-discount">-{project.discount_percent}%</span>}
      </div>

      <div className="card-body">
        <h3 className="card-title">{project.name}</h3>
        <p className="card-desc line-clamp-2">{project.short_description}</p>

        <div className="card-tags">
          {project.technologies.split(',').slice(0, 3).map((tech) => (
            <span key={tech.trim()} className="tag">{tech.trim()}</span>
          ))}
        </div>

        <div className="card-footer">
          <div className="card-price">
            {isFree ? (
              <span className="price-free">BEPUL</span>
            ) : (
              <>
                {hasDiscount && (
                  <span className="price-original">{formatUZS(project.price)}</span>
                )}
                <span className="price-current">{formatUZS(price)}</span>
              </>
            )}
          </div>
          <div className="card-stats">
            <span className="stat">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
              {project.rating_avg.toFixed(1)}
            </span>
            <span className="stat">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              {project.sales_count}
            </span>
          </div>
        </div>
      </div>
    </Link>
  )
}
