import re

with open('src/components/RiskDonutChart.tsx', 'r') as f:
    content = f.read()

# Replace innerRadius and outerRadius with fixed values
content = content.replace('innerRadius="75%"', 'innerRadius={120}')
content = content.replace('outerRadius="95%"', 'outerRadius={150}')

# Move the text up slightly because it was pushed down
content = content.replace('className="absolute bottom-0 left-0 right-0 flex flex-col items-center justify-end pb-2"', 'className="absolute bottom-2 left-0 right-0 flex flex-col items-center justify-end pb-2"')

with open('src/components/RiskDonutChart.tsx', 'w') as f:
    f.write(content)
