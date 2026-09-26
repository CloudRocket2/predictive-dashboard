import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Add isDark state
if "const [isDark, setIsDark] = useState(false);" not in content:
    content = content.replace("const [retrainProgress, setRetrainProgress] = useState(0);", "const [retrainProgress, setRetrainProgress] = useState(0);\n  const [isDark, setIsDark] = useState(false);")

# Update the wrapper div
# Find: <div className="flex h-screen bg-slate-50 dark:bg-slate-950 p-2 sm:p-4 overflow-hidden relative">
# We need to add ${isDark ? 'dark' : ''}
wrapper_pattern = r'<div className="flex h-screen bg-slate-50 dark:bg-slate-950 p-2 sm:p-4 overflow-hidden relative">'
if wrapper_pattern in content:
    content = content.replace(wrapper_pattern, '<div className={`flex h-screen bg-slate-50 dark:bg-slate-950 p-2 sm:p-4 overflow-hidden relative ${isDark ? "dark" : ""}`}>')

# Wire up Sun and Moon buttons
old_toggles = """<button className="w-8 h-8 flex items-center justify-center rounded-full text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
                  <Moon className="w-4 h-4" />
                </button>
                <button className="w-8 h-8 flex items-center justify-center rounded-full bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 shadow-sm transition-colors">
                  <Sun className="w-4 h-4" />
                </button>"""

# If already transformed by auto_dark_mode, we can just replace the whole toggle block
old_block = re.search(r'<div className="hidden sm:flex items-center bg-slate-50 dark:bg-slate-950 rounded-full p-1 gap-1">.*?</div>', content, re.DOTALL)
if old_block:
    new_block = """<div className="hidden sm:flex items-center bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-full p-1 gap-1">
                <button 
                  onClick={() => setIsDark(true)}
                  className={`w-8 h-8 flex items-center justify-center rounded-full transition-colors ${isDark ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'}`}>
                  <Moon className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => setIsDark(false)}
                  className={`w-8 h-8 flex items-center justify-center rounded-full transition-colors ${!isDark ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'}`}>
                  <Sun className="w-4 h-4" />
                </button>
              </div>"""
    content = content[:old_block.start()] + new_block + content[old_block.end():]

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
