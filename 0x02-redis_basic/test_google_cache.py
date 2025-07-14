import time
from web import get_page, r

url = "http://google.com"

# Initial fetch (should hit the web)
print("1. Fetching Google (initial)...")
html = get_page(url)
print(f"Length: {len(html)}")

# Check counter and cache
print("Access count:", r.get(f"count:{url}").decode())
print("Cached:", bool(r.get(f"cached:{url}")))

# Wait 5 seconds and fetch again (should be cached)
time.sleep(5)
print("\n2. Fetching Google again (cached)...")
html = get_page(url)
print(f"Length: {len(html)}")
print("Access count:", r.get(f"count:{url}").decode())
print("Cached:", bool(r.get(f"cached:{url}")))

# Wait 6 more seconds (total 11) to let the cache expire
time.sleep(6)
print("\n3. Fetching Google after cache expiry...")
html = get_page(url)
print(f"Length: {len(html)}")
print("Access count:", r.get(f"count:{url}").decode())
print("Cached:", bool(r.get(f"cached:{url}")))
