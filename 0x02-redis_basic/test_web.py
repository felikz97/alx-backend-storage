# test_web.py
import time
from web import get_page, r

url = "http://google.com"

print("1. Fetching...")
html = get_page(url)
print(f"Length: {len(html)}")
print("Cached:", bool(r.get(f"cached:{url}")))
print("Count:", r.get(f"count:{url}").decode())

time.sleep(5)
print("\n2. Fetching again (cached)...")
html = get_page(url)
print("Cached:", bool(r.get(f"cached:{url}")))
print("Count:", r.get(f"count:{url}").decode())

time.sleep(6)
print("\n3. Fetching after cache expires...")
html = get_page(url)
print("Cached:", bool(r.get(f"cached:{url}")))
print("Count:", r.get(f"count:{url}").decode())
print(f"Length: {len(html)}")
print("HTML content fetched again after cache expiry.")
