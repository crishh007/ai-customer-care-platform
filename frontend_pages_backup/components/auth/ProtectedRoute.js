// ASSIGNED TO: FE-1
// HOC to protect pages requiring authentication
// - Read JWT from localStorage
// - If missing or expired → redirect to /login
// - Otherwise render children

import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function ProtectedRoute({ children }) {
  const router = useRouter()

  useEffect(() => {
    // TODO: const token = localStorage.getItem('token')
    // TODO: if (!token) router.push('/login')
  }, [])

  return children
}
