'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';
import { SimulationResponse } from '@/lib/types';

interface WhatIfSimulatorProps {
  onSimulate: (discount: number, threshold: number) => void;
  result: SimulationResponse | null;
}

export default function WhatIfSimulator({ onSimulate, result }: WhatIfSimulatorProps) {
  const [discountPct, setDiscountPct] = useState(10);
  const [riskThreshold, setRiskThreshold] = useState(0.70);

  useEffect(() => {
    onSimulate(discountPct, riskThreshold);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSimulate = () => {
    onSimulate(discountPct, riskThreshold);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm p-6">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-5 h-5 text-blue-600" />
        <h2 className="text-lg font-semibold text-gray-900">What-If Simulator</h2>
      </div>

      <div className="space-y-6">
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-700">Discount %</label>
            <span className="bg-blue-100 text-blue-700 text-xs font-semibold px-2 py-1 rounded-full">
              {discountPct}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="50"
            step="1"
            value={discountPct}
            onChange={(e) => setDiscountPct(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-700">Risk Threshold</label>
            <span className="bg-blue-100 text-blue-700 text-xs font-semibold px-2 py-1 rounded-full">
              {riskThreshold.toFixed(2)}
            </span>
          </div>
          <input
            type="range"
            min="0.50"
            max="0.95"
            step="0.05"
            value={riskThreshold}
            onChange={(e) => setRiskThreshold(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
        </div>

        <button
          onClick={handleSimulate}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-6 py-2.5 font-medium transition-colors"
        >
          Run Simulation
        </button>

        {result && (
          <div className="mt-2 grid grid-cols-2 gap-4">
            <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl">
              <div className="text-sm text-gray-500 mb-1">Customers Targeted</div>
              <div className="text-xl font-semibold">{result.customers_targeted}</div>
            </div>
            <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl">
              <div className="text-sm text-gray-500 mb-1">Revenue at Risk</div>
              <div className="text-xl font-semibold">{formatCurrency(result.original_revenue_at_risk)}</div>
            </div>
            <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl">
              <div className="text-sm text-gray-500 mb-1">Discount Cost</div>
              <div className="text-xl font-semibold text-rose-500">-{formatCurrency(result.discount_cost)}</div>
            </div>
            <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl">
              <div className="text-sm text-gray-500 mb-1">Net Savings</div>
              <div className="text-2xl font-bold text-emerald-500">{formatCurrency(result.net_savings)}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
