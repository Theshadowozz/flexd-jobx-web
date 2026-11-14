import type { z } from 'zod'
import type { paginationSchema, responseSchema } from '@/schemas/response'

export type Pagination = z.infer<typeof paginationSchema>
export type ApiEnvelope = z.infer<typeof responseSchema>
export type ApiResponse<T> = Omit<ApiEnvelope, 'data'> & { data: T }
export type EntityId = string
