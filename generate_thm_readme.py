#!/usr/bin/env python3
"""
Gera README.md com as rooms completadas no TryHackMe.

Compatível com o endpoint atual:
https://tryhackme.com/api/all-completed-rooms?username=<USERNAME>

Uso:
    python generate_thm_readme.py <username> [--outfile README.md]

Opcional (para perfis privados):
    THM_SESSION=<cookie_session> python generate_thm_readme.py <username>
"""

import requests
import argparse
import os
from datetime import datetime, timezone

USER_AGENT = "thm-readme-generator/3.0 (+https://github.com/hypes999)"

def fetch_completed_rooms(username, session_cookie=None):
    """Obtém a lista de rooms completadas do TryHackMe"""
    url = f"https://tryhackme.com/api/all-completed-rooms?username={username}&limit=200&page=1"
    headers = {"User-Agent": USER_AGENT}
    if session_cookie:
        headers["Cookie"] = f"session={session_cookie}"
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()

    data = r.json()
    # Endpoint pode devolver lista diretamente ou dentro de uma key
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("rooms") or data.get("data") or data.get("completedRooms") or []
    else:
        items = []

    rooms = []
    for r in items:
        title = r.get("title") or r.get("name") or r.get("room_title") or "Unknown"
        code = r.get("code") or r.get("roomCode") or r.get("slug") or ""
        date = r.get("date_completed") or r.get("completedDate") or r.get("date")
        rooms.append({
            "title": title.strip(),
            "link": f"https://tryhackme.com/room/{code}",
            "date": date
        })
    return rooms

def render_markdown(username, rooms):
    """Gera o conteúdo Markdown do README"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# TryHackMe — Rooms completadas por `{username}`",
        "",
        f"_Última atualização: {now}_",
        "",
        "## Rooms",
        "",
    ]

    if not rooms:
        lines.append("_Nenhuma room encontrada — verifica se o perfil é público ou se há erro no endpoint._")
    else:
        for r in sorted(rooms, key=lambda x: x["title"].lower()):
            date = f" — {r['date'][:10]}" if r.get("date") else ""
            lines.append(f"- [{r['title']}]({r['link']}){date}")

    lines += ["", "---", "Gerado automaticamente por `generate_thm_readme.py`."]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="TryHackMe username")
    parser.add_argument("--outfile", default="README.md", help="Ficheiro de saída")
    args = parser.parse_args()

    session_cookie = os.environ.get("THM_SESSION")

    try:
        rooms = fetch_completed_rooms(args.username, session_cookie)
    except Exception as e:
        print(f"❌ Erro ao obter dados: {e}")
        return

    md = render_markdown(args.username, rooms)
    with open(args.outfile, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ {len(rooms)} rooms escritas em {args.outfile}")

if __name__ == "__main__":
    main()
