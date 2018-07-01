import MySQLdb
import os
import requests
import time
import lxml.html
import lxml.etree


class XPathTarget(object):
    def __init__(self, s):
        if isinstance(s, basestring):
            self.tree = lxml.html.fromstring(s)
        else:
            raise ValueError('unsupported type')


class XPathSniper(object):
    def __init__(self, xpath):
        self.xpath = xpath

    def shot_all(self, target, convert_to_string=True):
        if not isinstance(target, XPathTarget):
            target = XPathTarget(target)
        ret = target.tree.xpath(self.xpath)
        if convert_to_string:
            ret = map(self._to_string, ret)
        return ret

    def shot_first(self, target, convert_to_string=True):
        if not isinstance(target, XPathTarget):
            target = XPathTarget(target)

        result = target.tree.xpath(self.xpath)
        if isinstance(result, list):
            ret = result[0] if len(result) > 0 else None
            if convert_to_string:
                ret = self._to_string(ret)
            return ret

        return result

    @staticmethod
    def _to_string(ele):
        if isinstance(ele, lxml.etree.ElementBase):
            return lxml.etree.tostring(ele, encoding='unicode', method='html')
        else:
            return ele


page_count_sniper = XPathSniper(
    r'//div[@class="pagebar"]/a/@href'
)
content_block_sniper = XPathSniper(
    r'//div[@class="content-block"]'
)
secret_and_comfort_sniper = XPathSniper(
    r'//div[@class="col1"]/div[@class="block untagged"]'
)
secret_sniper = XPathSniper(
    r'//div[@class="content"]/text()'
)
secret_id_sniper = XPathSniper(
    r'//div[@class="content"]/@id'
)
comfort_sniper = XPathSniper(
    r'//div[@class=""]/div[@class=""]/div[@class=""]/div[@class=""]/span[@class="productBuyPrice"]/span/text()'
)

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip',
           'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
           'Cache-Control': 'max-age=0',
           'Connection': 'Keep-Alive',
           'User-Agent': "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-au; rv:1.9.0.1) Gecko/2008070206"
           }


def main(event):
    host = "http://www.6our.com/best?&p=%d"
    page_count = 20
    req = requests.Session()
    url = host % 0
    response = req.get(url, headers=headers, timeout=3000, )
    if response.status_code == 200:
        page_count_result = page_count_sniper.shot_all(response.text)
        page_count_result = [int(s.replace('/best?&p=', '')) for s in page_count_result]
        page_count_result.sort()
        if len(page_count_result) > 0:
            page_count = page_count_result[len(page_count_result) - 1]
    # showReply(id=19511)
    # type: "POST",
    # url: "/index.php/Reply/showReply",
    # data: "id=" + id,
    all_secrets = []
    all_secrets_id = []

    for i in xrange(page_count):
        if 0 != i:
            url = host % i
            response = requests.get(url, headers=headers, timeout=3000,)

        if response.status_code == 200:
            content_block_html = content_block_sniper.shot_all(response.text)
            if len(content_block_html) < 2:
                continue
            content_block_html = content_block_html[1]
            contents = secret_and_comfort_sniper.shot_all(content_block_html)
            for content in contents:
                secret = secret_sniper.shot_all(content)
                for s in secret:
                    if s not in ['\n\t', '\t\n']:
                        all_secrets.append(s.replace('\n\t', '').replace('\t\n', ''))
                secret_id = secret_id_sniper.shot_all(content)[0].replace("content-", "")
                all_secrets_id.append(secret_id)
        # TODO: delete
        if i >= 3:
            break
        time.sleep(5)
    # print len(all_secrets_id), all_secrets_id
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    user = os.environ.get("DB_USER")
    passwd = os.environ.get("DB_PASSWD")
    db = os.environ.get("DB")
    conn = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
    cursor = conn.cursor()
    # values = cursor.fetchall()
    # print valuesimport MySQLdb
import os
import requests
import time
import lxml.html
import lxml.etree


