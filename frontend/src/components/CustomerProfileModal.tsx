'use client';

import React from 'react';
import useSWR from 'swr';
import { X, Activity, User, CreditCard, Monitor, CheckCircle } from 'lucide-react';
import { fetchCustomerDeepDive, triggerCampaign } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface Props {
  customerId: string;
  onClose: () => void;
}

export default function CustomerProfileModal({ customerId, onClose }: Props) {
  const { data, error, isLoading } = useSWR(`customer-${customerId}`, () => fetchCustomerDeepDive(customerId));
  const [acting, setActing] = React.useState(false);

  const handleAction = async () => {
    setActing(true);
    try {
      await triggerCampaign(customerId);
      alert('Retention campaign successfully triggered.');
    } catch (err) {
      alert('Failed to trigger campaign');
    } finally {
      setActing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={onClose} />
      
      <div className="relative w-full max-w-4xl bg-white dark:bg-slate-900 rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-8 py-5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-white dark:bg-slate-900">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center">
              <User className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">{customerId}</h2>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Customer Deep Dive</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-8 overflow-y-auto flex-1 bg-slate-50 dark:bg-slate-950">
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-20">
              <Activity className="w-8 h-8 text-indigo-600 animate-spin mb-4" />
              <p className="text-slate-500 dark:text-slate-400 font-medium">Analyzing customer risk factors...</p>
            </div>
          )}
          
          {error && (
            <div className="bg-rose-50 border border-rose-200 text-rose-800 p-6 rounded-2xl">
              <p className="font-bold">Error loading customer data</p>
              <p className="text-sm mt-1">{error.message}</p>
            </div>
          )}

          {data && (
            <div className="space-y-6">
              {/* Top stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                  <p className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1">Churn Risk</p>
                  <p className={`text-2xl font-bold ${data.churn_probability > 0.5 ? 'text-rose-600' : 'text-emerald-600'}`}>
                    {Math.round(data.churn_probability * 100)}%
                  </p>
                </div>
                <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                  <p className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1">Monthly</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">${data.monthly_charges.toFixed(2)}</p>
                </div>
                <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                  <p className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1">Tenure</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">{data.tenure} <span className="text-sm text-slate-500 dark:text-slate-400">mos</span></p>
                </div>
                <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                  <p className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1">Total LTV</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">${data.total_charges.toFixed(2)}</p>
                </div>
              </div>

              {/* Main Analysis Area */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Details Column */}
                <div className="lg:col-span-1 space-y-6">
                  <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                    <h3 className="font-bold text-slate-900 dark:text-white mb-4">Demographics</h3>
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <CreditCard className="w-5 h-5 text-slate-400 dark:text-slate-500 mt-0.5" />
                        <div>
                          <p className="text-sm font-semibold text-slate-900 dark:text-white">{data.contract} Contract</p>
                          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{data.payment_method}</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <Monitor className="w-5 h-5 text-slate-400 dark:text-slate-500 mt-0.5" />
                        <div>
                          <p className="text-sm font-semibold text-slate-900 dark:text-white">{data.internet_service}</p>
                          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Internet Service</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-indigo-50 p-6 rounded-2xl border border-indigo-100">
                    <h3 className="font-bold text-indigo-900 mb-2">Recommended Action</h3>
                    <p className="text-sm text-indigo-700 font-medium leading-relaxed mb-4">
                      {data.contract === 'Month-to-month' 
                        ? 'Target with a 1-year contract upgrade offer and a 15% discount for 3 months.'
                        : 'Enroll in proactive check-in sequence to verify satisfaction.'}
                    </p>
                    <button 
                      onClick={handleAction}
                      disabled={acting}
                      className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {acting ? <Activity className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                      {acting ? 'Sending...' : 'Trigger Campaign'}
                    </button>
                  </div>
                </div>

                {/* SHAP Chart */}
                <div className="lg:col-span-2 bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                  <h3 className="font-bold text-slate-900 dark:text-white mb-1">Risk Drivers (SHAP Waterfall)</h3>
                  <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-6">Red pushes towards churn, green pushes away from churn.</p>
                  
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        layout="vertical"
                        data={data.shap_contributions}
                        margin={{ top: 0, right: 30, left: 100, bottom: 0 }}
                      >
                        <XAxis type="number" hide />
                        <YAxis 
                          dataKey="feature" 
                          type="category" 
                          axisLine={false} 
                          tickLine={false} 
                          tick={{ fill: '#64748b', fontSize: 12, fontWeight: 500 }} 
                          width={140}
                        />
                        <Tooltip 
                          cursor={{fill: '#f8fafc'}}
                          formatter={(value: any) => [value > 0 ? `+${Number(value).toFixed(3)}` : Number(value).toFixed(3), 'Impact']}
                          contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                          {data.shap_contributions.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.value > 0 ? '#ef4444' : '#10b981'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
