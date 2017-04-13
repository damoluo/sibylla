from lxml import html
import re
import requests
import time
from functools import reduce
import shelve

def get_data(date_str):
    url = 'http://www.cffex.com.cn/sj/ccpm/{}/{}/T.xml'.format(date_str[:6], date_str[6:])
    page = requests.get(url)
    xml = re.sub(r' +(?="|<|>|\?)|(?<=\n)\n', '', page.text).replace('  ', ' ')
    # print(page.content)
    # print(xml.lower())
    tree = html.fromstring(page.content)
    instrumentid = [x.strip() for x in tree.xpath('//data//instrumentid/text()')]
    tradingday = [x.strip() for x in tree.xpath('//data//tradingday/text()')]
    datatypeid = [x.strip() for x in tree.xpath('//data//datatypeid/text()')]
    rank = [x.strip() for x in tree.xpath('//data//rank/text()')]
    shortname = [x.strip() for x in tree.xpath('//data//shortname/text()')]
    volume = [x.strip() for x in tree.xpath('//data//volume/text()')]
    varvolume = [x.strip() for x in tree.xpath('//data//varvolume/text()')]
    partyid = [x.strip() for x in tree.xpath('//data//partyid/text()')]
    productid = [x.strip() for x in tree.xpath('//data//productid/text()')]

    data = {}
    for i in range(len(instrumentid)):
        if instrumentid[i] not in data:
            data[instrumentid[i]] = {
                'date': tradingday[i],
                'volume': [],
                'long': [],
                'short': []
            }
        ins = data[instrumentid[i]]
        v = {
            'rank': int(rank[i]),
            'name': shortname[i],
            'volume': int(volume[i]),
            'increment': int(varvolume[i]),
            'party_id': partyid[i]
        }
        if datatypeid[i] == '0':
            ins['volume'].append(v)
        elif datatypeid[i] == '1':
            ins['long'].append(v)
        elif datatypeid[i] == '2':
            ins['short'].append(v)

    instrumentid = [x.strip() for x in tree.xpath('//positionamt//instrumentid/text()')]
    volumeamt = [x.strip() for x in tree.xpath('//positionamt//volumeamt/text()')]
    varvolumeamt = [x.strip() for x in tree.xpath('//positionamt//varvolumeamt/text()')]
    buyvolumeamt = [x.strip() for x in tree.xpath('//positionamt//buyvolumeamt/text()')]
    buyvarvolumeamt = [x.strip() for x in tree.xpath('//positionamt//buyvarvolumeamt/text()')]
    sellvolumeamt = [x.strip() for x in tree.xpath('//positionamt//sellvolumeamt/text()')]
    sellvarvolumeamt = [x.strip() for x in tree.xpath('//positionamt//sellvarvolumeamt/text()')]
    futurecompany = [x.strip() for x in tree.xpath('//positionamt//futurecompany/text()')]

    for i in range(len(instrumentid)):
        if int(futurecompany[i]) == 0:
            meta = {
                'volume': int(volumeamt[i]),
                'volume_increment': int(varvolumeamt[i]),
                'long': int(buyvolumeamt[i]),
                'long_increment': int(buyvarvolumeamt[i]),
                'short': int(sellvolumeamt[i]),
                'short_increment': int(sellvarvolumeamt[i])
            }
            data[instrumentid[i]]['meta'] = meta
    return data


def get_signal(data):
    result = {}
    for code, ins in data.items():
        dB = reduce(lambda a, b: a + b, [x['increment'] for x in ins['long']])
        dS = reduce(lambda a, b: a + b, [x['increment'] for x in ins['short']])
        delta = dB - dS
        result[code] = {
            'valid': is_valid(ins),
            'heat': get_heat(ins),
            'delta': delta,
            'open_interest': ins['meta']['long']
        }
    return result


def is_valid(ins):
    return not (len(ins['volume']) < 20 or len(ins['long']) < 20 or len(ins['short']) < 20)


def get_heat(ins):
    top_sum = reduce(lambda a, b: a + b, [x['volume'] for x in ins['volume']])
    total = ins['meta']['volume']
    return top_sum / total


if __name__ == '__main__':
    # now = time.strftime('%Y%m%d')
    # data = get_data(now)
    # print(is_valid(data['T1706']))
    # print(data)
    # print(get_heat(data['T1706']))
    # signal = get_signal(data)
    # file = shelve.open("test")
    # file['data'] = signal
    # file.close()

    file = shelve.open("test")
    signal = file['data']
    file.close()
    print(signal)

