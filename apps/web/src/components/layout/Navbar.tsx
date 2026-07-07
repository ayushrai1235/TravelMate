'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { useEffect, useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import type { User } from '@supabase/supabase-js'
import { LogOut, MapPinned } from 'lucide-react'

export function Navbar() {
  const [user, setUser] = useState<User | null>(null)
  const supabase = useMemo(() => createClient(), [])
  const router = useRouter()

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setUser(session?.user ?? null)
      }
    )

    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user)
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [supabase.auth])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
    router.push('/')
    router.refresh()
  }

  return (
    <nav className="border-b border-slate-200 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
      <div className="container mx-auto flex min-h-16 items-center gap-4 px-4 py-3">
        <div className="flex min-w-0 items-center gap-4">
          <Link href="/" className="flex items-center gap-2 text-lg font-bold text-slate-950 dark:text-white">
            <MapPinned className="size-5 text-emerald-600" aria-hidden="true" />
            TravelMate AI
          </Link>
          <Link href="/planner" className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-950 dark:text-slate-300 dark:hover:text-white">
            Planner
          </Link>
          <Link href="/stations" className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-950 dark:text-slate-300 dark:hover:text-white">
            Station Codes
          </Link>
        </div>
        <div className="ml-auto flex min-w-0 items-center gap-3">
          {user ? (
            <div className="flex min-w-0 items-center gap-3">
              <span className="hidden truncate text-sm text-slate-500 sm:block">{user.email}</span>
              <Button variant="outline" onClick={handleSignOut} aria-label="Sign out">
                <LogOut className="size-4" aria-hidden="true" />
                <span className="hidden sm:inline">Sign Out</span>
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/sign-in">
                <Button variant="ghost">Log In</Button>
              </Link>
              <Link href="/sign-up">
                <Button>Sign Up</Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
