import logging
import re

import aiohttp
from .data import Manga
from .content_parser import MangaContent
from bs4 import BeautifulSoup


class HentaiChan:
    _host = 'https://hentaichan.live'
    _header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/97.0.4692.71 Safari/537.36',
    }

    def __init__(self, proxies: dict = None, debug: bool = False):
        self._proxy = proxies

        logging.basicConfig(format=f"[%(asctime)s] - [{__name__}/%(name)s] - [%(levelname)s]: %(message)s",
                            level=logging.DEBUG if debug else logging.INFO)

    async def __get_site_content(self, url, params: dict = None) -> BeautifulSoup:
        async with aiohttp.ClientSession(headers=self._header) as session:
            async with session.get(url, proxy=self._proxy, params=params) as resp:
                text = await resp.read()
        return BeautifulSoup(text.decode('utf-8'), 'html.parser')

    async def get_new(self, page_num: int = 1, count: int = 20) -> list[Manga]:
        """
        Метод возвращает :param count: эл-тов (если возможно)
        новой манги, используя номер страницы

        :param page_num: номер страницы.
        :param count: кол-во эл-тов страницы (максимум 20 на страницу)
        :return:
        """
        assert page_num >= 1, ValueError("Значение page_num не может быть меньше 1")
        assert count <= 20, ValueError("Значение count не может быть больше 20")

        offset = page_num * 20 - 20
        url = self._host + '/manga/new'
        return await self.__get_search_content(url, offset, count)

    async def search(self, page_num: int = 1, count: int = 20, query: str = None, tag: str = None) -> list[Manga]:
        assert page_num >= 1, ValueError("Значение page_num не может быть меньше 1")
        assert count <= 20, ValueError("Значение count не может быть больше 20")

        if tag:
            url = f'{self._host}/tags/{tag}'
        elif query:
            url = f'{self._host}/?do=search&subaction=search&story={query}'
        elif tag and query:
            raise TypeError('Метод search получил сразу 2 аргумента для поиска, допустим только 1')
        else:
            raise TypeError('Метод search не получил аргументов для поиска')

        offset = page_num * 20 - 20
        return await self.__get_search_content(url, offset, count)

    async def get_all_tags(self) -> list[str]:
        """
        Метод возвращает список всех tags
        упомянутых на сайте

        :return:
        """
        url = f'{self._host}/tags'
        raw_tags = (await self.__get_site_content(url)).find_all('li', class_='sidetag')
        tags = [tag.find_all('a')[-1].text for tag in raw_tags]

        return tags

    async def get_manga(self, manga_id: str) -> Manga:
        """
        Метод возвращает объект Manga

        :param manga_id:
        :return:
        """
        url = f'{self._host}/manga/{manga_id}.html'
        content = await self.__get_site_content(url)

        dle_content = content.find('div', id='content').find('div', id='dle-content')
        side_content = content.find('div', id='side')

        m = Manga(id=manga_id)
        m.poster = dle_content.find('div', id='manga_images').find('img').attrs.get('src')
        m.title = dle_content.find('div', id='info_wrap').find('a', class_='title_top_a').string
        m.date = dle_content.find('div', class_='row4_right').find('b').string

        info_rows = dle_content.find('div', id='info_wrap').find_all('div', class_='row')
        for el in info_rows:
            if el.find('div', class_='item').string == 'Аниме/манга':
                m.series = el.find('a').string
            elif el.find('div', class_='item').string == 'Автор':
                m.author = el.find('a').string
            elif el.find('div', class_='item').string == 'Переводчик':
                m.translator = el.find('a').string

        tags = []
        tags_table = side_content.find_all('li', class_='sidetag')
        for tag in tags_table:
            tags.append(((tag.find_all('a'))[-1]).string.replace(' ', '_'))

        m.tags = tags
        m.content = await self.__get_manga_content(manga_id)

        return m

    async def __get_search_content(self, url: str, offset: int, count: int) -> list[Manga]:
        """
        Вспомогательный метод, используется для парсинга манги из поисковой выдачи

        :param url:
        :param offset:
        :return:
        """
        soup_content = await self.__get_site_content(url, params={'offset': offset})
        elements = soup_content.find('div', id='content').find_all('div', class_='content_row')[:count]

        content = []
        for el in elements:
            el_div_with_manga_id = el.find('div', class_='manga_row1')
            if el_div_with_manga_id.find('a', class_='title_link'):
                href = el_div_with_manga_id.find('a', class_='title_link').attrs.get('href')
            else:
                href = el_div_with_manga_id.find('a').attrs.get('href').replace(self._host, '')

            _id = re.search(r'/(.+)/(.+).html', href)
            if _id.group(1) == 'manga':
                content.append(
                    await self.get_manga(_id.group(2))
                )
                logging.debug(f'[{elements.index(el) + 1}/{len(elements)}] {_id.group(1)} - accepted | {_id.group(2)}')
            else:
                logging.debug(f'[{elements.index(el) + 1}/{len(elements)}] {_id.group(1)} - passed | {_id.group(2)}')

        return content

    async def __get_manga_content(self, manga_id) -> MangaContent:
        """
        Вспомогательный метод для парсинга страниц контента манги

        :param manga_id:
        :return:
        """
        url = f'{self._host}/online/{manga_id}.html'
        return MangaContent(get_site_content_method=self.__get_site_content, manga_url=url)
