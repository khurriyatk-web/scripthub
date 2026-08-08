export interface Project {
  id: string
  name: string
  short_description: string
  full_description?: string
  price: number
  discount_percent?: number
  discounted_price?: number
  rating_avg: number
  rating_count: number
  sales_count: number
  technologies: string
  tags?: string
  version?: string
  is_featured?: boolean
  status?: string
  created_at?: string
  developer_id?: string
  category_id?: string
  requirements?: string
  license?: string
  documentation?: string
  github_link?: string
  demo_video?: string
  demo_images?: string
  views?: number
}

export interface Review {
  id: string
  user_id: string
  project_id: string
  rating: number
  comment: string | null
  created_at: string
}

export interface AuthUser {
  id: string
  username?: string
  full_name?: string
  role: string
  balance: number
  is_verified_developer: boolean
  telegram_id?: number
  photo_url?: string
  first_name?: string
  last_name?: string
  language_code?: string
  email?: string
  bio?: string
  referral_code?: string
  created_at?: string
  is_premium?: boolean
}
