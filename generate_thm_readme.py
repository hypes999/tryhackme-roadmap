#!/usr/bin/env python3
# generate_thm_readme.py
"""
Gera README.md com rooms completadas do TryHackMe a partir do perfil público.
Uso: python generate_thm_readme.py <username> [--outfile README.md]
"""

import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import argparse
import time

THM_BASE = "https://tryhackme.com"

def fetch_profile(username):
    url = f"{THM_BASE}/profile/{username}"
    headers = {
        "User-Agent": "thm-readme-generator/1.0 (+https://github.com/yourname)"
    }
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text

def parse_rooms(html):
    soup = BeautifulSoup(html, "html.parser")
    rooms = []

    # Estratégia genérica: procurar links para /room/ dentro do conteúdo de profile/rooms
    # O layout pode mudar; se não apareceres nada, inspeciona a página e ajusta este selector.
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/room/"):
            title = a.get_text(strip=True)
            link = THM_BASE + href
            # evitar duplicados
            if any(r["link"] == link for r in rooms):
                continue
            rooms.append({"title": title or href.split("/")[-1], "link": link})
    return rooms

def render_markdown(username, rooms):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# TryHackMe — Rooms completadas por `{username}`",
        "",
        f"_Última atualização: {now}_",
        "",
        "## Rooms",
        ""
    ]
    if not rooms:
        lines.append("_Nenhuma room encontrada — verifica se o perfil é público ou se o HTML mudou._")
    else:
        for r in rooms:
            lines.append(f"- [{r['title']}]({r['link']})")
    lines.append("")
    lines.append("---")
    lines.append("Gerado automaticamente por `generate_thm_readme.py`.")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="TryHackMe username")
    parser.add_argument("--outfile", default="README.md", help="Ficheiro de saída")
    args = parser.parse_args()

    html = fetch_profile(args.username)
    rooms = parse_rooms(html)

    # optionally sort alphabetically
    rooms = sorted(rooms, key=lambda x: x["title"].lower())

    md = render_markdown(args.username, rooms)
    with open(args.outfile, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {len(rooms)} rooms to {args.outfile}")

if __name__ == "__main__":
    main()
