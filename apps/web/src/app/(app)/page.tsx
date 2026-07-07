import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] text-center px-4">
      <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl text-slate-900 dark:text-white">
        Your Intelligent Travel Companion
      </h1>
      <p className="mt-6 text-xl text-slate-600 dark:text-slate-400 max-w-2xl">
        TravelMate AI plans multi-modal journeys combining trains, buses, and flights with real-time confidence scoring and alternative routes.
      </p>
      <div className="mt-10 flex items-center justify-center gap-x-6">
        <Link href="/planner">
          <Button size="lg" className="text-lg px-8">
            Start Planning
          </Button>
        </Link>
        <Link href="/about" className="text-sm font-semibold leading-6 text-slate-900 dark:text-slate-300">
          Learn more <span aria-hidden="true">→</span>
        </Link>
      </div>
    </div>
  )
}
