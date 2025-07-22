import requests
from bs4 import BeautifulSoup as bs
import json

def check_wash_machines(url:str='https://cabinet.unimetriq.com/client/df6c49da933a1654efdce60526a73558') -> dict:
    '''
    Записывает статус машинок в mach_status.json
    '''
    req = requests.get(url)
    soup = bs(req.content, 'html.parser')

    wash_machs = soup.find_all('div', class_=['col', 'mb-3', 'childItem'])
    wash_machs.pop(0)

    res_row = []
    res = {}

    for wash_mach in wash_machs:
        status_mach = wash_mach.find_all('div', class_ = 'text-center')
        for mach in status_mach:
            if ''.join(str(mach.text).split()) == 'СТИРКА':
                continue
            mache = ''.join(str(mach.text).split())
            res_row.append(mache)

    for r in range(0, len(res_row), 2):
        res[res_row[r]] = res_row[r + 1]

    with open('mach_status.json', 'w', encoding='utf-8') as m_s:
        json.dump(res, m_s, ensure_ascii=False, indent=2)
