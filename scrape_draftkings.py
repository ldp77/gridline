import requests

DATA_BASE_DIRECTORY='623-01'

url = 'https://sportsbook.draftkings.com/leagues/football/ncaaf'
resp = requests.get(url)
html_content = resp.text

with open(f'{DATA_BASE_DIRECTORY}/html/draftkings.html', 'w') as outfile:
    outfile.write(html_content)
