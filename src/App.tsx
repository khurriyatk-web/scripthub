import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useTelegram } from './hooks/useTelegram'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import Marketplace from './pages/Marketplace'
import ProjectDetail from './pages/ProjectDetail'
import Profile from './pages/Profile'
import Downloads from './pages/Downloads'
import Favorites from './pages/Favorites'
import Cart from './pages/Cart'
import DeveloperPanel from './pages/DeveloperPanel'
import Support from './pages/Support'
import Login from './pages/Login'

export default function App() {
  const { ready } = useTelegram()

  useEffect(() => {
    ready()
  }, [ready])

  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/project/:id" element={<ProjectDetail />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/downloads" element={<Downloads />} />
          <Route path="/favorites" element={<Favorites />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/developer" element={<DeveloperPanel />} />
          <Route path="/support" element={<Support />} />
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </AuthProvider>
  )
}
