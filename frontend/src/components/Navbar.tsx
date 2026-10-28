import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  ShieldCheck,
  LayoutDashboard,
  GitPullRequest,
  FolderGit2,
  History,
  Settings,
  ExternalLink,
} from 'lucide-react';
import { api } from '../api/client';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        await api.checkHealth();
        if (isMounted) setIsBackendHealthy(true);
      } catch {
        if (isMounted) setIsBackendHealthy(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Review PR', path: '/review', icon: GitPullRequest },
    { name: 'Repositories', path: '/repositories', icon: FolderGit2 },
    { name: 'History', path: '/history', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-950/90 backdrop-blur border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo / Brand */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/30 group-hover:border-sky-400 transition-colors">
              <ShieldCheck className="w-5 h-5 text-sky-400" />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-white flex items-center">
                DevGuard <span className="text-sky-400 ml-1">AI</span>
              </span>
              <span className="text-[10px] text-slate-400 block -mt-1 font-mono">PR Review Assistant</span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-800 text-sky-400 shadow-sm'
                      : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Backend Status & Docs */}
          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-mono">
              <span
                className={`w-2 h-2 rounded-full ${
                  isBackendHealthy === null
                    ? 'bg-amber-400 animate-pulse'
                    : isBackendHealthy
                    ? 'bg-emerald-400'
                    : 'bg-red-400'
                }`}
              />
              <span className="text-slate-400">
                {isBackendHealthy === null
                  ? 'Connecting...'
                  : isBackendHealthy
                  ? 'API Ready'
                  : 'API Offline'}
              </span>
            </div>

            <a
              href="/docs"
              target="_blank"
              rel="noreferrer"
              className="hidden lg:flex items-center text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors px-2 py-1"
            >
              API Docs
              <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </div>
        </div>
      </div>
    </header>
  );
};
