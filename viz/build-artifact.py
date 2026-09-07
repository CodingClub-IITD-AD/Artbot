#!/usr/bin/env python3
"""Generate the shareable Artifact build from the standalone mockup.

mockup.html is a complete document (opens straight off disk, three.js vendored
next to it). Artifacts supply their own doctype/head/body and can only load
scripts from an allowlisted CDN, so this strips the shell and points three.js
at cdnjs. One source, two targets - do not hand-edit the output.
"""
import re, sys, pathlib

src = pathlib.Path("mockup.html").read_text()
out = src

# 1. drop the document shell - the artifact wrapper provides it
for tag in ['<!doctype html>', '<html lang="en">', '<head>', '</head>',
            '<body>', '</body>', '</html>',
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">']:
    out = out.replace(tag + "\n", "").replace(tag, "")

# 2. three.js must come from the allowlisted CDN; there is no sibling file there
local = '''<script src="three.min.js"></script>
<script>
  // If the local copy is missing, fall back to the CDN synchronously.
  if (typeof THREE === "undefined") {
    document.write('<scr' + 'ipt src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"><\\/scr' + 'ipt>');
  }
</script>'''
cdn = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
if local not in out:
    sys.exit("ERROR: script block not found - did mockup.html change shape?")
out = out.replace(local, cdn, 1)

out = re.sub(r'\n{3,}', '\n\n', out).lstrip()
pathlib.Path("mockup.artifact.html").write_text(out)

# sanity
bad = [t for t in ('<!doctype', '<html', '<head>', '<body>') if t in out.lower()]
if bad:
    sys.exit("ERROR: document shell survived: " + ", ".join(bad))
if 'src="three.min.js"' in out:
    sys.exit("ERROR: still pointing at the local three.js")
print("built mockup.artifact.html  (%d KB)" % (len(out)//1024))
