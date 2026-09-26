'use client';

import React, { useState } from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface Props {
  baselineRevenue: number[];
  retainedRevenue: number[];
  targetMRR?: number;
}

export default function RevenueAreaChart({ baselineRevenue, retainedRevenue, targetMRR = 456000 }: Props) {
  const [timeRange, setTimeRange] = useState<'Days' | 'Week' | 'Month'>('Month');

  const timeLabels = {
    Days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    Week: ['W1', 'W2', 'W3', 'W4'],
    Month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
  }[timeRange];
  
  const numPoints = timeRange === 'Days' ? 7 : timeRange === 'Week' ? 28 : 30;
  const baseMultiplier = timeRange === 'Days' ? 0.05 : timeRange === 'Week' ? 0.2 : 1;
  
  const data = [];
  // Build backwards from the target MRR to create a realistic trajectory
  let currentVal = targetMRR;
  const historicalData = [];
  for (let i = numPoints - 1; i >= 0; i--) {
    const added = Math.max(1000, Math.random() * 8000); // Add 1k-8k per day/week/month
    historicalData.unshift({ val: currentVal, added: added });
    currentVal -= added;
  }
  
  for (let i = 0; i < numPoints; i++) {
    const labelIdx = Math.floor(i / (numPoints / timeLabels.length));
    const point = historicalData[i];
    data.push({
      name: timeLabels[Math.min(labelIdx, timeLabels.length - 1)],
      total: Math.floor(point.val),
      added: Math.floor(point.added),
      fullDate: timeRange === 'Month' ? `${Math.floor((i % 30) + 1)} ${timeLabels[Math.min(labelIdx, timeLabels.length - 1)]} 2026` : `${timeLabels[Math.min(labelIdx, timeLabels.length - 1)]}`
    });
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const total = payload.find((p: any) => p.dataKey === 'total')?.value;
      const added = payload.find((p: any) => p.dataKey === 'added')?.value;

      return (
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-lg border border-slate-200 dark:border-slate-800 flex flex-col gap-2 min-w-[150px]">
          <p className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{payload[0].payload.fullDate}</p>
          
          <div className="flex justify-between items-end">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Total</span>
            <span className="text-base font-bold text-slate-900 dark:text-white">
              ${new Intl.NumberFormat('en-US', { notation: "compact", compactDisplay: "short" }).format(total)}
            </span>
          </div>

          <div className="flex justify-between items-end border-t border-slate-100 dark:border-slate-800 pt-2 mt-1">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Added</span>
            <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
              +${new Intl.NumberFormat('en-US').format(added)}
            </span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 shadow-[0_2px_10px_rgb(0,0,0,0.02)] border border-slate-100 dark:border-slate-800 w-full h-full flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100">Revenue Trajectory</h3>
        <div className="flex bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 rounded-full p-1 gap-1">
          {(['Days', 'Week', 'Month'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-colors ${
                timeRange === range
                  ? 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1 w-full relative min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={data}
            margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="var(--chart-grid)" />
            
            <XAxis 
              dataKey="name" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--chart-text)', fontSize: 11, fontWeight: 600 }}
              tickMargin={12}
              interval={4} 
            />
            
            {/* Left Axis for Total Revenue */}
            <YAxis 
              yAxisId="left"
              axisLine={false} 
              tickLine={false}
              tickFormatter={(val) => val === 0 ? '$0' : `${val / 1000}k`}
              tick={{ fill: 'var(--chart-text)', fontSize: 11, fontWeight: 600 }}
              tickMargin={12}
            />

            {/* Right Axis for Added Revenue (hidden but used for scaling the bars properly) */}
            <YAxis 
              yAxisId="right"
              orientation="right"
              axisLine={false}
              tickLine={false}
              tick={false}
              width={0}
            />

            <Tooltip 
               content={<CustomTooltip />} 
               cursor={{ fill: 'var(--chart-grid)', opacity: 0.4 }} 
            />
            
            <Bar 
              yAxisId="right"
              dataKey="added" 
              fill="var(--chart-bar)" 
              radius={[2, 2, 0, 0]} 
              maxBarSize={8}
            />
            
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="total"
              stroke="var(--chart-primary)"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 5, fill: 'var(--chart-primary)', stroke: 'var(--background)', strokeWidth: 2 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
