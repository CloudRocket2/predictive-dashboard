with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Add useEffect import
if "useEffect" not in content:
    content = content.replace("import React, { useState } from 'react';", "import React, { useState, useEffect } from 'react';")

# Add the effect
effect_code = """
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);
"""

# Insert right after isDark definition
if effect_code not in content:
    content = content.replace("const [isDark, setIsDark] = useState(false);", f"const [isDark, setIsDark] = useState(false);\n{effect_code}")

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
