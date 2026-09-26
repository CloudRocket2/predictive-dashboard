'use client';

import React from 'react';
import { Users, Search, Send } from 'lucide-react';
import { CustomerPrediction } from '@/lib/types';
import { triggerCampaign } from '@/lib/api';

interface CustomerTableProps {
  customers: CustomerPrediction[];
  total: number;
  page: number;
  onPageChange: (page: number) => void;
  searchTerm: string;
  onSearchChange: (val: string) => void;
  onRowClick?: (customerId: string) => void;
}

export default function CustomerTable({ 
  customers, 
  total, 
  page, 
  onPageChange, 
  searchTerm, 
  onSearchChange,
  onRowClick 
}: CustomerTableProps) {
  
  const [actingOn, setActingOn] = React.useState<string | null>(null);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
  };

  const getRiskColor = (prob: number) => {
    if (prob < 0.5) return 'bg-emerald-500';
    if (prob <= 0.75) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const handleAction = async (e: React.MouseEvent, customerId: string) => {
    e.stopPropagation();
    setActingOn(customerId);
    try {
      await triggerCampaign(customerId);
      // Optional: show a toast here
      alert(`Campaign triggered for ${customerId}`);
    } catch (err) {
      console.error(err);
      alert('Failed to trigger campaign');
    } finally {
      setActingOn(null);
    }
  };

  const itemsPerPage = 10;
  const totalPages = Math.ceil(total / itemsPerPage);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm p-8 border border-slate-100 dark:border-slate-800 overflow-hidden flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center">
            <Users className="w-5 h-5 text-indigo-600" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">At-Risk Customers</h2>
        </div>
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400 dark:text-slate-500 bg-slate-50 dark:bg-slate-950 px-3 py-1 rounded-full">{total} total</span>
      </div>

      <div className="mb-6 relative max-w-sm">
        <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500" />
        <input
          type="text"
          placeholder="Search by Customer ID..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pl-11 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all placeholder:text-slate-400 dark:text-slate-500"
        />
      </div>

      <div className="overflow-x-auto flex-1">
        <table className="w-full whitespace-nowrap">
          <thead>
            <tr className="text-left text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider border-b border-slate-100 dark:border-slate-800">
              <th className="pb-4 pl-4 pr-4">Customer ID</th>
              <th className="pb-4 px-4">Monthly Charges</th>
              <th className="pb-4 px-4">Churn Risk</th>
              <th className="pb-4 px-4">Confidence</th>
              <th className="pb-4 px-4">Top Drivers</th>
              <th className="pb-4 pr-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {customers.map((customer) => (
              <tr 
                key={customer.customer_id} 
                onClick={() => onRowClick && onRowClick(customer.customer_id)}
                className={`transition-colors ${onRowClick ? 'cursor-pointer hover:bg-slate-50 dark:bg-slate-950' : 'hover:bg-slate-50 dark:bg-slate-950'}`}
              >
                <td className="py-4 pl-4 pr-4 font-mono text-sm font-medium text-slate-900 dark:text-white">{customer.customer_id}</td>
                <td className="py-4 px-4 text-sm text-slate-600 dark:text-slate-400 dark:text-slate-500 font-medium">{formatCurrency(customer.monthly_charges)}</td>
                <td className="py-4 px-4">
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden w-24">
                      <div
                        className={`h-full rounded-full ${getRiskColor(customer.churn_probability)}`}
                        style={{ width: `${Math.round(customer.churn_probability * 100)}%` }}
                      />
                    </div>
                    <span className="text-sm font-bold text-slate-700 dark:text-slate-300">
                      {Math.round(customer.churn_probability * 100)}%
                    </span>
                  </div>
                </td>
                <td className="py-4 px-4 text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500 font-medium">
                  {Math.round(customer.lower_bound * 100)}% - {Math.round(customer.upper_bound * 100)}%
                </td>
                <td className="py-4 px-4">
                  <div className="flex flex-wrap gap-1.5">
                    {customer.top_drivers?.map((driver, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 dark:text-slate-500"
                      >
                        {driver}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="py-4 pr-4 text-right">
                  <button 
                    onClick={(e) => handleAction(e, customer.customer_id)}
                    disabled={actingOn === customer.customer_id}
                    className="inline-flex items-center justify-center p-2 rounded-lg bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors disabled:opacity-50"
                    title="Send Intervention Campaign"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
            {customers.length === 0 && (
              <tr>
                <td colSpan={6} className="py-12 text-center text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500 font-medium bg-slate-50 dark:bg-slate-950/50 rounded-xl mt-4">
                  No customers found matching your criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-6 pt-6 border-t border-slate-100 dark:border-slate-800">
        <button
          onClick={() => onPageChange(Math.max(1, page - 1))}
          disabled={page <= 1}
          className="px-4 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:bg-slate-950 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400 dark:text-slate-500">
          Page {page} {totalPages > 0 && `of ${totalPages}`}
        </span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={totalPages > 0 ? page >= totalPages : false}
          className="px-4 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:bg-slate-950 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
}
