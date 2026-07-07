'use client'

import { FormEvent, useMemo, useState } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Globe2, Loader2, Mail, UserPlus } from 'lucide-react'

type AuthFormProps = {
  mode: 'login' | 'signup'
}

export function AuthForm({ mode }: AuthFormProps) {
  const supabase = useMemo(() => createClient(), [])
  const router = useRouter()
  const searchParams = useSearchParams()
  const next = searchParams.get('next') ?? '/planner'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const isSignup = mode === 'signup'

  async function handlePasswordSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsLoading(true)
    setError(null)
    setMessage(null)

    const result = isSignup
      ? await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: fullName },
            emailRedirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}`,
          },
        })
      : await supabase.auth.signInWithPassword({ email, password })

    setIsLoading(false)

    if (result.error) {
      setError(result.error.message)
      return
    }

    if (isSignup && !result.data.session) {
      setMessage('Check your email to confirm the account, then come back to continue planning.')
      return
    }

    // Wait for the session to be persisted before redirecting
    const { data: { session } } = await supabase.auth.getSession()
    if (session) {
      router.push(next)
      router.refresh()
    } else {
      setError('Authentication succeeded but session was not created. Please try again.')
    }
  }

  async function handleGoogleSignIn() {
    setIsLoading(true)
    setError(null)
    const { error: oauthError } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}`,
      },
    })

    if (oauthError) {
      setError(oauthError.message)
      setIsLoading(false)
    }
  }

  return (
    <div className="mx-auto w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold text-slate-950 dark:text-white">
          {isSignup ? 'Create your account' : 'Welcome back'}
        </h1>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          {isSignup
            ? 'Use Supabase Auth to keep your trips synced and protected.'
            : 'Sign in to open your saved planning workspace.'}
        </p>
      </div>

      <form onSubmit={handlePasswordSubmit} className="mt-6 space-y-4">
        {isSignup ? (
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
            Full name
            <input
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none transition focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900 dark:focus:border-white"
              autoComplete="name"
            />
          </label>
        ) : null}
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
          Email
          <input
            required
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none transition focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900 dark:focus:border-white"
            autoComplete="email"
          />
        </label>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
          Password
          <input
            required
            type="password"
            minLength={6}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none transition focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900 dark:focus:border-white"
            autoComplete={isSignup ? 'new-password' : 'current-password'}
          />
        </label>

        {error ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-200">
            {error}
          </p>
        ) : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800 dark:border-emerald-900/60 dark:bg-emerald-950/30 dark:text-emerald-200">
            {message}
          </p>
        ) : null}

        <Button className="w-full" size="lg" disabled={isLoading}>
          {isLoading ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : isSignup ? <UserPlus className="size-4" aria-hidden="true" /> : <Mail className="size-4" aria-hidden="true" />}
          {isSignup ? 'Sign Up' : 'Log In'}
        </Button>
      </form>

      <div className="my-5 flex items-center gap-3 text-xs uppercase text-slate-400">
        <span className="h-px flex-1 bg-slate-200 dark:bg-slate-800" />
        or
        <span className="h-px flex-1 bg-slate-200 dark:bg-slate-800" />
      </div>

      <Button variant="outline" className="w-full" size="lg" onClick={handleGoogleSignIn} disabled={isLoading}>
        <Globe2 className="size-4" aria-hidden="true" />
        Continue with Google
      </Button>

      <p className="mt-5 text-center text-sm text-slate-600 dark:text-slate-400">
        {isSignup ? 'Already have an account?' : 'New to TravelMate?'}{' '}
        <Link className="font-medium text-slate-950 underline-offset-4 hover:underline dark:text-white" href={isSignup ? `/sign-in?next=${encodeURIComponent(next)}` : `/sign-up?next=${encodeURIComponent(next)}`}>
          {isSignup ? 'Log in' : 'Sign up'}
        </Link>
      </p>
    </div>
  )
}
