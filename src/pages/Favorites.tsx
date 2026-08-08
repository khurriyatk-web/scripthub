import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Project } from '../types'
import ProjectCard from '../components/ProjectCard'
import { useAuth } from '../context/AuthContext'
import './Favorites.css'

export default function Favorites() {
  const { user } = useAuth()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      setLoading(false)
      return
    }
    api
      .get<{ items: { project_id: string }[] }>('/users/favorites')
      .then(async ({ items }) => {
        if (!items || items.length === 0) {
          setProjects([])
          setLoading(false)
          return
        }
        const projects: Project[] = []
        for (const f of items) {
          try {
            const p = await api.get<Project>(`/projects/${f.project_id}`)
            projects.push(p)
          } catch { /* skip deleted */ }
        }
        setProjects(projects)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [user])

  return (
    <div className="favorites fade-in">
      <h1 className="page-title">Sevimlilar</h1>
      {loading ? (
        <div className="project-list">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 100, borderRadius: 14 }} />
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="empty-state glass" style={{ borderRadius: 14, padding: 48 }}>
          <div className="empty-icon-wrap">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
            </svg>
          </div>
          <p>Sevimlilar yo'q</p>
          <span className="empty-subtitle">Loyihadagi yurak belgisini bosing</span>
        </div>
      ) : (
        <div className="project-list">
          {projects.map((p) => <ProjectCard key={p.id} project={p} />)}
        </div>
      )}
    </div>
  )
}
