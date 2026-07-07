import { createClient } from '@/lib/supabase/server'
import { PlannerWorkspace } from '@/components/planner/PlannerWorkspace'
import { redirect } from 'next/navigation'

export default async function PlannerPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/sign-in')
  }

  return <PlannerWorkspace userEmail={user.email} />
}
