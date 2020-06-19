import logging
from collections import namedtuple
import csv

import bs4
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

ParserResult = namedtuple(
    'ParserResult',
    (
        'url',
        'model',
    ),
)

HEADERS = (
    'Товар',
    'Ссылка',
)


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User - Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 83.0.4103.106Safari / 537.36',
            'Accept-Language': 'ru',
        }
        self.result = []

    def load_page(self):
        url = 'https://allo.ua/ua/products/notebooks/'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        blocks = soup.select('li.item')
        for block in blocks:
            self.parse_block(block=block)

    def parse_block(self, block):
        url_block = block.select_one('a.product-name.multiple-lines-crop')
        if not url_block:
            logger.error('no url block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return

        model_block = block.select_one('a.product-name.multiple-lines-crop')
        if not model_block:
            logger.info('no model block')
            return

        model = model_block.get('title')
        if not model:
            logger.info('no model')
            return

        self.result.append(ParserResult(
            url=url,
            model=model,
        ))

        logger.debug('Модель товара: {}'.format(model))
        logger.debug('Ссылка на товар: {}'.format(url))
        logger.debug('-' * 100)

    def save_results(self):
        path = 'D:\\code\\projects\\python\\parser\\results.csv'
        with open(path, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info('Получено {} результатов поиска'.format(len(self.result)))

        self.save_results()


if __name__ == '__main__':
    parser = Client()
    parser.run()
