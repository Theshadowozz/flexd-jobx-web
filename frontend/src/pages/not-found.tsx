import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export default function NotFound() {
  return <section className="space-y-5"><p className="font-mono text-sm text-primary">404</p><h1 className="text-4xl font-semibold">Halaman tidak ditemukan</h1><p className="text-muted-foreground">Periksa alamat atau kembali ke workspace.</p><Button asChild><Link to="/">Kembali ke workspace</Link></Button></section>
}
