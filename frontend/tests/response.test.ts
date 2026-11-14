import assert from 'node:assert/strict'
import test from 'node:test'
import { z } from 'zod'

import { apiResponseSchema } from '../src/schemas/response.ts'

test('accepts entity response without legacy object wrapper', () => {
  const schema = apiResponseSchema(z.object({ skills: z.array(z.object({ id: z.number() })) }))
  assert.deepEqual(schema.parse({ message: { success: 'OK' }, error: {}, data: { skills: [] } }).data,
    { skills: [] })
})

test('accepts categorized errors and empty data', () => {
  const schema = apiResponseSchema(z.object({}))
  const body = schema.parse({ message: { error: 'Invalid' },
    error: { validation: { name: 'Required' } }, data: {} })
  assert.equal(body.error.validation.name, 'Required')
})

test('rejects old flat error contract', () => {
  assert.equal(apiResponseSchema(z.object({})).safeParse({
    message: {}, error: { name: 'Required' }, data: {},
  }).success, false)
})
