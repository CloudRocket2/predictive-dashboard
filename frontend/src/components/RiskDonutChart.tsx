'use client';

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { ArrowUpRight } from 'lucide-react';

interface Props {
  data: {
    highRisk: number;
    mediumRisk: number;
    lowRisk: number;
    lowRevenue?: number;
    mediumRevenue?: number;
    highRevenue?: number;
    totalRevenue?: number;
  };
}

export default function RiskDonutChart({ data }: Props) {
  const chartData = [
    { name: 'Low Risk', value: data.lowRisk || 0, color: '#3b82f6', amount: data.lowRevenue || 0 },
    { name: 'Medium Risk', value: data.mediumRisk || 0, color: '#f59e0b', amount: data.mediumRevenue || 0 },
    { name: 'High Risk', value: data.highRisk || 0, color: '#ef4444', amount: data.highRevenue || 0 },
  ];

  const total = chartData.reduce((acc, curr) => acc + curr.value, 0);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 shadow-[0_2px_10px_rgb(0,0,0,0.02)] border border-slate-100 dark:border-slate-800 flex flex-col h-full relative">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100">Risk Distribution</h3>
        <button className="text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:text-slate-400 dark:text-slate-500">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
          </svg>
        </button>
      </div>

      {/* Gauge Chart */}
      <div className="relative h-48 w-full mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="100%" // Center y at the bottom to make a perfect semi-circle
              startAngle={180}
              endAngle={0}
              innerRadius={120}
              outerRadius={150}
              paddingAngle={2}
              dataKey="value"
              stroke="none"
              cornerRadius={100} // Extra rounded ends
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
               contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 8px 30px rgb(0,0,0,0.08)'}}
               itemStyle={{fontWeight: 'bold'}}
            />
          </PieChart>
        </ResponsiveContainer>
        
        {/* Center Text */}
        <div className="absolute bottom-2 left-0 right-0 flex flex-col items-center justify-end pb-2">
          <span className="text-4xl font-black text-slate-900 dark:text-white tracking-tight">${new Intl.NumberFormat('en-US').format(data.totalRevenue || 0)}</span>
          <div className="flex items-center gap-1 mt-1">
            <ArrowUpRight className="w-4 h-4 text-emerald-500 stroke-[3]" />
            <span className="text-sm font-bold text-emerald-500">16.8%</span>
            <span className="text-sm font-medium text-slate-400 dark:text-slate-500 ml-1">Last month</span>
          </div>
        </div>
      </div>

      {/* Legend List */}
      <div className="mt-8 space-y-4">
        {chartData.map((item, i) => (
          <div key={i} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="font-semibold text-slate-600 dark:text-slate-400 dark:text-slate-500">{item.name}</span>
            </div>
            <div className="flex items-center gap-6">
              <span className="text-slate-400 dark:text-slate-500 font-medium w-10 text-right">
                {Math.round((item.value / (total || 1)) * 100)}%
              </span>
              <span className="font-semibold text-slate-800 dark:text-slate-100 w-16 text-right">
                ${new Intl.NumberFormat('en-US').format(item.amount)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
