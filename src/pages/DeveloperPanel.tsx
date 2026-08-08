import { useEffect, useState, useRef } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useTelegram } from '../hooks/useTelegram'
import { formatUZS } from '../utils/format'
import './DeveloperPanel.css'

const TECH_PRESETS = [
  'Python', 'FastAPI', 'Flask', 'Django', 'Aiogram', 'Pyrogram', 'Telethon', 'PyQt', 'Tkinter', 'Kivy',
  'Selenium', 'BeautifulSoup', 'Scrapy', 'Pandas', 'NumPy', 'Matplotlib', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'OpenCV',
  'Asyncio', 'Aiohttp', 'Requests', 'SQLAlchemy', 'Alembic', 'Celery', 'Redis', 'Pydantic', 'Uvicorn', 'Gunicorn',
  'JavaScript', 'TypeScript', 'React', 'Next.js', 'Vue', 'Nuxt', 'Angular', 'Svelte', 'Solid.js', 'Qwik',
  'Node.js', 'Express', 'NestJS', 'Fastify', 'Koa', 'Hapi', 'Socket.io', 'GraphQL', 'Apollo', 'tRPC',
  'Vite', 'Webpack', 'Rollup', 'Esbuild', 'Turbo-pak', 'Tailwind', 'Sass', 'SCSS', 'CSS3', 'HTML5',
  'Bootstrap', 'Material UI', 'Chakra UI', 'Radix UI', 'Shadcn', 'Framer Motion', 'Three.js', 'GSAP', 'Lottie', 'Canvas',
  'Electron', 'Tauri', 'React Native', 'Expo', 'Flutter', 'Dart', 'Kotlin', 'Jetpack Compose', 'Swift', 'SwiftUI',
  'Objective-C', 'C', 'C++', 'C#', '.NET', 'ASP.NET', 'Blazor', 'Unity', 'Unreal Engine', 'Godot',
  'Go', 'Gin', 'Echo', 'Fiber', 'Rust', 'Actix', 'Tokio', 'Rocket', 'Axum', 'Cargo',
  'Java', 'Spring Boot', 'Maven', 'Gradle', 'Ktor', 'Quarkus', 'Micronaut', 'JPA', 'Hibernate', 'Lombok',
  'PHP', 'Laravel', 'Symfony', 'CodeIgniter', 'Yii', 'CakePHP', 'Slim', 'Composer', 'WordPress', 'Drupal',
  'Ruby', 'Rails', 'Sinatra', 'Grape', 'Elixir', 'Phoenix', 'LiveView', 'OTP', 'Haskell', 'Yesod',
  'Scala', 'Play', 'Akka', 'Cats', 'Clojure', 'Ring', 'Reagent', 'Perl', 'Dancer', 'Mojolicious',
  'Lua', 'LÖVE', 'Luarocks', 'Shell', 'Bash', 'Zsh', 'PowerShell', 'Batch', 'Awk', 'Sed',
  'SQL', 'PostgreSQL', 'MySQL', 'SQLite', 'MongoDB', 'Redis', 'Cassandra', 'DynamoDB', 'CouchDB', 'InfluxDB',
  'Elasticsearch', 'ClickHouse', 'Supabase', 'Firebase', 'Prisma', 'Drizzle', 'TypeORM', 'Sequelize', 'Mongoose', 'Knex',
  'Docker', 'Kubernetes', 'Docker Compose', 'Helm', 'Terraform', 'Ansible', 'Vagrant', 'Packer', 'Nomad', 'Consul',
  'AWS', 'Google Cloud', 'Azure', 'DigitalOcean', 'Vercel', 'Netlify', 'Cloudflare', 'Heroku', 'Railway', 'Fly.io',
  'Nginx', 'Caddy', 'Apache', 'Traefik', 'HAProxy', 'Linux', 'Ubuntu', 'Debian', 'CentOS', 'Alpine',
  'Git', 'GitHub Actions', 'GitLab CI', 'Jenkins', 'CircleCI', 'Travis CI', 'Drone', 'ArgoCD', 'Spinnaker', 'Tekton',
  'GraphQL', 'REST API', 'gRPC', 'WebSockets', 'SSE', 'WebRTC', 'WebTransport', 'MQTT', 'RabbitMQ', 'Kafka',
  'Stripe', 'PayPal', 'Click', 'Payme', 'Uzum', 'Yandex.Money', 'QIWI', 'Crypto', 'Web3', 'Solidity',
  'Hardhat', 'Truffle', 'Wagmi', 'Viem', 'Ethers.js', 'IPFS', 'Pinata', 'Moralis', 'The Graph', 'Chainlink',
  'OpenAI', 'LangChain', 'LlamaIndex', 'Pinecone', 'Weaviate', 'Qdrant', 'Chroma', 'Ollama', 'vLLM', 'HuggingFace',
  'Puppeteer', 'Playwright', 'Cypress', 'Selenium', 'Jest', 'Vitest', 'Pytest', 'Unittest', 'Mocha', 'Chai',
  'Storybook', 'ESLint', 'Prettier', 'Biome', 'Ruff', 'Black', 'Mypy', 'SonarQube', 'Codecov', 'Sentry',
  'Figma', 'Sketch', 'Adobe XD', 'Framer', 'Canva', 'Photoshop', 'Illustrator', 'After Effects', 'Premiere', 'Blender',
  'Arduino', 'Raspberry Pi', 'ESP32', 'ESP8266', 'MicroPython', 'PlatformIO', 'ROS', 'OpenCV', 'Tesseract', 'YOLO',
  'Tornado', 'Sanic', 'Starlette', 'Pyrogram v2', 'Telebot', 'Bot.js', 'Telegraf.js', 'grammY', 'Telegraf', 'TeleBot',
]

