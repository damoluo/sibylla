from lxml import html
import re
import requests

page = requests.get('http://www.cffex.com.cn/sj/ccpm/201704/12/T.xml')
xml = re.sub(r' +(?="|<|>|\?)|(?<=\n)\n', '', page.text).replace('  ', ' ')
# print(page.content)
print(xml.lower())

tree = html.fromstring(page.content)

instrumentid = [x.strip() for x in tree.xpath("//data//instrumentid/text()")]
tradingday = [x.strip() for x in tree.xpath("//data//tradingday/text()")]
datatypeid = [x.strip() for x in tree.xpath("//data//datatypeid/text()")]
rank = [x.strip() for x in tree.xpath("//data//rank/text()")]
shortname = [x.strip() for x in tree.xpath("//data//shortname/text()")]
volume = [x.strip() for x in tree.xpath("//data//volume/text()")]
varvolume = [x.strip() for x in tree.xpath("//data//varvolume/text()")]
partyid = [x.strip() for x in tree.xpath("//data//partyid/text()")]
productid = [x.strip() for x in tree.xpath("//data//productid/text()")]

data = {}
for i in range(len(instrumentid)):
    if instrumentid[i] not in data:
        data[instrumentid[i]] = {
            "date": tradingday[i],
            "volume": [],
            "long": [],
            "short": []
        }
    ins = data[instrumentid[i]]
    v = {
        "rank": int(rank[i]),
        "name": shortname[i],
        "volume": int(volume[i]),
        "increment": int(varvolume[i]),
        "party_id": partyid[i]
    }
    if datatypeid[i] == "0":
        ins['volume'].append(v)
    elif datatypeid[i] == "1":
        ins['long'].append(v)
    elif datatypeid[i] == "2":
        ins['short'].append(v)

print(data)
#
# print(len(instrumentid))
# print(len(tradingday))
# print(len(datatypeid))
# print(len(rank))
# print(len(shortname))
# print(len(volume))
# print(len(varvolume))
# print(len(partyid))
# print(len(productid))
