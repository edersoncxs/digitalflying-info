"""Resolve uma única Release para todos os ambientes da execução."""
import json
import os
import re
import urllib.parse
import urllib.request

repo = os.environ['GITHUB_REPOSITORY']
tag = os.environ.get('INPUT_TAG', '').strip()
if tag and not re.fullmatch(r'v\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?', tag):
    raise SystemExit('Informe uma tag de versão, por exemplo v1.0.2')
rota = '/tags/' + urllib.parse.quote(tag, safe='') if tag else '/latest'
headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'DF-Delivery-testes'}
if os.environ.get('GITHUB_TOKEN'):
    headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
req = urllib.request.Request(f'https://api.github.com/repos/{repo}/releases{rota}', headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    release = json.load(resp)
if release['draft']:
    raise SystemExit('Os testes esperam uma Release publicada')
esperados = {'df-delivery_amd64.deb', 'df-delivery.x86_64.rpm', 'df-delivery_x64-setup.exe'}
if not esperados.issubset({a['name'] for a in release['assets']}):
    raise SystemExit('A Release não contém os três instaladores')
tag = release['tag_name']
base = f'https://github.com/{repo}/releases/download/{urllib.parse.quote(tag, safe="")}'
with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
    f.write(f'tag={tag}\nbase={base}\n')
print(f'Todos os ambientes testarão a mesma Release: {tag}')
