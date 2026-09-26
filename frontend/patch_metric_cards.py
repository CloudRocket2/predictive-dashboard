import re

with open('src/components/MetricCards.tsx', 'r') as f:
    content = f.read()

# Add useState
if "import React, { useState } from 'react';" not in content:
    content = content.replace("import React from 'react';", "import React, { useState } from 'react';")

# Add state to component
state_code = """
  const [timeRange, setTimeRange] = useState('Month');

  // Multipliers to mock data changing based on time range
  const multiplier = timeRange === 'Days' ? 0.03 : timeRange === 'Week' ? 0.25 : 1;
"""
content = re.sub(r'export default function MetricCards\([^)]+\) \{', r'\g<0>' + state_code, content)

# Apply multiplier to metrics
content = content.replace("value: formatK(totalRevenue),", "value: formatK(totalRevenue * multiplier),")
content = content.replace("value: formatK(totalRevenue * 0.25),", "value: formatK(totalRevenue * 0.25 * multiplier),")
content = content.replace("trend: -13.8,", "trend: timeRange === 'Month' ? -13.8 : timeRange === 'Week' ? 4.2 : -2.1,")
content = content.replace("trend: 21.8,", "trend: timeRange === 'Month' ? 21.8 : timeRange === 'Week' ? 12.4 : 5.6,")

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

with open('src/components/MetricCards.tsx', 'w') as f:
    f.write(content)
