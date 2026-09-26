with open('src/app/layout.tsx', 'r') as f:
    content = f.read()

content = content.replace('import { Inter } from "next/font/google";', 'import { IBM_Plex_Sans } from "next/font/google";')
content = content.replace('const inter = Inter({', 'const font = IBM_Plex_Sans({\n  weight: ["300", "400", "500", "600", "700"],')
content = content.replace('variable: "--font-inter",', 'variable: "--font-plex",')
content = content.replace('${inter.variable}', '${font.variable}')

with open('src/app/layout.tsx', 'w') as f:
    f.write(content)

with open('tailwind.config.ts', 'w') as f:
    # Just in case they had tailwind v3 config, wait, there is no tailwind.config.ts.
    pass

# Update globals.css to set font family
with open('src/app/globals.css', 'r') as f:
    css = f.read()

if "font-family" not in css:
    css += "\n\n@theme {\n  --font-sans: var(--font-plex), ui-sans-serif, system-ui, sans-serif;\n}\n"
    with open('src/app/globals.css', 'w') as f:
        f.write(css)

