import { redirect } from 'next/navigation'

export default function LoginRedirectPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>
}) {
  return searchParams.then(({ next }) => {
    redirect(`/sign-in${next ? `?next=${encodeURIComponent(next)}` : ''}`)
  })
}
