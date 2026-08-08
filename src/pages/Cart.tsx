import { Link } from 'react-router-dom'
import './Cart.css'

export default function Cart() {
  return (
    <div className="cart fade-in">
      <h1 className="page-title">Savat</h1>
      <div className="empty-state glass" style={{ borderRadius: 14, padding: 48 }}>
        <div className="empty-icon-wrap">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="8" cy="21" r="1" />
            <circle cx="19" cy="21" r="1" />
            <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
          </svg>
        </div>
        <p>Savat bo'sh</p>
        <span className="empty-subtitle">Bozordan kod toping</span>
        <Link to="/marketplace" className="btn btn-primary btn-lg" style={{ marginTop: 20 }}>
          Bozorni ko'rish
        </Link>
      </div>
    </div>
  )
}