class XPathTarget(object):
    def __init__(self, s):
        if isinstance(s, basestring):
            self.tree = lxml.html.fromstring(s)
        else:
            raise ValueError('unsupported type')


class XPathSniper(object):
    def __init__(self, xpath):
        self.xpath = xpath

    def shot_all(self, target, convert_to_string=True):
        if not isinstance(target, XPathTarget):
            target = XPathTarget(target)
        ret = target.tree.xpath(self.xpath)
        if convert_to_string:
            ret = map(self._to_string, ret)
        return ret

    def shot_first(self, target, convert_to_string=True):
        if not isinstance(target, XPathTarget):
            target = XPathTarget(target)

        result = target.tree.xpath(self.xpath)
        if isinstance(result, list):
            ret = result[0] if len(result) > 0 else None
            if convert_to_string:
                ret = self._to_string(ret)
            return ret

        return result

    @staticmethod
    def _to_string(ele):
        if isinstance(ele, lxml.etree.ElementBase):
            return lxml.etree.tostring(ele, encoding='unicode', method='html')
        else:
            return ele


page_count_sniper = XPathSniper(
    r'//div[@class="pagebar"]/a/@href'
)
content_block_sniper = XPathSniper(
    r'//div[@class="content-block"]'
)
secret_and_comfort_sniper = XPathSniper(
    r'//div[@class="col1"]/div[@class="block untagged"]'
)
secret_sniper = XPathSniper(
    r'//div[@class="content"]/text()'
)
secret_id_sniper = XPathSniper(
    r'//div[@class="content"]/@id'
)
comfort_sniper = XPathSniper(
    r'//div[@class=""]/div[@class=""]/div[@class=""]/div[@class=""]/span[@class="productBuyPrice"]/span/text()'
)

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip',
           'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
           'Cache-Control': 'max-age=0',
           'Connection': 'Keep-Alive',
           'User-Agent': "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-au; rv:1.9.0.1) Gecko/2008070206"
           }


def main(event):
    host = "http://www.6our.com/best?&p=%d"
    page_count = 20
    req = requests.Session()
    url = host % 0
    response = req.get(url, headers=headers, timeout=3000, )
    if response.status_code == 200:
        page_count_result = page_count_sniper.shot_all(response.text)
        page_count_result = [int(s.replace('/best?&p=', '')) for s in page_count_result]
        page_count_result.sort()
        if len(page_count_result) > 0:
            page_count = page_count_result[len(page_count_result) - 1]
    # showReply(id=19511)
    # type: "POST",
    # url: "/index.php/Reply/showReply",
    # data: "id=" + id,
    all_secrets = []
    all_secrets_id = []

    for i in xrange(page_count):
        if 0 != i:
            url = host % i
            response = requests.get(url, headers=headers, timeout=3000,)

        if response.status_code == 200:
            content_block_html = content_block_sniper.shot_all(response.text)
            if len(content_block_html) < 2:
                continue
            content_block_html = content_block_html[1]
            contents = secret_and_comfort_sniper.shot_all(content_block_html)
            for content in contents:
                secret = secret_sniper.shot_all(content)
                for s in secret:
                    if s not in ['\n\t', '\t\n']:
                        all_secrets.append(s.replace('\n\t', '').replace('\t\n', ''))
                secret_id = secret_id_sniper.shot_all(content)[0].replace("content-", "")
                all_secrets_id.append(secret_id)
        # TODO: delete
        if i >= 3:
            break
        time.sleep(5)
    # print len(all_secrets_id), all_secrets_id
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    user = os.environ.get("DB_USER")
    passwd = os.environ.get("DB_PASSWD")
    db = os.environ.get("DB")
    conn = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
    cursor = conn.cursor()
    # values = cursor.fetchall()
    # print values
    for s in all_secrets:
        cursor.execute("insert into secret_material(`secret`, `secret_id`) values('%s', '%d')" % (s, 0))
    conn.close()

    for s in all_secrets:
        cursor.execute("insert into secret_material(`secret`, `secret_id`) values('%s', '%d')" % (s, 0))
    conn.close()
