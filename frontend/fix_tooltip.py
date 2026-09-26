import re
with open('src/components/CustomerProfileModal.tsx', 'r') as f:
    content = f.read()

content = content.replace("formatter={(value: number) => [value > 0 ? `+${value.toFixed(3)}` : value.toFixed(3), 'Impact']}", "formatter={(value: any) => [value > 0 ? `+${Number(value).toFixed(3)}` : Number(value).toFixed(3), 'Impact']}")

with open('src/components/CustomerProfileModal.tsx', 'w') as f:
    f.write(content)
