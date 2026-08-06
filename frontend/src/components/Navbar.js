"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function Navbar() {
  const pathname = usePathname();
  const { isAuthenticated, logout } = useAuthStore();
  
  return (
    <nav className="w-full border-b border-white/10 bg-[#0a0a0a]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <div className="flex-shrink-0 flex items-center">
            <Link href="/" className="flex items-center gap-2">
              <span className="font-bold text-2xl tracking-tighter text-white uppercase">Rig<span className="text-[#ff4500]">.care</span></span>
            </Link>
          </div>
          
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-8">
              <Link href="/" className={`${pathname === '/' ? 'text-white' : 'text-gray-500'} nav-link font-mono uppercase text-xs`}>
                Landing
              </Link>
              <Link href="/chat" className={`${pathname === '/chat' ? 'text-white' : 'text-gray-500'} nav-link font-mono uppercase text-xs`}>
                Support AI
              </Link>
              {isAuthenticated ? (
                <>
                  <Link href="/dashboard" className={`${pathname === '/dashboard' ? 'text-white' : 'text-gray-500'} nav-link font-mono uppercase text-xs`}>
                    Dashboard
                  </Link>
                  <Link href="/tickets" className={`${pathname === '/tickets' ? 'text-white' : 'text-gray-500'} nav-link font-mono uppercase text-xs`}>
                    Escalations
                  </Link>
                  <button onClick={logout} className="nav-link font-mono uppercase text-xs text-red-500 hover:text-red-400">
                    Disconnect
                  </button>
                </>
              ) : (
                <div className="flex items-center space-x-4">
                  <Link href="/login" className="nav-link font-mono uppercase text-xs">
                    Login
                  </Link>
                  <Link href="/register" className="btn-primary">
                    Get Early Access
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
