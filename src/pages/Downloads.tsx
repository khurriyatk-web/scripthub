import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Project } from '../types'
import ProjectCard from '../components/ProjectCard'
import { useAuth } from '../context/AuthContext'
import './Downloads.css'

export default function Downloads() {
  const { user } = useAuth()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      setLoading(false)
      return
    }
    api
      .get<{ items: { project_id: string }[] }>('/users/downloads')
      .then(async ({ items }) => {
        if (!items || items.length === 0) {
          setProjects([])
          setLoading(false)
          return
        }
        const projects: Project[] = []
        for (const d of items) {
          try {
            const p = await api.get<Project>(`/projects/${d.project_id}`)
            projects.push(p)
          } catch { /* skip deleted */ }
        }
        setProjects(projects)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [user])

  return (
    <div className="downloads fade-in">
      <h1 className="page-title">Yuklamalar</h1>
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
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          </div>
          <p>Yuklamalar yo'q</p>
          <span className="empty-subtitle">Sotib olingan loyihalar shu yerda ko'rinadi</span>
        </div>
      ) : (
        <div className="project-list">
          {projects.map((p) => <ProjectCard key={p.id} project={p} />)}
        </div>
      )}
    </div>
  )
}
