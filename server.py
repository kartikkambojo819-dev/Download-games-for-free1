from flask import Flask, request, Response
import cloudscraper
import re

app = Flask(__name__)

# Cloudflare सुरक्षा को पार करने के लिए मोबाइल ब्राउज़र का उपयोग
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'android', 'mobile': True}
)

TARGET_URL = "https://filmyzilla.digital"
NEW_NAME = "Kartik Kamboj"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    url = f"{TARGET_URL}/{path}"
    if request.query_string:
        url += f"?{request.query_string.decode('utf-8')}"
        
    print(f"[*] Fetching ({request.method}): {url}")
    
    try:
        if request.method == 'POST':
            resp = scraper.post(url, data=request.form)
        else:
            resp = scraper.get(url)
        
        # अनचाहे हेडर्स को हटाना ताकि प्रॉक्सी बिना रुकावट काम करे
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        content_type = resp.headers.get('Content-Type', '')

        if 'text/html' in content_type:
            html_text = resp.text
            
            # वेबसाइट का नाम बदलकर Kartik Kamboj करना
            html_text = re.sub(r'Filmyzilla\.com|Filmyzila\.com|Filmyzilla|Filmyzila', NEW_NAME, html_text, flags=re.IGNORECASE)
            html_text = re.sub(r'https?://filmyzilla\.digital', 'http://localhost:5000', html_text, flags=re.IGNORECASE)
            html_text = re.sub(r'filmyzilla\.digital', 'localhost:5000', html_text, flags=re.IGNORECASE)
            
            # लिंक्स और टेक्स्ट को डार्क बैकग्राउंड पर साफ दिखाने के लिए CSS
            custom_css = """
            <style>
                a, a:link, a:visited { color: #4fc3f7 !important; }
                a:hover { color: #ff5722 !important; }
            </style>
            </head>
            """
            html_text = re.sub(r'</head>', custom_css, html_text, flags=re.IGNORECASE)
            
            return Response(html_text, resp.status_code, headers, content_type=content_type)
        
        return Response(resp.content, resp.status_code, headers)
        
    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

if __name__ == '__main__':
    print("Local Server starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
