import { redirect } from 'next/navigation'
import { AuthForm } from '@/components/auth/AuthForm'
import { createClient } from '@/lib/supabase/server'

export default async function SignInPage() {
  const supabase = await createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (user) {
    redirect('/planner')
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10 dark:bg-slate-950">
      <AuthForm mode="login" />
    </div>
  )
}
