with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Add states
if "const [retrainProgress" not in content:
    content = content.replace(
        "const [retrainResult, setRetrainResult] = useState<RetrainResponse | null>(null);",
        "const [retrainResult, setRetrainResult] = useState<RetrainResponse | null>(null);\n  const [retrainProgress, setRetrainProgress] = useState(0);\n  const [isDark, setIsDark] = useState(false);"
    )

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
