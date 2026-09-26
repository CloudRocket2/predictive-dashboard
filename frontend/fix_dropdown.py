import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Remove the buggy useEffect
buggy_use_effect = """  // Close dropdowns on outside click roughly
  useEffect(() => {
    const closeDropdowns = () => { setProfileOpen(false); setNotifOpen(false); };
    document.addEventListener('click', closeDropdowns);
    return () => document.removeEventListener('click', closeDropdowns);
  }, []);"""

content = content.replace(buggy_use_effect, """  // Added a simpler approach: a full screen invisible overlay when dropdown is open
  const closeDropdowns = () => { setProfileOpen(false); setNotifOpen(false); };""")

# Add the overlay next to the header
header_start = "{/* Universal Header */}"
overlay_div = """{(profileOpen || notifOpen) && (
          <div className="fixed inset-0 z-20" onClick={closeDropdowns} />
        )}"""

content = content.replace("{/* Universal Header */}", overlay_div + "\n        {/* Universal Header */}")

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
