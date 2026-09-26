'use client';

import React, { useState } from 'react';
import { DollarSign, ArrowUpRight, ArrowDownRight, Users, Activity, TrendingUp } from 'lucide-react';

interface MetricCardsProps {
  totalRevenue: number;
  mrr: number;
  revenueAtRisk: number;
  totalCustomers: number;
  avgChurnRisk: number;
}

export default function MetricCards({ totalRevenue, mrr, revenueAtRisk, totalCustomers, avgChurnRisk }: MetricCardsProps) {
  const [timeRange, setTimeRange] = useState<'Days' | 'Week' | 'Month'>('Month');

  // Multipliers to mock data changing based on time range
  const multiplier = timeRange === 'Days' ? 0.03 : timeRange === 'Week' ? 0.25 : 1;

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };
  
  // Format to K/M for thousands/millions to match design
  const formatK = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value.toFixed(0)}`;
  };

  const metrics = [
    {
      title: 'Total Revenue',
      value: formatK(totalRevenue), // Historical total LTV
      trend: timeRange === 'Month' ? 4.8 : timeRange === 'Week' ? 1.2 : 0.1,
      icon: DollarSign,
    },
    {
      title: 'Monthly Recurring Revenue',
      value: formatK(mrr), 
      trend: timeRange === 'Month' ? 21.8 : timeRange === 'Week' ? 12.4 : 5.6,
      icon: TrendingUp,
    },
    {
      title: 'ARPU',
      value: `$${(mrr / (totalCustomers || 1)).toFixed(2)}`,
      trend: 16.8,
      icon: Users,
    },
    {
      title: 'Churn Rate',
      value: `${(avgChurnRisk * 100).toFixed(1)}%`,
      trend: -12.8,
      icon: Activity,
    },
  ];

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100">Overview</h3>
        <div className="flex bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 rounded-full p-1 gap-1">
          {(['Days', 'Week', 'Month'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-colors ${
                timeRange === range
                  ? 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:text-slate-100'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          const isPositive = metric.trend > 0;
          
          return (
            <div
              key={index}
              className="bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-[0_2px_10px_rgb(0,0,0,0.02)] border border-slate-100 dark:border-slate-800 flex flex-col justify-between h-36"
            >
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 rounded-full border border-slate-200 dark:border-slate-700 flex items-center justify-center bg-slate-50 dark:bg-slate-950">
                  <Icon className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
                </div>
                <span className="text-xs font-bold text-slate-600 dark:text-slate-400">{metric.title}</span>
              </div>
              
              <div className="mt-auto">
                <p className="text-3xl font-black text-slate-900 dark:text-white tracking-tight mb-2">
                  {metric.value}
                </p>
                <div className="flex items-center gap-1.5">
                  {isPositive ? (
                    <ArrowUpRight className="w-3.5 h-3.5 text-emerald-500 stroke-[3]" />
                  ) : (
                    <ArrowDownRight className="w-3.5 h-3.5 text-rose-500 stroke-[3]" />
                  )}
                  <span className={`text-xs font-bold ${isPositive ? 'text-emerald-500' : 'text-rose-500'}`}>
                    {Math.abs(metric.trend)}%
                  </span>
                  <span className="text-xs font-medium text-slate-400 dark:text-slate-500">vs last month</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
