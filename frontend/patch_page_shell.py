import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Replace root div
content = content.replace('<div className="flex h-screen bg-slate-50">', '<div className="flex h-screen bg-slate-50 p-2 sm:p-4 overflow-hidden">')

# Add missing imports for Header (Moon, Sun, Search, Bell)
imports = """import { Moon, Sun, Bell } from 'lucide-react';
"""
if "import { Moon, Sun" not in content:
    content = content.replace("import { PieChart,", imports + "import { PieChart,")

# Replace main wrapper
content = content.replace('<main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-50 pt-24 md:pl-64">', '<main className="flex-1 bg-white rounded-[32px] shadow-sm border border-slate-200 overflow-x-hidden overflow-y-auto relative z-0 ml-0 md:ml-64 flex flex-col">\n        <div className="pt-24 pb-8 px-6 md:px-12 w-full flex-1">')
# Close the div we just opened inside the main
content = content.replace('</main>', '</div>\n        </main>')


# Replace Header
header_search = r'<header className="fixed top-0 right-0 left-0 md:left-64 bg-slate-50/80.*?</header>'
new_header = """<header className="fixed top-4 right-4 left-4 md:left-[270px] bg-white/80 backdrop-blur-md z-30 flex items-center justify-between px-6 md:px-12 py-4 rounded-[24px]">
          <h2 className="text-xl font-bold text-slate-800 capitalize hidden sm:block">
            {activePage === 'dashboard' ? 'Revenue Analytics' : activePage}
          </h2>
          
          <div className="flex flex-1 sm:flex-none items-center justify-end gap-4 md:gap-6">
            <div className="relative max-w-md w-full sm:w-64">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search anything..."
                className="w-full bg-slate-100 text-sm font-medium text-slate-800 rounded-full pl-11 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-slate-200 transition-shadow"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <button className="w-10 h-10 flex items-center justify-center rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
              </button>
              <div className="hidden sm:flex items-center bg-slate-100 rounded-full p-1 gap-1">
                <button className="w-8 h-8 flex items-center justify-center rounded-full text-slate-400 hover:text-slate-600 transition-colors">
                  <Moon className="w-4 h-4" />
                </button>
                <button className="w-8 h-8 flex items-center justify-center rounded-full bg-white text-slate-800 shadow-sm transition-colors">
                  <Sun className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden cursor-pointer border border-slate-200 flex-shrink-0">
              <img src="https://i.pravatar.cc/150?u=a042581f4e29026704d" alt="Profile" className="w-full h-full object-cover" />
            </div>
          </div>
        </header>"""
content = re.sub(header_search, new_header, content, flags=re.DOTALL)


with open('src/app/page.tsx', 'w') as f:
    f.write(content)
