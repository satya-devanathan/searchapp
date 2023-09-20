from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict
import requests
import urllib
import httpx
queries = defaultdict(dict)

browser = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
browser += " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
API_KEY = "AIzaSyBjNSYWnabAK1Cke_w0qCAW2mkXGcRYUOc&cx=03bdb93ff93b54780"
HEADER = {
        "User-Agent": browser
    }


def tasks_list_html():
    try:
        html = "<table border=1 cellspacing=5 cellpadding=5>"
        html += "<tr>"
        html += "<th>search_string</th>"
        html += "<th>status</th>"
        html += "<th>requested_datetime</th>"
        html += "<th>completed_datetime</th>"
        html += "<th>lastupdated_datetime</th>"
        html += "</tr>"
        for key in queries:
            query = queries[key]
            task_status = query.get('status', None)
            anchor_string = f"<a href='/results/?q={key}' target='_blank'>{key}</a>"
            search_string = anchor_string if task_status == "Completed" else key

            requested_datetime = query.get('requested_datetime', "")
            completed_datetime = query.get('completed_datetime', "")
            lastupdated_datetime = query.get('lastupdated_datetime', "")

            html += "<tr>"
            html += f"<td>{search_string}</td><td>{task_status}</td>"
            html += f"<td>{requested_datetime}</td><td>{completed_datetime}</td><td>{lastupdated_datetime}</td>"
            html += "</tr>"
        html += "</table>"
        return html
    except Exception as ex:
        print(f"ERROR{ex}")


def result_html(search_string, results):
    try:
        status = results.get('status', "")
        requested_datetime = results.get('requested_datetime', "")
        completed_datetime = results.get("completed_datetime", "")
        lastupdated_datetime = results.get("lastupdated_datetime", "")

        search_results = results['results']
        # print(search_results.keys())

        html = "<html><body align=center>"
        html += "<table border=1 cellspacing=5 cellpadding=5>"
        html += "<tr>"
        html += "<th>search_string</th>"
        html += "<th>status</th>"
        html += "<th>requested_datetime</th>"
        html += "<th>completed_datetime</th>"
        html += "<th>lastupdated_datetime</th>"
        html += "</tr>"
        html += "<tr>"
        html += f"<td>{search_string}</td>"
        html += f"<td>{status}</td>"
        html += f"<td>{requested_datetime}</td>"
        html += f"<td>{completed_datetime}</td>"
        html += f"<td>{lastupdated_datetime}</td>"
        html += "</tr>"

        google_result = search_results.get('google', "")
        google_table_html = "<table border=1 cellspacing=5 valign='top'>"
        google_table_html += "<tr><th>Google</th></tr>"
        if len(google_result) != 0:
            for google in google_result:
                google_table_html += "<tr>"
                google_table_html += f"<td nowrap><a href='{google['url']}' target='_blank'>{google['title']}</a></td>"
                google_table_html += "</tr>"
        google_table_html += "</table>"

        duckduckgo_result = search_results.get('duckduckgo', "")
        duckduckgo_table_html = "<table border=1 cellspacing=5 valign='top'>"
        duckduckgo_table_html += "<tr><th>DuckDuckGo</th></tr>"
        if len(duckduckgo_result) != 0:
            for idx, duckduckgo in enumerate(duckduckgo_result):
                if idx < 10:
                    duckduckgo_table_html += "<tr>"
                    duckduckgo_table_html += f"<td nowrap><a href='{duckduckgo['url']}' target='_blank'>{duckduckgo['title']}</a></td>"
                    duckduckgo_table_html += "</tr>"
                else:
                    break
        duckduckgo_table_html += "</table>"

        wikipedia_result = search_results.get('wikipedia', "")
        wikipedia_table_html = "<table border=1 cellspacing=5 valign='top'>"
        wikipedia_table_html += "<tr><th>Wikipedia</th></tr>"
        if len(wikipedia_result) != 0:
            for wikipedia in wikipedia_result:
                wikipedia_table_html += "<tr>"
                wikipedia_table_html += f"<td>{wikipedia}</td>"
                wikipedia_table_html += "</tr>"
        wikipedia_table_html += "</table>"

        results_html_table = "<table>"
        results_html_table += f"<tr><td colspan=2 align=center>{wikipedia_table_html}</td></tr>"
        results_html_table += "<tr>"
        results_html_table += f"<td align=center>{google_table_html}</td>"
        results_html_table += f"<td align=center>{duckduckgo_table_html}</td>"
        results_html_table += "</tr>"
        results_html_table += "</table>"

        html += f"<tr><td colspan=5>{results_html_table}</td></tr>"
        html += "</body></html>"
        return html
    except Exception as ex:
        print(f"function: result_html, ERROR{ex}")


async def fetch_google(search_string: str) -> list:

    result = []
    api_url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&q={search_string}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=HEADER)
            content = response.json()
            print(f"Content: {content}")
            for item in content.get('items', []):
                result.append({"title": item.get("title"), "url": item.get("link")})
            queries[search_string]["results"]["google"] = result
        return result
    except Exception as ex:
        print(f"function: fetch_google, ERROR{ex}")


async def fetch_duckduckgo(search_string) -> list:
    result = []
    api_url = f"https://html.duckduckgo.com/html/?q={search_string}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=HEADER)
            content = response.text
            print(f"Content: {response}")
            soup = BeautifulSoup(content, "html.parser")

            for a_tag in soup.find_all("a", {"class": "result__a"}):
                href = a_tag.get("href")
                # print(href)
                href = href.replace("//duckduckgo.com/l/?uddg=", "")
                # print("before processing", href)
                if not href.strip().startswith("http"):
                    href = "https" + href
                href = urllib.parse.unquote_plus(href)
                href = href[0:href.find("&")] if href.find("&") > 0 else href

                result.append({"title": a_tag.text, "url": href})
            queries[search_string]["results"]["duckduckgo"] = result
        return result
    except Exception as ex:
        print(f"function: fetch_duckduckgo, ERROR{ex}")


async def fetch_wikipedia(search_string: str) -> list:
    # Fetch data from Wikipedia (can be refined to get more specific data)
    try:
        api_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={search_string}&limit=10&namespace=0&format=json"
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            contents = response.json()
            # ensure list is not empty
            first_resp_link = contents[-1][1]
            response = await client.get(first_resp_link, headers=HEADER)
            html_content = response.text

            soup = BeautifulSoup(html_content, "html.parser")
            all_p = soup.find_all("p")
            rel_p_tags = all_p[0:3]
            paragraphs = [p.text for p in rel_p_tags if p]
            queries[search_string]["results"]["wikipedia"] = paragraphs
            return paragraphs
    except Exception as ex:
        print(f"function: fetch_wikipedia, ERROR{ex}")


async def search_text(search_string):
    try:
        search_string = search_string.strip()
        if search_string not in queries.keys():
            query = {"status": 'INProgress', "requested_datetime": datetime.now(), "results": dict()}
            queries[search_string] = query
            await fetch_google(search_string)
            await fetch_duckduckgo(search_string)
            await fetch_wikipedia(search_string)
            queries[search_string]["status"] = "Completed"
            queries[search_string]["completed_datetime"] = datetime.now()
        else:
            queries[search_string]["lastupdated_datetime"] = datetime.now()
    except Exception as ex:
        print(f"function: search_string, ERROR:{ex}")


def search_result(q):
    try:
        return result_html(q, queries[q]) if q in queries.keys() else ""

    except Exception as ex:
        print(f"ERROR{ex}")