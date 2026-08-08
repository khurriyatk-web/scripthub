function formatUZS(price: number): string {
  // price is in tiyin (1 so'm = 100 tiyin)
  if (price === 0) return 'BEPUL'
  const som = Math.round(price / 100)
  return som.toLocaleString('ru-RU') + " so'm"
}

export { formatUZS }
