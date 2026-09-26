'use client';

import React from 'react';
import { LayoutDashboard, Users, Settings, ChevronRight, PieChart } from 'lucide-react';

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
}

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'analytics', label: 'Revenue', icon: PieChart },
  { id: 'customers', label: 'Users', icon: Users },
  { id: 'settings', label: 'Setting', icon: Settings },
];

export default function Sidebar({ activePage, onNavigate }: SidebarProps) {
  return (
    <aside className="w-64 bg-slate-50 dark:bg-slate-950 h-[calc(100vh-32px)] flex-col fixed left-4 top-4 bottom-4 z-40 rounded-[32px] hidden md:flex border-r-0">
      {/* Logo */}
      <div className="px-8 py-8 flex items-center gap-3">
        <div className="w-8 h-8 flex items-center justify-center text-blue-500">
           {/* Abstract knot logo placeholder */}
           <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8">
             <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
           </svg>
        </div>
        <span className="text-xl font-semibold text-slate-800 dark:text-slate-100 tracking-tight">Predictive</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 mt-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const isActive = activePage === item.id;
            const Icon = item.icon;
            return (
              <li key={item.id}>
                <button
                  onClick={() => onNavigate(item.id)}
                  className={`w-full flex items-center gap-4 px-4 py-3 rounded-full text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                      : 'text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-900 dark:text-white hover:bg-slate-100 dark:bg-slate-800/50'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-slate-900 dark:text-white' : 'text-slate-400 dark:text-slate-500'}`} />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom: Settings & Workspace */}
      <div className="p-6">
        <div className="bg-white dark:bg-slate-900 rounded-full p-2 flex items-center gap-3 shadow-sm border border-slate-100 dark:border-slate-800 cursor-pointer hover:shadow-md transition-shadow">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-bold text-white">SI</span>
          </div>
          <div className="flex-1 min-w-0 pr-2">
            <p className="text-[10px] text-slate-400 dark:text-slate-500 font-medium uppercase tracking-wider leading-tight">Workspace</p>
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate leading-tight">Startup Inc.</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
