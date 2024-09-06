import json
import re
from playwright.sync_api import Playwright, sync_playwright, expect, Route

def is_fordon(entry):
    for cat in entry.get('category', {}):
        if cat.get('id', None) == "1000":
            print("FILTERING CRAP")
            return True

def filter_crap(lst):
    return [entry for entry in lst if not is_fordon(entry)]

def handle_route(route: Route) -> None:

    #response = route.fetch()
    url = f"{route.request.url}&cg=4000&cg=2000&cg=5000&cg=6000&cg=8000"
    print(f">>> {url}")
    response = route.fetch(url=url)
    body = response.text()

    data = json.loads(body)

    if "data" in data:
        data['data'] = filter_crap(data['data'])
    if "gallery" in data:
        data['gallery'] = filter_crap(data['gallery'])

    body = json.dumps(data, indent=2)
    #print(body)

    route.fulfill(
        response=response,
        body=body,
        headers={**response.headers},
    )


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()
    page.goto("https://www.blocket.se/")

    page.wait_for_load_state()

    #page.on("request", lambda request: print(">>", request.method, request.url))
    #page.on("response", lambda response: print("<<", response.status, response.url))
    page.route("**/v2/content?**", handle_route)


    page.get_by_placeholder("Vad vill du söka efter?").click()
    page.get_by_placeholder("Vad vill du söka efter?").fill("ender")
    page.get_by_placeholder("Vad vill du söka efter?").press("Enter")

    page.wait_for_load_state()

    page.wait_for_timeout(timeout=9999*1000)
    

    # ---------------------
    context.storage_state(path="post_script.json")
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