interface DashboardData {
  totals: {
    projects: number
    published: number
    pending: number
    draft: number
    sales: number
    revenue: number
    views: number
    avg_rating: number
  }
  daily_revenue: { date: string; revenue: number; sales: number }[]
  top_projects: {
    id: string; name: string; price: number; sales_count: number
    rating_avg: number; status: string; revenue: number
  }[]
  recent_orders: {
    id: string; project_name: string; amount: number
    status: string; created_at: string
  }[]
}

interface DevProject {
  id: string
  name: string
  short_description: string
  price: number
  discounted_price: number
  discount_percent: number
  status: string
  sales_count: number
  rating_avg: number
  rating_count: number
  views: number
  revenue: number
  created_at: string
}

export default function DeveloperPanel() {
  const { user } = useAuth()
  const { haptic, hapticNotify } = useTelegram()
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [projects, setProjects] = useState<DevProject[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    name: '', short_description: '', full_description: '', technologies: '', price: '',
  })
  const [projectFile, setProjectFile] = useState<File | null>(null)
  const [thumbnailFile, setThumbnailFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const thumbInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (user) loadData()
  }, [user])

  const loadData = async () => {
    setLoading(true)
    try {
      const [dash, projs] = await Promise.all([
        api.get<DashboardData>('/developer/dashboard'),
        api.get<{ items: DevProject[] }>('/developer/projects'),
      ])
      setDashboard(dash)
      setProjects(projs.items || [])
    } catch {
      setDashboard(null)
      setProjects([])
    }
    setLoading(false)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!['zip', 'rar', '7z', 'tar', 'gz', 'py', 'js', 'ts'].includes(ext || '')) {
      alert('ZIP, RAR, 7Z, TAR, GZ, PY, JS, TS formatdagi fayllar qabul qilinadi')
      return
    }
    setProjectFile(file)
    haptic('light')
  }

  const handleThumbSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setThumbnailFile(file)
    haptic('light')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!projectFile || !user) {
      alert('Iltimos, loyiha faylini (ZIP/RAR) yuklang')
      return
    }
    haptic('medium')
    setUploading(true)
    try {
      const fileFormData = new FormData()
      fileFormData.append('file', projectFile)
      const fileRes = await api.upload<{ path: string; filename: string; size: number; sha256: string }>('/upload/project-file', fileFormData)

      let thumbnailPath: string | null = null
      if (thumbnailFile) {
        const thumbFormData = new FormData()
        thumbFormData.append('file', thumbnailFile)
        const thumbRes = await api.upload<{ path: string }>('/upload/image', thumbFormData)
        thumbnailPath = thumbRes.path
      }

      await api.post('/projects', {
        name: form.name,
        short_description: form.short_description,
        full_description: form.full_description,
        technologies: form.technologies,
        price: Math.round(parseFloat(form.price || '0') * 100),
        github_link: fileRes.path,
        demo_video: thumbnailPath,
      })

      hapticNotify('success')
      setForm({ name: '', short_description: '', full_description: '', technologies: '', price: '' })
      setProjectFile(null)
      setThumbnailFile(null)
      setShowForm(false)
      await loadData()
    } catch (e) {
      hapticNotify('error')
      alert((e as Error).message)
    } finally {
      setUploading(false)
    }
  }

  if (user && user.role !== 'developer' && user.role !== 'admin' && user.role !== 'moderator') {
    return (
      <div className="developer fade-in">
        <div className="empty-state glass" style={{ borderRadius: 14, padding: 48 }}>
          <div className="empty-icon-wrap">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </div>
          <p>Dasturchi huquqi kerak</p>
          <span className="empty-subtitle">Dasturchi bo'lish uchun admin bilan bog'laning</span>
        </div>
      </div>
    )
  }

  const t = dashboard?.totals
  const maxRevenue = dashboard?.daily_revenue?.length
    ? Math.max(...dashboard.daily_revenue.map((d) => d.revenue), 1)
    : 1

  return (
    <div className="developer fade-in">
      <div className="dev-header">
        <h1 className="page-title">Sotuv dashbordi</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Bekor' : '+ Mahsulot'}
        </button>
      </div>

      {/* Real-time stats */}
      <div className="dev-stats">
        <div className="dev-stat-card glass">
          <span className="dev-stat-value">{t?.projects ?? 0}</span>
          <span className="dev-stat-label">Loyihalar</span>
        </div>
        <div className="dev-stat-card glass">
          <span className="dev-stat-value">{t?.sales ?? 0}</span>
          <span className="dev-stat-label">Sotuvlar</span>
        </div>
        <div className="dev-stat-card glass">
          <span className="dev-stat-value">{formatUZS(t?.revenue ?? 0)}</span>
          <span className="dev-stat-label">Daromad</span>
        </div>
        <div className="dev-stat-card glass">
          <span className="dev-stat-value">{t?.views ?? 0}</span>
          <span className="dev-stat-label">Ko'rishlar</span>
        </div>
      </div>

      {/* Revenue chart (last 7 days) */}
      {dashboard && dashboard.daily_revenue.length > 0 && (
        <div className="dev-chart glass">
          <h3 className="dev-section-title">So'nggi 7 kun daromadi</h3>
          <div className="chart-bars">
            {dashboard.daily_revenue.map((d, i) => (
              <div key={i} className="chart-bar-col">
                <div
                  className="chart-bar"
                  style={{ height: `${(d.revenue / maxRevenue) * 100}%` }}
                  title={`${d.date}: ${formatUZS(d.revenue)}`}
                />
                <span className="chart-bar-label">{d.date.slice(5)}</span>
                <span className="chart-bar-value">{d.sales} ta</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top projects */}
      {dashboard && dashboard.top_projects.length > 0 && (
        <div className="dev-section glass">
          <h3 className="dev-section-title">Top loyihalar</h3>
          <div className="dev-top-list">
            {dashboard.top_projects.map((p, i) => (
              <div key={p.id} className="dev-top-item">
                <span className="dev-top-rank">#{i + 1}</span>
                <div className="dev-top-info">
                  <span className="dev-top-name">{p.name}</span>
                  <span className="dev-top-meta">{p.sales_count} sotuv · ⭐ {p.rating_avg}</span>
                </div>
                <span className="dev-top-revenue">{formatUZS(p.revenue)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent orders */}
      {dashboard && dashboard.recent_orders.length > 0 && (
        <div className="dev-section glass">
          <h3 className="dev-section-title">So'nggi buyurtmalar</h3>
          <div className="dev-orders-list">
            {dashboard.recent_orders.map((o) => (
              <div key={o.id} className="dev-order-item">
                <div className="dev-order-info">
                  <span className="dev-order-name">{o.project_name}</span>
                  <span className="dev-order-date">
                    {o.created_at ? new Date(o.created_at).toLocaleDateString('ru-RU') : ''}
                  </span>
                </div>
                <div className="dev-order-right">
                  <span className={`dev-order-status status-${o.status}`}>{o.status}</span>
                  <span className="dev-order-amount">{formatUZS(o.amount)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add product form */}
      {showForm && (
        <form className="dev-form glass" onSubmit={handleSubmit}>
          <h3>Yangi mahsulot</h3>
          <label className="form-label">Loyiha nomi</label>
          <input className="input" placeholder="Mening ajoyib botim" value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <label className="form-label">Qisqa tavsif</label>
          <input className="input" placeholder="Qisqa bir qatorli tavsif" value={form.short_description}
            onChange={(e) => setForm({ ...form, short_description: e.target.value })} required />
          <label className="form-label">To'liq tavsif</label>
          <textarea className="input" placeholder="Loyiha nima qilishini batafsil yozing..."
            value={form.full_description} onChange={(e) => setForm({ ...form, full_description: e.target.value })} rows={4} required />
          <label className="form-label">Narx (so'mda, 0 — bepul)</label>
          <input className="input" type="number" step="1000" placeholder="50000" value={form.price}
            onChange={(e) => setForm({ ...form, price: e.target.value })} />
          <label className="form-label">Texnologiyalar (vergul bilan)</label>
          <input className="input" placeholder="Python, FastAPI, PostgreSQL" value={form.technologies}
            onChange={(e) => setForm({ ...form, technologies: e.target.value })} />

          <label className="form-label">Mahsulot rasmi</label>
          <div className="upload-area" onClick={() => thumbInputRef.current?.click()}>
            {thumbnailFile ? (
              <div className="upload-preview">
                <img src={URL.createObjectURL(thumbnailFile)} alt="Thumbnail" className="upload-thumb-img" />
                <span className="upload-filename">{thumbnailFile.name}</span>
              </div>
            ) : (
              <div className="upload-placeholder">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
                  <circle cx="9" cy="9" r="2" />
                  <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
                </svg>
                <span>Rasm tanlash</span>
                <span className="upload-hint">PNG, JPG, WEBP</span>
              </div>
            )}
          </div>
          <input ref={thumbInputRef} type="file" accept=".png,.jpg,.jpeg,.webp" onChange={handleThumbSelect} hidden />

          <label className="form-label">Mahsulot fayli (ZIP, RAR, 7Z)</label>
          <div className="upload-area upload-area-file" onClick={() => fileInputRef.current?.click()}>
            {projectFile ? (
              <div className="upload-preview">
                <div className="file-icon-wrap">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                </div>
                <div className="file-info">
                  <span className="upload-filename">{projectFile.name}</span>
                  <span className="upload-hint">{(projectFile.size / 1024 / 1024).toFixed(2)} MB · {projectFile.name.split('.').pop()?.toUpperCase()}</span>
                </div>
              </div>
            ) : (
              <div className="upload-placeholder">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
                <span>Fayl yuklash</span>
                <span className="upload-hint">ZIP, RAR, 7Z, TAR, GZ</span>
              </div>
            )}
          </div>
          <input ref={fileInputRef} type="file" accept=".zip,.rar,.7z,.tar,.gz,.py,.js,.ts" onChange={handleFileSelect} hidden />

          <button type="submit" className="btn btn-primary btn-lg" disabled={uploading}>
            {uploading ? 'Yuklanmoqda...' : 'Mahsulot yaratish'}
          </button>
        </form>
      )}

      {/* Project list */}
      <div className="dev-project-list">
        <h3 className="dev-section-title">Mening loyihalarim</h3>
        {loading ? (
          <div className="skeleton" style={{ height: 80, borderRadius: 12 }} />
        ) : projects.length === 0 ? (
          <div className="empty-state glass" style={{ borderRadius: 14, padding: 40 }}>
            <p>Loyihalar yo'q</p>
            <span className="empty-subtitle">Birinchi mahsulotingizni qo'shing</span>
          </div>
        ) : (
          projects.map((p) => (
            <div key={p.id} className="dev-project glass">
              <div className="dev-project-info">
                <h3 className="dev-project-name">{p.name}</h3>
                <div className="dev-project-meta">
                  <span className="dev-project-price">{p.price === 0 ? 'BEPUL' : formatUZS(p.price)}</span>
                  <span className="dev-project-sales">{p.sales_count} sotuv</span>
                  <span className="dev-project-views">{p.views} ko'rish</span>
                  <span className={`dev-project-status status-${p.status}`}>{p.status}</span>
                </div>
              </div>
              <div className="dev-project-revenue">
                <span className="dev-project-revenue-value">{formatUZS(p.revenue)}</span>
                <span className="dev-project-revenue-label">daromad</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
