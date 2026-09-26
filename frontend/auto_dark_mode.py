import os
import re

replacements = {
    r'\bbg-slate-50\b': 'bg-slate-50 dark:bg-slate-950',
    r'\bbg-white\b': 'bg-white dark:bg-slate-900',
    r'\btext-slate-900\b': 'text-slate-900 dark:text-white',
    r'\btext-slate-800\b': 'text-slate-800 dark:text-slate-100',
    r'\btext-slate-700\b': 'text-slate-700 dark:text-slate-300',
    r'\btext-slate-600\b': 'text-slate-600 dark:text-slate-400',
    r'\btext-slate-500\b': 'text-slate-500 dark:text-slate-400',
    r'\btext-slate-400\b': 'text-slate-400 dark:text-slate-500',
    r'\bborder-slate-100\b': 'border-slate-100 dark:border-slate-800',
    r'\bborder-slate-200\b': 'border-slate-200 dark:border-slate-700',
    r'\bbg-slate-100\b': 'bg-slate-100 dark:bg-slate-800',
    r'\bbg-slate-200\b': 'bg-slate-200 dark:bg-slate-700',
    r'\bhover:bg-slate-50\b': 'hover:bg-slate-50 dark:hover:bg-slate-800',
    r'\bhover:text-slate-600\b': 'hover:text-slate-600 dark:hover:text-slate-300',
    r'\bhover:text-slate-800\b': 'hover:text-slate-800 dark:hover:text-slate-200',
}

def process_file(filepath):
    with open(filepath, 'r') as f:
        original = f.read()
    
    content = original
    
    # Simple regex replace for each pattern if it doesn't already have dark: right next to it
    for old, new_val in replacements.items():
        # Negative lookahead to avoid replacing if we already added dark:
        pattern = old + r'(?!\s+dark:)'
        content = re.sub(pattern, new_val, content)

    # Some manual fixes for buttons where we want the inverse (e.g. bg-slate-900 text-white)
    # Actually wait, let's just let them be black in dark mode or change them to bg-white text-slate-900
    content = re.sub(r'\bbg-slate-900 text-white\b(?!\s+dark:)', 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900', content)

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.tsx'):
            process_file(os.path.join(root, file))
