import certifi, httpx

# Test 1: plain httpx
print("Testing httpx with certifi...")
try:
    with httpx.Client(verify=certifi.where()) as c:
        r = c.get("https://api.openai.com")
        print("httpx+certifi OK:", r.status_code)
except Exception as e:
    print("httpx+certifi FAIL:", e)

# Test 2: default ssl
print("\nTesting httpx default ssl...")
try:
    with httpx.Client() as c:
        r = c.get("https://api.openai.com")
        print("httpx default OK:", r.status_code)
except Exception as e:
    print("httpx default FAIL:", e)

# Test 3: verify=False (insecure, just for diagnosis)
print("\nTesting httpx verify=False...")
import warnings
warnings.filterwarnings("ignore")
try:
    with httpx.Client(verify=False) as c:
        r = c.get("https://api.openai.com")
        print("httpx no-verify OK:", r.status_code)
except Exception as e:
    print("httpx no-verify FAIL:", e)
