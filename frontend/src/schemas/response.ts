import { z } from 'zod'

export const apiErrorSchema = z.record(z.string(), z.record(z.string(), z.string()))

export function apiResponseSchema<T extends z.ZodType>(data: T) {
  return z.object({
    message: z.record(z.string(), z.string()),
    error: apiErrorSchema,
    data,
  })
}
