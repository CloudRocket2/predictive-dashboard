import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Add imports
imports = """import CustomerProfileModal from '@/components/CustomerProfileModal';
import { fetchSegmentation } from '@/lib/api';
import { PieChart, Pie, ScatterChart, Scatter, ZAxis, CartesianGrid } from 'recharts';
"""
content = content.replace("import CustomerTable from '@/components/CustomerTable';", "import CustomerTable from '@/components/CustomerTable';\n" + imports)

# Add sidebar item
# The sidebar is an external component! 
# Let's check if Sidebar.tsx needs to be updated too. We'll do that separately.

# Add state for selected customer
state_vars = """
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  
  // Segmentation data
  const { data: segData } = useSWR(activePage === 'analytics' ? 'segmentation' : null, fetchSegmentation);
"""
content = content.replace("const [simResult, setSimResult]", state_vars + "\n  const [simResult, setSimResult]")


# Add AnalyticsView
analytics_view = """
  const renderAnalytics = () => (
    <div className="space-y-6 max-w-6xl">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Cohort Analytics</h1>
      
      {!segData ? (
        <div className="flex items-center justify-center py-20"><RefreshCw className="w-8 h-8 text-indigo-600 animate-spin" /></div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
               <h3 className="font-bold text-slate-900 mb-4">Risk by Contract</h3>
               <div className="space-y-4">
                 {segData.contract_risk.map(c => (
                   <div key={c.segment}>
                     <div className="flex justify-between text-sm mb-1"><span className="font-medium text-slate-700">{c.segment}</span><span className="font-bold text-slate-900">{Math.round(c.avg_risk*100)}%</span></div>
                     <div className="h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-indigo-500 rounded-full" style={{width: `${c.avg_risk*100}%`}}></div></div>
                   </div>
                 ))}
               </div>
            </div>
            <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
               <h3 className="font-bold text-slate-900 mb-4">Risk by Internet</h3>
               <div className="space-y-4">
                 {segData.internet_risk.map(c => (
                   <div key={c.segment}>
                     <div className="flex justify-between text-sm mb-1"><span className="font-medium text-slate-700">{c.segment}</span><span className="font-bold text-slate-900">{Math.round(c.avg_risk*100)}%</span></div>
                     <div className="h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-rose-500 rounded-full" style={{width: `${c.avg_risk*100}%`}}></div></div>
                   </div>
                 ))}
               </div>
            </div>
            <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
               <h3 className="font-bold text-slate-900 mb-4">Risk by Payment</h3>
               <div className="space-y-4">
                 {segData.payment_risk.map(c => (
                   <div key={c.segment}>
                     <div className="flex justify-between text-sm mb-1"><span className="font-medium text-slate-700">{c.segment}</span><span className="font-bold text-slate-900">{Math.round(c.avg_risk*100)}%</span></div>
                     <div className="h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-emerald-500 rounded-full" style={{width: `${c.avg_risk*100}%`}}></div></div>
                   </div>
                 ))}
               </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 h-[400px]">
             <h3 className="font-bold text-slate-900 mb-1">Value Matrix (Sample)</h3>
             <p className="text-xs font-medium text-slate-500 mb-6">Top right quadrant = High Value, High Risk. Target immediately.</p>
             <ResponsiveContainer width="100%" height="100%">
               <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                 <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                 <XAxis type="number" dataKey="churn_probability" name="Churn Risk" domain={[0, 1]} tick={{fill: '#64748b'}} />
                 <YAxis type="number" dataKey="monthly_charges" name="MRR ($)" tick={{fill: '#64748b'}} />
                 <Tooltip cursor={{strokeDasharray: '3 3'}} contentStyle={{borderRadius: '12px'}} />
                 <Scatter name="Customers" data={segData.value_matrix} fill="#6366f1" />
               </ScatterChart>
             </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
"""
content = content.replace("const renderDashboard = () => (", analytics_view + "\n  const renderDashboard = () => (")

# Update render logic
content = content.replace("{activePage === 'dashboard' && renderDashboard()}", "{activePage === 'dashboard' && renderDashboard()}\n          {activePage === 'analytics' && renderAnalytics()}")

# Update CustomerTable onRowClick
content = content.replace("onSearchChange={(val) => {\n          setSearchTerm(val);\n          setCustomerPage(1);\n        }}", "onSearchChange={(val) => {\n          setSearchTerm(val);\n          setCustomerPage(1);\n        }}\n        onRowClick={(id) => setSelectedCustomerId(id)}")

content = content.replace("onSearchChange={(val) => {\n                  setSearchTerm(val);\n                  setCustomerPage(1);\n                }}", "onSearchChange={(val) => {\n                  setSearchTerm(val);\n                  setCustomerPage(1);\n                }}\n                onRowClick={(id) => setSelectedCustomerId(id)}")


# Add the modal to the very end of the component
modal_code = """
        </main>
      </div>
      {selectedCustomerId && (
        <CustomerProfileModal customerId={selectedCustomerId} onClose={() => setSelectedCustomerId(null)} />
      )}
    </div>
  );
"""
content = content.replace("</main>\n      </div>\n    </div>\n  );", modal_code)

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
