import re

with open('src/components/RevenueAreaChart.tsx', 'r') as f:
    content = f.read()

# Add useState
if "import React, { useState } from 'react';" not in content:
    content = content.replace("import React from 'react';", "import React, { useState } from 'react';")

# Add state to component
state_code = """
  const [timeRange, setTimeRange] = useState('Month');
"""
content = re.sub(r'export default function RevenueAreaChart\([^)]+\) \{', r'\g<0>' + state_code, content)

# Modify data generation to be dependent on timeRange
old_data_gen = """const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];
  
  // Interpolate 6 data points into ~30 points for a smooth curve to match design
  const data = [];
  let baseVal = 50000;
  for (let i = 0; i < 30; i++) {
    // Generate a wiggly upward trend
    baseVal = baseVal + (Math.random() * 20000 - 5000) + (i * 2000);
    const monthIdx = Math.floor(i / (30 / months.length));
    data.push({
      name: months[Math.min(monthIdx, months.length - 1)],
      value: Math.floor(baseVal),
      fullDate: `${Math.floor((i % 30) + 1)} ${months[Math.min(monthIdx, months.length - 1)]} 2026`
    });
  }"""

new_data_gen = """const timeLabels = {
    Days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    Week: ['W1', 'W2', 'W3', 'W4'],
    Month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
  }[timeRange];
  
  const numPoints = timeRange === 'Days' ? 7 : timeRange === 'Week' ? 28 : 30;
  const baseMultiplier = timeRange === 'Days' ? 0.05 : timeRange === 'Week' ? 0.2 : 1;
  
  const data = [];
  let baseVal = 50000 * baseMultiplier;
  for (let i = 0; i < numPoints; i++) {
    baseVal = baseVal + (Math.random() * (20000 * baseMultiplier) - (5000 * baseMultiplier)) + (i * (2000 * baseMultiplier));
    const labelIdx = Math.floor(i / (numPoints / timeLabels.length));
    data.push({
      name: timeLabels[Math.min(labelIdx, timeLabels.length - 1)],
      value: Math.floor(baseVal),
      fullDate: timeRange === 'Month' ? `${Math.floor((i % 30) + 1)} ${timeLabels[Math.min(labelIdx, timeLabels.length - 1)]} 2026` : `${timeLabels[Math.min(labelIdx, timeLabels.length - 1)]}`
    });
  }"""

content = content.replace(old_data_gen, new_data_gen)

# Replace the static buttons
old_buttons = """<button className="px-4 py-1.5 text-xs font-semibold rounded-full text-slate-500 hover:text-slate-800 transition-colors">Days</button>
          <button className="px-4 py-1.5 text-xs font-semibold rounded-full text-slate-500 hover:text-slate-800 transition-colors">Week</button>
          <button className="px-4 py-1.5 text-xs font-semibold rounded-full bg-slate-900 text-white shadow-sm transition-colors">Month</button>"""

new_buttons = """{['Days', 'Week', 'Month'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-colors ${
                timeRange === range
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              {range}
            </button>
          ))}"""

content = content.replace(old_buttons, new_buttons)

with open('src/components/RevenueAreaChart.tsx', 'w') as f:
    f.write(content)
