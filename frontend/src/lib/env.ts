import { envSchema } from '@/schemas/env'

export const env = envSchema.parse(import.meta.env)
