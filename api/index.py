import sys
import os

# No Vercel, o arquivo fica em /var/task/api/index.py
# O diretório raiz do projeto é um nível acima
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

from app import create_app

app = create_app()

# Vercel espera um callable chamado `app` ou `handler`
# Flask app já é um WSGI callable
