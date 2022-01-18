import json
import re


class MangaContent:
    def __init__(self, get_site_content_method, manga_url: str):
        self.__get_site_content = get_site_content_method
        self._url = manga_url

    @property
    async def images(self) -> list[str]:
        soup_content = await self.__get_site_content(self._url, params={'development_access': 'true'})
        raw_js = soup_content.find_all('script')[2].text

        var_data = raw_js.replace('createGallery(data)', '').replace('    ', '').replace('\n', '').replace("'", '"')
        pattern = re.compile(r"var data = (\{.*?\})$", re.MULTILINE | re.DOTALL)

        if var_data:
            obj = pattern.search(var_data).group(1)
            obj = json.loads(obj)
            return obj['fullimg']
        else:
            return []
