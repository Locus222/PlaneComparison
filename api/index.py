"""
api/index.py – vstupní bod pro Vercel serverless nasazení.
Importuje Flask aplikaci z kořenového app.py.
"""
import sys
import os

# Přidáme kořenový adresář projektu do sys.path,
# aby bylo možné importovat app.py a ostatní moduly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel očekává WSGI callable s názvem 'app' nebo 'handler'
# Stačí exportovat app – @vercel/python to rozpozná automaticky.

