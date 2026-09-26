with open('src/app/globals.css', 'r') as f:
    content = f.read()

# Replace the custom variant with the correct one
content = content.replace('@custom-variant dark (&:is(.dark *));', '@custom-variant dark (&:where(.dark, .dark *));')

with open('src/app/globals.css', 'w') as f:
    f.write(content)
