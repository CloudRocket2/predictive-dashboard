with open('src/components/Sidebar.tsx', 'r') as f:
    content = f.read()

navItems = """const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'analytics', label: 'Cohort Analytics', icon: Users },
  { id: 'customers', label: 'Customers', icon: Users },
  { id: 'settings', label: 'Model Settings', icon: Settings },
];"""

# Wait, icon is 'Users' for both analytics and customers. Let's use 'BarChart2' or 'PieChart' for analytics.
# Oh, we need to import it.
content = content.replace("import { LayoutDashboard, Users, Settings, Shield, ChevronRight } from 'lucide-react';", "import { LayoutDashboard, Users, Settings, Shield, ChevronRight, PieChart } from 'lucide-react';")

new_nav = """const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'analytics', label: 'Cohort Analytics', icon: PieChart },
  { id: 'customers', label: 'Customers', icon: Users },
  { id: 'settings', label: 'Model Settings', icon: Settings },
];"""

import re
content = re.sub(r'const navItems = \[.*?\];', new_nav, content, flags=re.DOTALL)

with open('src/components/Sidebar.tsx', 'w') as f:
    f.write(content)
