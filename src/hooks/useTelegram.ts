import { useCallback } from 'react'

export function useTelegram() {
  const tg = window.Telegram?.WebApp

  const ready = useCallback(() => {
    tg?.ready()
    tg?.expand()
    tg?.setHeaderColor('#060810')
    tg?.setBackgroundColor('#060810')
  }, [tg])

  const haptic = useCallback((style: 'light' | 'medium' | 'heavy' = 'light') => {
    tg?.HapticFeedback?.impactOccurred(style)
  }, [tg])

  const hapticNotify = useCallback((type: 'success' | 'warning' | 'error') => {
    tg?.HapticFeedback?.notificationOccurred(type)
  }, [tg])

  const getInitData = useCallback(() => {
    return tg?.initData ?? ''
  }, [tg])

  const getUser = useCallback((): {
    id: number
    first_name: string
    last_name?: string
    username?: string
    photo_url?: string
    language_code?: string
  } | null => {
    return tg?.initDataUnsafe?.user ?? null
  }, [tg])

  return {
    tg,
    ready,
    haptic,
    hapticNotify,
    getInitData,
    getUser,
  }
}
