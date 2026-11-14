import { Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/layout/app-shell'
import Home from '@/pages/home'
import NotFound from '@/pages/not-found'

export default function App() {
  return <AppShell><Routes><Route path="/" element={<Home />} /><Route path="*" element={<NotFound />} /></Routes></AppShell>
}
