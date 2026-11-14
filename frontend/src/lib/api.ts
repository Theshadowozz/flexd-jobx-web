import { apiResponseSchema } from '../schemas/response.ts'
import { z } from 'zod'

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly categories: Record<string, Record<string, string>>,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function apiRequest<T extends z.ZodType>(
  path: string,
  dataSchema: T,
  options: RequestInit = {},
): Promise<z.infer<T>> {
  const baseUrl = (import.meta.env?.VITE_APP_API_BASE_URL ?? '/api/v1').replace(/\/+$/, '')
  const response = await fetch(`${baseUrl}/${path.replace(/^\/+/, '')}`, {
    ...options,
    signal: options.signal ?? AbortSignal.timeout(10000),
  })
  if (!response.ok) {
    const body = apiResponseSchema(z.object({})).safeParse(await response.json())
    throw new ApiError(response.status, body.success ? body.data.error : {},
      body.success ? body.data.message.error ?? 'Request gagal' : 'Respons server tidak valid')
  }
  const body = apiResponseSchema(z.unknown()).parse(await response.json())
  return dataSchema.parse(body.data)
}
