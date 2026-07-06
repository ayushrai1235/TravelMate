import { NextRequest } from 'next/server'
import { proxyToBackend } from '@/lib/api/bff'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function POST(request: NextRequest) {
  return proxyToBackend({ backendPath: '/v1/trips/plan', request })
}
