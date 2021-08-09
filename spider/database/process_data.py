import re
from typing import List

from spider.model import Setu, Artwork, Author, Size, Url


def process_data(data: list) -> List[Setu]:
    setu_list = []
    for setu in data:
        if setu['page_count'] == 1:  # 单页
            setu_list.append(
                Setu(
                    artwork=Artwork(title=setu['title'], id=setu['id']),
                    author=Author(name=re.sub(r'[@,＠].*$', '', setu['user']['name']), id=setu['user']['id']),
                    sanity_level=setu['sanity_level'],
                    r18=None,
                    page=0,
                    create_date=setu['create_date'],
                    size=Size(width=setu['width'], height=setu['height']),
                    tags=[tag['name'] for tag in setu['tags']] +
                         [tag['translated_name'] for tag in setu['tags'] if tag['translated_name'] != None],
                    urls=Url(original=setu['meta_single_page']['original_image_url'],
                             large=setu['image_urls']['large'],
                             medium=setu['image_urls']['medium'])
                )
            )
        else:  # 多页
            for i in range(setu['page_count']):
                setu_list.append(
                    Setu(
                        artwork=Artwork(title=setu['title'], id=setu['id']),
                        author=Author(name=re.sub(r'[@,＠].*$', '', setu['user']['name']), id=setu['user']['id']),
                        sanity_level=setu['sanity_level'],
                        r18=None,
                        page=i,
                        create_date=setu['create_date'],
                        size=Size(width=setu['width'], height=setu['height']),
                        tags=[tag['name'] for tag in setu['tags']] +
                             [tag['translated_name'] for tag in setu['tags'] if tag['translated_name'] != None],
                        urls=Url(original=setu['meta_pages'][i]['image_urls']['original'],
                                 large=setu['meta_pages'][i]['image_urls']['large'],
                                 medium=setu['meta_pages'][i]['image_urls']['medium'])
                    )
                )
    return setu_list
