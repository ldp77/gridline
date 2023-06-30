import requests
import time

DATA_BASE_DIRECTORY='623-01'

url_base = 'https://www.vegasinsider.com/college-football/odds/las-vegas/?week=2023-reg-'
for n in range(1, 16):
    url = f'{url_base}{n}'
    resp = requests.get(url)
    html_content = resp.text
    with open(f'{DATA_BASE_DIRECTORY}/html/vegasinsider-week-{n}.html', 'w') as outfile:
        outfile.write(html_content)
    time.sleep(5)