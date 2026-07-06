import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function PlannerPage() {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-white">Trip Planner</h1>
      <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">
        Welcome, {user.email}. Start planning your next adventure.
      </p>
      
      {/* Planner functionality will be implemented here */}
      <div className="mt-8 p-6 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
        <p className="text-center text-slate-500">Trip Planner Form Coming Soon</p>
      </div>
    </div>
  )
}
