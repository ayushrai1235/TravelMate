import { redirect } from 'next/navigation'

export default function SignupRedirectPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>
}) {
  return searchParams.then(({ next }) => {
    redirect(`/sign-up${next ? `?next=${encodeURIComponent(next)}` : ''}`)
  })
}
