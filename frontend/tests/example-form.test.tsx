import { configureStore } from '@reduxjs/toolkit'
import { Provider } from 'react-redux'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, it } from 'vitest'
import { ExampleForm } from '../src/components/examples/example-form'
import appReducer from '../src/redux/slices/app-slice'

it('validates input and saves valid workspace name to Redux', async () => {
  const store = configureStore({ reducer: { app: appReducer } })
  const user = userEvent.setup()
  render(<Provider store={store}><ExampleForm /></Provider>)
  const input = screen.getByLabelText('Nama workspace')
  await user.clear(input)
  await user.click(screen.getByRole('button', { name: 'Simpan nama' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Gunakan minimal 2 karakter.')
  await user.type(input, 'Tim JobX')
  await user.click(screen.getByRole('button', { name: 'Simpan nama' }))
  expect(store.getState().app.workspaceName).toBe('Tim JobX')
})
