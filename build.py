"""Build index.html (standalone, for hosting) from site.html (source)."""
DESC="Oneering builds, improves and runs production software. AI agents do the work, a named engineer is accountable, and nothing ships until an independent check passes."
s=open('site.html',encoding='utf-8').read()
head=f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="canonical" href="https://oneering.com/">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<meta property="og:type" content="website">
<meta property="og:url" content="https://oneering.com/">
<meta property="og:title" content="Oneering | Engineering after Agile">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="https://oneering.com/og.png">
<meta name="twitter:card" content="summary_large_image">
<style>body{{margin:0}}[hidden]{{display:none!important}}img{{max-width:100%}}</style>
'''
s=s.replace('<title>Oneering</title>','<title>Oneering | Engineering after Agile</title>')
s=s.replace('content="Oneering runs software engineering on a process designed for AI to execute. Engineering after Agile."',f'content="{DESC}"')
open('index.html','w',encoding='utf-8').write(head+s+'\n</body>\n</html>\n')
