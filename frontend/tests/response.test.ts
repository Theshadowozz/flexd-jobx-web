import { describe, expect, it } from 'vitest'
import { z } from 'zod'
import { apiResponseSchema } from '../src/schemas/response'

describe('resource response contract', () => {
  it('accepts only singular data for details', () => {
    const schema = apiResponseSchema(z.object({ skill_alias: z.object({ id: z.string() }) }).strict())
    expect(schema.parse({ message: { success: 'Retrieved' }, error: {}, data: { skill_alias: { id: '12' } } }).data.skill_alias.id).toBe('12')
  })
  it('rejects numeric BIGINT IDs', () => {
    const schema = apiResponseSchema(z.object({ skill_alias: z.object({ id: z.string() }) }))
    expect(schema.safeParse({ message: {}, error: {}, data: { skill_alias: { id: 12 } } }).success).toBe(false)
  })
})
