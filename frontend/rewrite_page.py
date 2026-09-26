import re

content = """'use client';

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

  // Close dropdowns on outside click roughly
  useEffect(() => {
    const closeDropdowns = () => { setProfileOpen(false); setNotifOpen(false); };
    document.addEventListener('click', closeDropdowns);
    return () => document.removeEventListener('click', closeDropdowns);
  }, []);

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

  const [simResult, setSimResult] = useState<SimulationResponse | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // Model settings state
  const [retrainResult, setRetrainResult] = useState<RetrainResponse | null>(null);
  
  // Polling model status
  const { data: modelStatus, mutate: mutateModelStatus } = useSWR(
    'model-status', 
    getModelStatus, 
    { refreshInterval: retrainResult?.status === 'training_started' || retrainResult?.status === 'training' ? 2000 : 0 }
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
      const result = await retrainModel();
      setRetrainResult(result);
      mutateModelStatus(result, false);
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
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Model Settings</h1>
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
        <div className="bg-white rounded-3xl shadow-sm p-8 border border-slate-100">
          <h2 className="text-lg font-semibold text-slate-900 mb-6">Current Model</h2>
          <div className="space-y-5">
            <div className="flex justify-between items-center py-3 border-b border-slate-50">
              <span className="text-sm text-slate-500">Algorithm</span>
              <span className="text-sm font-semibold text-slate-900 px-3 py-1 bg-slate-100 rounded-full">XGBoost</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-slate-50">
              <span className="text-sm text-slate-500">ROC-AUC</span>
              <span className="text-sm font-semibold text-slate-900">
                {summary?.model_roc_auc?.toFixed(4) ?? '--'}
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-slate-50">
              <span className="text-sm text-slate-500">Brier Score</span>
              <span className="text-sm font-semibold text-slate-900">
                {summary?.model_brier_score?.toFixed(4) ?? '--'}
              </span>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-sm text-slate-500">PSI (MonthlyCharges)</span>
              <span className={`text-sm font-semibold ${
                driftStatus === 'Stable' ? 'text-emerald-600' :
                driftStatus === 'Warning' ? 'text-amber-600' : 'text-rose-600'
              }`}>
                {psiScore?.toFixed(4) ?? '--'} ({driftStatus ?? 'Unknown'})
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow-sm p-8 border border-slate-100">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Retrain Model</h2>
          <p className="text-sm text-slate-500 leading-relaxed mb-8">
            Retrain the XGBoost model using the latest data in your Neon PostgreSQL database.
            This runs in the background and will dynamically update SHAP values and drift metrics.
          </p>
          <button
            onClick={handleRetrain}
            disabled={isTraining}
            className="flex items-center gap-3 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white rounded-xl px-6 py-3 font-medium transition-all shadow-sm"
          >
            <RefreshCw className={`w-4 h-4 ${isTraining ? 'animate-spin' : ''}`} />
            {isTraining ? 'Training in progress...' : 'Initiate Retrain'}
          </button>

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
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Customer Risk Explorer</h1>
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
      />
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
          <button onClick={() => mutateSummary()} className="text-sm font-medium text-rose-600 bg-white px-4 py-2 rounded-lg border border-rose-200 hover:bg-rose-50">
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

          <MetricCards
            data={{
              total_customers: summary.total_customers,
              total_revenue: summary.total_revenue,
              revenue_at_risk: summary.revenue_at_risk,
              avg_churn_risk: summary.avg_churn_risk,
            }}
            simulationSavings={simResult?.net_savings ?? null}
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RiskDonutChart
              customers={customersData?.customers.map((c) => ({
                churn_probability: c.churn_probability,
                monthly_charges: c.monthly_charges,
              })) || []}
            />
            <RevenueAreaChart simulationData={simulationChartData} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <div className="relative h-full">
                {isSimulating && (
                   <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-10 flex items-center justify-center rounded-3xl">
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
              />
            </div>
          </div>
        </>
      )}
    </div>
  );

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      
      <div className="flex-1 md:ml-64 flex flex-col min-h-screen">
        {/* Universal Header */}
        <header className="bg-white/80 backdrop-blur-md border-b border-slate-100 px-8 py-4 flex items-center justify-between sticky top-0 z-30">
          <div>
            <h1 className="text-xl font-bold text-slate-900 hidden md:block">Predictive Churn Dashboard</h1>
            <h1 className="text-xl font-bold text-slate-900 md:hidden">Churn Board</h1>
          </div>
          
          <div className="flex items-center gap-5">
            {/* Notifications Dropdown */}
            <div className="relative" onClick={(e) => e.stopPropagation()}>
              <button 
                onClick={() => { setNotifOpen(!notifOpen); setProfileOpen(false); }}
                className="relative p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-full transition-colors"
              >
                <Bell className="w-5 h-5" />
                {driftStatus === 'Critical' && (
                   <span className="absolute top-1.5 right-2 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white"></span>
                )}
              </button>
              
              {notifOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-100 rounded-2xl shadow-xl z-50 p-4 transform origin-top-right transition-all">
                  <h3 className="font-semibold text-slate-900 mb-3 text-sm">Notifications</h3>
                  {driftStatus === 'Critical' ? (
                    <div className="p-3 bg-rose-50 border border-rose-100 rounded-xl text-sm flex items-start gap-3">
                       <ShieldAlert className="w-5 h-5 text-rose-500 flex-shrink-0" />
                       <div>
                         <p className="font-semibold text-rose-900">Drift Alert</p>
                         <p className="text-rose-700 mt-0.5">Critical drift on MonthlyCharges. Model retraining recommended.</p>
                       </div>
                    </div>
                  ) : (
                    <div className="p-4 text-center">
                      <p className="text-sm text-slate-500">You're all caught up!</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Profile Dropdown */}
            <div className="relative" onClick={(e) => e.stopPropagation()}>
              <button 
                onClick={() => { setProfileOpen(!profileOpen); setNotifOpen(false); }}
                className="w-9 h-9 bg-indigo-600 hover:bg-indigo-700 transition-colors rounded-full flex items-center justify-center shadow-sm"
              >
                <span className="text-sm font-bold text-white">S</span>
              </button>
              
              {profileOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-100 rounded-2xl shadow-xl z-50 py-2 transform origin-top-right transition-all">
                  <div className="px-4 py-3 border-b border-slate-50 mb-2">
                    <p className="text-sm font-bold text-slate-900">Startup Inc.</p>
                    <p className="text-xs text-slate-500 font-medium">admin@startup.inc</p>
                  </div>
                  <button 
                    onClick={() => { setActivePage('settings'); setProfileOpen(false); }} 
                    className="w-full text-left px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-indigo-600 transition-colors"
                  >
                    Model Settings
                  </button>
                  <button className="w-full text-left px-4 py-2.5 text-sm font-medium text-rose-600 hover:bg-rose-50 transition-colors">
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Dynamic Body */}
        <main className="flex-1 p-8">
          {activePage === 'settings' && renderSettings()}
          {activePage === 'customers' && renderCustomers()}
          {activePage === 'dashboard' && renderDashboard()}
        </main>
      </div>
    </div>
  );
}
"""
with open('src/app/page.tsx', 'w') as f:
    f.write(content)
