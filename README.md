# HentaiChanApi-async
## Wrapper over https://hentaichan.live

hentai-chan-api-async is a small asynchronous parser library 
that will allow you to easily use manga from https://hentaichan.live
Recommended to use python3.7+

## Install

```sh
pip install hentai-chan-api-async
```

## Features

- Parsing by pages and quantities
- Search engine by queries and by tags
- Manga object to easily retrieve manga data
- Ability to use a proxy
- Asynchronous

## Examples

An example of using the 'get_new' method:
```Python
import asyncio
from hentai_chan_api_async import HentaiChan


async def main():
    hc = HentaiChan()

    manga = await hc.get_new(page_num=1, count=2)

    for el in manga:
        print(el.id)  # '40918-doll-house-glava-2'
        print(el.title)  # 'Doll House - глава 2'
        print(el.poster)  # https://imgcover.../.../01.jpg'
        print(el.series)  # 'Оригинальные работы'
        print(el.author)  # 'Sexgazers'
        print(el.translator)  # 'Zone'
        print(await el.content.images)  # ['https://.../.png', 'https://.../.png'...]
        print(el.tags)  # ['анал', 'без цензуры', 'большая грудь', ...]
        print(el.date)  # '17 января 2022'


asyncio.get_event_loop().run_until_complete(main())
    
```
Note that the arguments: "page_num=1" and "count=2" are optional.
By default, "page_num=1" and "count=20".

Also note that calling "el.content.images" will invoke the parser, which may take some time to use. I advise you to call "el.content.images" only when necessary.


Tag search example:
```Python
import asyncio
from hentai_chan_api_async import HentaiChan


async def main():
    hc = HentaiChan()

    tags = await hc.get_all_tags()  # ['3D', 'action', 'ahegao', 'bdsm', 'corruption', ...]
    manga = await hc.search(tag=tags[0])  # [Manga(id='40779-ms-i', title='Ms. I (Невыразимые секреты её прошлого)')...]

    print(manga[0].title)  # Ms. I (Невыразимые секреты её прошлого)
    print(await manga[0].content.images)  # ['https://mimg2.imgschan.xyz/manganew/m/1641154521_ms.-i/001.jpg', ...]


asyncio.get_event_loop().run_until_complete(main())

```

Search query example:
```Python
import asyncio
from hentai_chan_api_async import HentaiChan


async def main():
    hc = HentaiChan()

    manga = await hc.search(page_num=3, query='bikini')  # [Manga(...)...]
    
    print(manga[0].title)  # Bikini's Bottom
    print(await manga[0].content.images)  # ['https://mimg2.imgschan.xyz/manganew/l/1630962513_lightsource-bik...', ...]


asyncio.get_event_loop().run_until_complete(main())
```
