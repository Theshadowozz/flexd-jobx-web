import { z } from 'zod'

export const envSchema = z.object({
  APP_PUBLIC_NAME: z.string().default('JobX'),
  APP_PUBLIC_API_BASE_URL: z.url().default('http://localhost:8000/api/v1'),
})
