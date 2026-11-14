import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import mark from '@/assets/brand-mark.svg'

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-background">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-5">
          <Link to="/" className="flex items-center gap-3 rounded-md focus-visible:outline-2 focus-visible:outline-primary" aria-label="JobX beranda">
            <img src={mark} alt="" className="size-10" /><span className="text-xl font-bold tracking-tight">JobX<span className="font-normal text-muted-foreground"> / flexd</span></span>
          </Link>
          <span className="rounded-full border border-border px-3 py-1 font-mono text-xs text-muted-foreground">Development scaffold</span>
        </div>
      </header>
      <main id="main-content" className="mx-auto max-w-6xl px-6 py-12 md:py-20">{children}</main>
      <footer className="mx-auto max-w-6xl border-t border-border px-6 py-6 text-xs text-muted-foreground">JobX · Portfolio, skill, dan peluang kerja.</footer>
    </div>
  )
}
