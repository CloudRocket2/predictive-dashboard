import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

old_scatter = """<ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                 <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                 <XAxis type="number" dataKey="churn_probability" name="Churn Risk" domain={[0, 1]} tick={{fill: '#64748b'}} />
                 <YAxis type="number" dataKey="monthly_charges" name="MRR ($)" tick={{fill: '#64748b'}} />
                 <Tooltip cursor={{strokeDasharray: '3 3'}} contentStyle={{borderRadius: '12px'}} />
                 <Scatter name="Customers" data={segData.value_matrix} fill="#6366f1" />
               </ScatterChart>"""

new_scatter = """<ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
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
                   formatter={(value: any, name: string) => {
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
               </ScatterChart>"""

content = content.replace(old_scatter, new_scatter)

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
