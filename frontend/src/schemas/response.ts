import { z } from 'zod'

export const paginationSchema = z.object({
  total: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
  offset: z.number().int().nonnegative(),
})

export const responseSchema = z.object({
  message: z.record(z.string(), z.string()),
  error: z.record(z.string(), z.string()),
  data: z.record(z.string(), z.unknown()),
})

export function apiResponseSchema<T extends z.ZodType>(data: T) {
  return responseSchema.extend({ data })
}
