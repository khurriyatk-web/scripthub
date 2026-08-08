import { type ReactNode } from 'react'
import BottomNav from './BottomNav'
import { useTelegram } from '../hooks/useTelegram'

export default function Layout({ children }: { children: ReactNode }) {
  const { tg } = useTelegram()
  const viewportHeight = tg?.viewportStableHeight || 0

  return (
    <div
      className="app-container"
      style={viewportHeight ? { minHeight: `${viewportHeight}px` } : undefined}
    >
      <main className="app-main">{children}</main>
      <BottomNav />
    </div>
  )
}
