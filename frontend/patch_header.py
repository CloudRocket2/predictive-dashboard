import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# The header is inside <main>. We need to replace it.
header_pattern = r'<header.*?</header>'
new_header = """<header className="bg-white/90 backdrop-blur-md px-6 md:px-12 py-6 flex items-center justify-between sticky top-0 z-30 rounded-t-[32px]">
          <h2 className="text-2xl font-bold text-slate-900 hidden sm:block">
            {activePage === 'dashboard' ? 'Revenue Analytics' : activePage.charAt(0).toUpperCase() + activePage.slice(1)}
          </h2>
          
          <div className="flex flex-1 sm:flex-none items-center justify-end gap-4 md:gap-6">
            <div className="relative max-w-md w-full sm:w-64">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search anything..."
                className="w-full bg-slate-50 text-sm font-medium text-slate-800 rounded-full pl-11 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-slate-200 transition-shadow"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <button className="w-10 h-10 flex items-center justify-center rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
              </button>
              <div className="hidden sm:flex items-center bg-slate-50 rounded-full p-1 gap-1">
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

content = re.sub(header_pattern, new_header, content, flags=re.DOTALL)

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
