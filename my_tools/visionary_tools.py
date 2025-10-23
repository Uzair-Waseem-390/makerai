from agents import function_tool
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
from typing import Dict, Any, List, Literal, Optional

# ==================== DATABASE SETUP ====================

DB_PATH = os.path.join(os.getcwd(), "visionary_agent_db.sqlite")

def init_db():
    """Initialize local SQLite database if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS startup_ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_name TEXT UNIQUE,
            description TEXT,
            domain TEXT,
            region TEXT,
            innovation_point TEXT,
            year INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# ==================== TOOL 1: web_search ====================

@function_tool
def web_search(query: str) -> str:
    """
    Perform a free web search using DuckDuckGo (no API key needed).
    Returns up to 5 relevant results with titles, links, and snippets.

    Args:
        query: The search query string.

    Returns:
        JSON string with success, query, results (list), and count.
    """
    import json
    
    print(f"Searching for: {query}")
    
    try:
        search_url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0"}
        payload = {"q": query}

        response = requests.post(search_url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.find_all("div", class_="result", limit=5):
            link_tag = result.find("a", class_="result__a")
            snippet_tag = result.find("a", class_="result__snippet")

            if link_tag and snippet_tag:
                results.append({
                    "title": link_tag.get_text(strip=True),
                    "link": link_tag["href"],
                    "snippet": snippet_tag.get_text(strip=True)
                })

        return json.dumps({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "query": query,
            "results": []
        })


# ==================== TOOL 2: data_base ====================

@function_tool
def data_base(
    action: Literal["search", "add", "list_domains"],
    keyword: str = "",
    domain: str = "",
    region: str = "",
    idea_name: str = "",
    description: str = "",
    innovation_point: str = "",
    year: int = 2025
) -> str:
    """
    Interact with the local startup ideas database.

    Args:
        action: One of 'search', 'add', 'list_domains'
        keyword: (search) Keyword to match in idea name/description
        domain: (search/add) Filter by or set domain
        region: (search/add) Filter by or set region
        idea_name: (add) Name of the startup idea
        description: (add) Description of the idea
        innovation_point: (add) Key innovation point
        year: (add) Year of the idea

    Returns:
        JSON string with success, action, and results.
    """
    import json
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"DateBase is called for action: {action}")
    # print(f"DateBase is called for keyword: {keyword}")
    # print(f"DateBase is called for domain: {domain}")
    # print(f"DateBase is called for region: {region}")
    # print(f"DateBase is called for idea_name: {idea_name}")
    # print(f"DateBase is called for description: {description}")
    # print(f"DateBase is called for innovation_point: {innovation_point}")
    # print(f"DateBase is called for year: {year}")

    try:
        if action == "search":
            query = "SELECT idea_name, description, domain, region FROM startup_ideas WHERE 1=1"
            params = []

            if keyword:
                query += " AND (LOWER(idea_name) LIKE ? OR LOWER(description) LIKE ?)"
                params.extend([f"%{keyword.lower()}%", f"%{keyword.lower()}%"])
            if domain:
                query += " AND domain = ?"
                params.append(domain)
            if region:
                query += " AND region = ?"
                params.append(region)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = [
                {"idea_name": r[0], "description": r[1], "domain": r[2], "region": r[3]}
                for r in rows
            ]

            return json.dumps({"success": True, "action": "search", "matches": results, "count": len(results)})

        elif action == "add":
            if not idea_name:
                return json.dumps({"success": False, "error": "idea_name is required for add action"})

            cursor.execute('''
                INSERT OR IGNORE INTO startup_ideas 
                (idea_name, description, domain, region, innovation_point, year)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                idea_name,
                description,
                domain,
                region,
                innovation_point,
                year
            ))
            conn.commit()

            return json.dumps({
                "success": True,
                "action": "add",
                "idea_name": idea_name,
                "status": "added" if cursor.rowcount > 0 else "already_exists"
            })

        elif action == "list_domains":
            cursor.execute("SELECT DISTINCT domain FROM startup_ideas WHERE domain IS NOT NULL")
            domains = [row[0] for row in cursor.fetchall()]
            return json.dumps({"success": True, "action": "list_domains", "domains": domains})

        else:
            return json.dumps({"success": False, "error": f"Unknown action: {action}"})

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
    finally:
        conn.close()