import React from 'react';
import { Navbar } from './Navbar';
import { ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-sky-500/20 selection:text-sky-300">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-sky-400" />
            <span>DevGuard AI — Automated Code Review & Pull Request Assistant</span>
          </div>
          <div className="flex items-center space-x-6">
            <Link to="/settings" className="hover:text-slate-300 transition-colors">
              Settings
            </Link>
            <a href="/docs" target="_blank" rel="noreferrer" className="hover:text-slate-300 transition-colors">
              OpenAPI Swagger
            </a>
            <span className="text-slate-400">Deterministic Engine + Optional LLM</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
