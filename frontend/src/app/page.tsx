'use client';

import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { useDebounce } from 'use-debounce';
import { Search, Bell, RefreshCw, Menu, X, ShieldAlert } from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import MetricCards from '@/components/MetricCards';
import RiskDonutChart from '@/components/RiskDonutChart';
import RevenueAreaChart from '@/components/RevenueAreaChart';
import WhatIfSimulator from '@/components/WhatIfSimulator';
import CustomerTable from '@/components/CustomerTable';
import CustomerProfileModal from '@/components/CustomerProfileModal';
import { fetchSegmentation } from '@/lib/api';
import { Moon, Sun } from 'lucide-react';
import { ReferenceLine, Cell, PieChart, Pie, ScatterChart, Scatter, ZAxis, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import {
  fetchDashboardSummary,
  fetchCustomers,
  simulateDiscount,
  retrainModel,
  getModelStatus,
} from '@/lib/api';
import { SimulationResponse, RetrainResponse } from '@/lib/types';

export default function DashboardPage() {
  const [activePage, setActivePage] = useState('dashboard');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  // Added a simpler approach: a full screen invisible overlay when dropdown is open
  const closeDropdowns = () => { setProfileOpen(false); setNotifOpen(false); };

  // Data fetching using SWR
  const { 
    data: summary, 
    error: summaryError,
    mutate: mutateSummary 
  } = useSWR('dashboard-summary', fetchDashboardSummary);

  const [customerPage, setCustomerPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch] = useDebounce(searchTerm, 500);

  const { 
    data: customersData, 
    mutate: mutateCustomers 
  } = useSWR(
    ['customers', customerPage, debouncedSearch],
    ([_, page, search]) => fetchCustomers(page, 10, 0, 'churn_probability', 'desc', search)
  );

  
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  
  // Segmentation data
  const { data: segData } = useSWR(activePage === 'analytics' ? 'segmentation' : null, fetchSegmentation);

  const [simResult, setSimResult] = useState<SimulationResponse | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // Model settings state
  const [retrainResult, setRetrainResult] = useState<RetrainResponse | null>(null);
  const [retrainProgress, setRetrainProgress] = useState(0);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  
  // Polling model status
  const { data: modelStatus, mutate: mutateModelStatus } = useSWR(
    'model-status', 
    getModelStatus, 
    { refreshInterval: retrainResult?.status === 'training_started' || retrainResult?.status === 'training' ? 2000 : 5000 }
  );

  useEffect(() => {
    if (modelStatus?.status === 'success' || modelStatus?.status === 'error') {
      setRetrainResult(modelStatus);
      if (modelStatus.status === 'success') {
        mutateSummary();
        mutateCustomers();
      }
    }
  }, [modelStatus, mutateSummary, mutateCustomers]);

  const loading = !summary && !summaryError;
  const error = summaryError;

  // Customer pagination
  const handlePageChange = (page: number) => {
    setCustomerPage(page);
  };

  // Simulation
  const handleSimulate = async (discount: number, threshold: number) => {
    setIsSimulating(true);
    try {
      const result = await simulateDiscount(discount, threshold);
      setSimResult(result);
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  // Retrain
  const handleRetrain = async () => {
    try {
      setRetrainResult({ status: 'training_started', message: 'Training in progress...' });
      setRetrainProgress(0);
      
      const interval = setInterval(() => {
        setRetrainProgress((p: number) => {
          if (p >= 95) return 95;
          return p + (95 - p) * 0.15;
        });
      }, 500);

      const result = await retrainModel();
      clearInterval(interval);
      setRetrainProgress(100);
      
      setTimeout(() => {
        setRetrainResult(result);
        mutateModelStatus(result, false);
      }, 600);
    } catch (err) {
      console.error('Retrain trigger failed:', err);
      setRetrainResult({ status: 'error', message: 'Failed to trigger training' });
    }
  };

  // Generate simulation chart data
  const simulationChartData = {
    withoutIntervention: simResult?.projection_without_intervention || Array(6).fill(summary?.total_revenue || 0),
    withIntervention: simResult?.projection_with_intervention || Array(6).fill(summary?.total_revenue || 0),
  };

  // Drift status
  const driftStatus = summary?.drift_metrics?.status;
  const psiScore = summary?.drift_metrics?.psi_score;

  const isTraining = modelStatus?.status === 'training' || modelStatus?.status === 'training_started' || retrainResult?.status === 'training_started';

  const renderSettings = () => (
    <div className="space-y-6 max-w-5xl">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Model Settings</h1>
      {driftStatus && driftStatus !== 'Stable' && (
        <div className={`p-4 rounded-2xl border ${
          driftStatus === 'Critical'
            ? 'bg-rose-50 border-rose-200 text-rose-800'
            : 'bg-amber-50 border-amber-200 text-amber-800'
        }`}>
          <div className="flex gap-3">
             <ShieldAlert className="w-5 h-5 flex-shrink-0" />
             <div>
                <p className="font-semibold text-sm">Data Drift Detected — MonthlyCharges PSI: {psiScore?.toFixed(4)}</p>
                <p className="text-sm mt-1 opacity-90">
                  {driftStatus === 'Critical'
                    ? 'Significant distribution shift detected. Retrain immediately.'
                    : 'Moderate shift detected. Consider retraining the model.'}
                </p>
             </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm p-8 border border-slate-100 dark:border-slate-800">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">Current Model Engine</h2>
          <div className="space-y-5">
            <div className="flex justify-between items-center py-3 border-b border-slate-100 dark:border-slate-800">
              <span className="text-sm text-slate-500 dark:text-slate-400">LLM Engine</span>
              <span className="text-sm font-semibold text-slate-900 dark:text-white px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-full border border-slate-200 dark:border-slate-700">GPT OSS 120B</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-slate-100 dark:border-slate-800">
              <span className="text-sm text-slate-500 dark:text-slate-400">Context Window</span>
              <span className="text-sm font-semibold text-slate-900 dark:text-white">
                {modelStatus?.metrics?.context_window ? `${modelStatus.metrics.context_window.toLocaleString()} Tokens` : '8,192 Tokens'}
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-slate-100 dark:border-slate-800">
              <span className="text-sm text-slate-500 dark:text-slate-400">Average Inference Latency</span>
              <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                {modelStatus?.metrics?.latency ? `~${Math.round(modelStatus.metrics.latency)}ms (Live)` : '~320ms (Edge)'}
              </span>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-sm text-slate-500 dark:text-slate-400">Knowledge Base Status</span>
              <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                Synced with Neon PostgreSQL
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm p-8 border border-slate-100 dark:border-slate-800">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Sync Knowledge Base</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-8">
            Sync the latest customer interactions and billing history from your Neon PostgreSQL database into the LLM's context.
            This ensures GPT OSS 120B's churn predictions and explanations are strictly grounded in real-time data.
          </p>
          <div className="flex flex-col gap-4">
            <button
              onClick={handleRetrain}
              disabled={isTraining}
              className="flex items-center justify-center sm:justify-start gap-3 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white rounded-xl px-6 py-3 font-medium transition-all shadow-sm w-fit"
            >
              <RefreshCw className={`w-4 h-4 ${isTraining ? 'animate-spin' : ''}`} />
              {isTraining ? 'Training in progress...' : 'Sync Knowledge Base'}
            </button>
            
            {isTraining && (
              <div className="w-full max-w-sm mt-2">
                <div className="flex justify-between text-xs font-semibold text-slate-500 dark:text-slate-400 dark:text-slate-500 mb-2">
                  <span>Recompiling weights & running SHAP...</span>
                  <span>{Math.round(retrainProgress)}%</span>
                </div>
                <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-slate-900 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${retrainProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {retrainResult && !isTraining && (
            <div className={`mt-6 p-5 rounded-2xl border ${
              retrainResult.status === 'success' ? 'bg-emerald-50 border-emerald-100' : 'bg-rose-50 border-rose-100'
            }`}>
              <p className={`font-semibold text-sm ${
                retrainResult.status === 'success' ? 'text-emerald-800' : 'text-rose-800'
              }`}>
                {retrainResult.message}
              </p>
              {retrainResult.status === 'success' && (
                <div className="mt-3 text-sm text-emerald-700 font-medium">
                  ROC-AUC: {retrainResult.roc_auc} &bull; Brier: {retrainResult.brier_score}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderCustomers = () => (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Customer Risk Explorer</h1>
      <CustomerTable
        customers={customersData?.customers || []}
        total={customersData?.total || 0}
        page={customerPage}
        onPageChange={handlePageChange}
        searchTerm={searchTerm}
        onSearchChange={(val) => {
          setSearchTerm(val);
          setCustomerPage(1);
        }}
        onRowClick={(id) => setSelectedCustomerId(id)}
      />
    </div>
  );

  
  const renderAnalytics = () => (
    <div className="space-y-6 max-w-6xl">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Cohort Analytics</h1>
      
      {!segData ? (
        <div className="flex items-center justify-center py-20"><RefreshCw className="w-8 h-8 text-indigo-600 animate-spin" /></div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800">
               <h3 className="font-bold text-slate-900 dark:text-white mb-4">Risk by Contract</h3>
               <div className="space-y-4">
                 {segData.contract_risk.map(c => (
                   <div key={c.segment}>
                     <div className="flex justify-between text-sm mb-1"><span className="font-medium text-slate-700 dark:text-slate-300">{c.segment}</span><span className="font-bold text-slate-900 dark:text-white">{Math.round(c.avg_risk*100)}%</span></div>
                     <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-indigo-500 rounded-full" style={{width: `${c.avg_risk*100}%`}}></div></div>
                   </div>
                 ))}
               </div>
            </div>
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800">
               <h3 className="font-bold text-slate-900 dark:text-white mb-4">Risk by Internet</h3>
               <div className="space-y-4">
                 {segData.internet_risk.map(c => (
                   <div key={c.segment}>
                     <div className="flex justify-between text-sm mb-1"><span className="font-medium text-slate-700 dark:text-slate-300">{c.segment}</span><span className="font-bold text-slate-900 dark:text-white">{Math.round(c.avg_risk*100)}%</span></div>
                     <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-rose-500 rounded-full" style={{width: `${c.avg_risk*100}%`}}></div></div>
                   </div>
                 ))}
               </div>
            </div>
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800">
               <h3 className="font-bold text-slate-900 dark:text-white mb-4">Risk by Payment</h3>
               <div className="space-y-4">
                 {segData.payment_risk.map(c => (
                   <div key={c.segment}>
                     <div className="flex justify-between text-sm mb-1"><span className="font-medium text-slate-700 dark:text-slate-300">{c.segment}</span><span className="font-bold text-slate-900 dark:text-white">{Math.round(c.avg_risk*100)}%</span></div>
                     <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-emerald-500 rounded-full" style={{width: `${c.avg_risk*100}%`}}></div></div>
                   </div>
                 ))}
               </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 h-[400px]">
             <h3 className="font-bold text-slate-900 dark:text-white mb-1">Value Matrix (Sample)</h3>
             <p className="text-xs font-medium text-slate-500 dark:text-slate-400 dark:text-slate-500 mb-6">Top right quadrant = High Value, High Risk. Target immediately.</p>
             <ResponsiveContainer width="100%" height="100%">
               <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                 <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                 <XAxis 
                   type="number" 
                   dataKey="churn_probability" 
                   name="Churn Risk" 
                   domain={[0, 1]} 
                   tick={{fill: '#64748b', fontSize: 12}} 
                   axisLine={false}
                   tickLine={false}
                 />
                 <YAxis 
                   type="number" 
                   dataKey="monthly_charges" 
                   name="MRR ($)" 
                   tick={{fill: '#64748b', fontSize: 12}} 
                   axisLine={false}
                   tickLine={false}
                 />
                 <Tooltip 
                   cursor={{strokeDasharray: '3 3', stroke: '#cbd5e1'}} 
                   contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 8px 30px rgb(0,0,0,0.08)'}} 
                   formatter={(value: any, name: any) => {
                     if (name === 'Churn Risk') return [`${Math.round(value * 100)}%`, name];
                     if (name === 'MRR ($)') return [`$${value.toFixed(2)}`, name];
                     return [value, name];
                   }}
                 />
                 <ReferenceLine x={0.5} stroke="#94a3b8" strokeDasharray="4 4" strokeWidth={1.5} opacity={0.5} />
                 <ReferenceLine y={60} stroke="#94a3b8" strokeDasharray="4 4" strokeWidth={1.5} opacity={0.5} />
                 
                 <Scatter name="Customers" data={segData.value_matrix}>
                   {segData.value_matrix.map((entry: any, index: number) => {
                     const isHighRisk = entry.churn_probability > 0.5;
                     const isHighValue = entry.monthly_charges > 60;
                     
                     let fill = '#3b82f6'; // Safe
                     if (isHighRisk && isHighValue) fill = '#ef4444'; // Danger
                     else if (isHighRisk && !isHighValue) fill = '#f59e0b'; // Warning
                     else if (!isHighRisk && isHighValue) fill = '#10b981'; // Success
                     
                     return <Cell key={`cell-${index}`} fill={fill} fillOpacity={0.7} stroke={fill} strokeWidth={1} />;
                   })}
                 </Scatter>
               </ScatterChart>
             </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );

  const renderDashboard = () => (
    <div className="space-y-6">
      {error && (
        <div className="bg-rose-50 border border-rose-100 rounded-2xl p-5 text-rose-800 flex items-center justify-between">
          <div>
            <p className="font-semibold">Failed to connect to backend</p>
            <p className="text-sm mt-1">{error.message}</p>
          </div>
          <button onClick={() => mutateSummary()} className="text-sm font-medium text-rose-600 bg-white dark:bg-slate-900 px-4 py-2 rounded-lg border border-rose-200 hover:bg-rose-50">
            Retry
          </button>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-32">
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      )}

      {!loading && summary && (
        <>
          {driftStatus && driftStatus !== 'Stable' && (
            <div className={`p-4 rounded-2xl border flex items-center justify-between ${
              driftStatus === 'Critical'
                ? 'bg-rose-50 border-rose-200 text-rose-800'
                : 'bg-amber-50 border-amber-200 text-amber-800'
            }`}>
              <div className="flex gap-3 items-center">
                 <ShieldAlert className="w-5 h-5 flex-shrink-0" />
                 <p className="font-medium text-sm">
                   Data Drift Alert — PSI: {psiScore?.toFixed(4)} on MonthlyCharges.
                 </p>
              </div>
              <button onClick={() => setActivePage('settings')} className="text-sm font-semibold underline hover:no-underline">
                Resolve →
              </button>
            </div>
          )}

          <MetricCards totalRevenue={summary?.total_revenue || 0} revenueAtRisk={summary?.revenue_at_risk || 0} totalCustomers={summary?.total_customers || 0} avgChurnRisk={summary?.avg_churn_risk || 0} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RiskDonutChart 
              data={{
                highRisk: customersData?.customers.filter((c: any) => c.churn_probability > 0.75).length || 0,
                mediumRisk: customersData?.customers.filter((c: any) => c.churn_probability > 0.5 && c.churn_probability <= 0.75).length || 0,
                lowRisk: customersData?.customers.filter((c: any) => c.churn_probability <= 0.5).length || 0,
              }} 
            />
            <RevenueAreaChart 
                baselineRevenue={simResult ? simResult.projection_without_intervention : []} 
                retainedRevenue={simResult ? simResult.projection_with_intervention : []} 
              />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <div className="relative h-full">
                {isSimulating && (
                   <div className="absolute inset-0 bg-white dark:bg-slate-900/60 backdrop-blur-[2px] z-10 flex items-center justify-center rounded-3xl">
                      <RefreshCw className="w-6 h-6 text-blue-600 animate-spin" />
                   </div>
                )}
                <WhatIfSimulator onSimulate={handleSimulate} result={simResult} />
              </div>
            </div>
            <div className="lg:col-span-2">
              <CustomerTable
                customers={customersData?.customers || []}
                total={customersData?.total || 0}
                page={customerPage}
                onPageChange={handlePageChange}
                searchTerm={searchTerm}
                onSearchChange={(val) => {
                  setSearchTerm(val);
                  setCustomerPage(1);
                }}
                onRowClick={(id) => setSelectedCustomerId(id)}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );

  return (
    <div className={`flex h-screen bg-slate-50 dark:bg-slate-950 p-2 sm:p-4 overflow-hidden relative ${isDark ? "dark" : ""}`}>
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      
      <main className="flex-1 bg-white dark:bg-slate-900 rounded-[32px] shadow-sm border border-slate-200 dark:border-slate-700 overflow-x-hidden overflow-y-auto relative z-0 md:ml-[264px] flex flex-col h-full">
        {(profileOpen || notifOpen) && (
          <div className="fixed inset-0 z-20" onClick={closeDropdowns} />
        )}
        
        {/* Universal Header */}
        <header className="bg-white dark:bg-slate-900/90 backdrop-blur-md px-6 md:px-12 py-6 flex items-center justify-between sticky top-0 z-30 rounded-t-[32px]">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white hidden sm:block">
            {activePage === 'dashboard' ? 'Revenue Analytics' : activePage.charAt(0).toUpperCase() + activePage.slice(1)}
          </h2>
          
          <div className="flex flex-1 sm:flex-none items-center justify-end gap-4 md:gap-6">
            <div className="relative max-w-md w-full sm:w-64">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500" />
              <input
                type="text"
                placeholder="Search anything..."
                className="w-full bg-slate-50 dark:bg-slate-950 text-sm font-medium text-slate-800 dark:text-slate-100 rounded-full pl-11 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-slate-200 transition-shadow"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <button className="w-10 h-10 flex items-center justify-center rounded-full text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:text-slate-400 dark:text-slate-500 hover:bg-slate-50 dark:bg-slate-950 transition-colors relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
              </button>
              <div className="hidden sm:flex items-center bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-full p-1 gap-1">
                <button 
                  onClick={() => setIsDark(true)}
                  className={`w-8 h-8 flex items-center justify-center rounded-full transition-colors ${isDark ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'}`}>
                  <Moon className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => setIsDark(false)}
                  className={`w-8 h-8 flex items-center justify-center rounded-full transition-colors ${!isDark ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'}`}>
                  <Sun className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="w-10 h-10 rounded-full bg-blue-500 overflow-hidden cursor-pointer flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold text-sm">SI</span>
            </div>
          </div>
        </header>

        {/* Dynamic Body */}
        <div className="flex-1 p-6 md:p-12">
          {activePage === 'settings' && renderSettings()}
          {activePage === 'customers' && renderCustomers()}
          {activePage === 'dashboard' && renderDashboard()}
          {activePage === 'analytics' && renderAnalytics()}
        </div>
      </main>
      
      {selectedCustomerId && (
        <CustomerProfileModal customerId={selectedCustomerId} onClose={() => setSelectedCustomerId(null)} />
      )}
    </div>
  );
}
