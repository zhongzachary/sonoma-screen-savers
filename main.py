"""
This code will (asynchronously) download all the preview images and generate a README.md that
  contains a link to all the screen savers video.
"""
import asyncio
import aiohttp
import aiofiles
import json
import pandas

# read the entries.json from system
# if you are not running macOS Sonoma, you can use `data/entries.json`
ORIGINAL_ENTRIES_PATH = '/Library/Application Support/com.apple.idleassetsd/Customer/entries.json'

with open(ORIGINAL_ENTRIES_PATH, 'r') as f:
    ENTRIES = json.load(f)

DISPLAY_NAMES =  pandas.read_csv('data/display_names.csv').set_index('assetId')

ASSET_URLS = pandas.DataFrame.from_dict(
        dict(
            assetId=asset['id'], 
            previewImage=asset['previewImage'], 
            fullVideo=asset['url-4K-SDR-240FPS']
        )
        for asset in ENTRIES['assets']
    )\
    .set_index('assetId')

NAMES_AND_URLS = DISPLAY_NAMES.join(ASSET_URLS)


async def download(session: aiohttp.ClientSession, 
                   url: str, 
                   filename:str):
    """
    Download content from the given URL into the file.
    """
    async with session.get(url, verify_ssl=False) as response:
        async with aiofiles.open(filename, mode='wb') as f:
            await f.write(await response.read())


async def download_all(urls: pandas.Series, folder:str):
    """
    Download from a Series of URLs to the given folder.
    
    The keys of the series will be used as the file name.

    e.g. To download all preview images into a folder called "preview_images", use
    ```
    asyncio.run(download_all(NAMES_AND_URLS['previewImage'], 'preview_images'))
    ```
    """
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.ensure_future(
                download(session, url, f'{folder}/{name}.{url.split(".")[-1]}')
            )
            for name, url in urls.items()
        ]
        await asyncio.gather(*tasks)


def save_screen_savers_url_as_markdown():
    # extract fields needed
    table = NAMES_AND_URLS.reset_index(drop=False)\
        [['name', 'category', 'previewImage', 'fullVideo', 'assetId']]\
        .set_index('name')

    # convert preview image into Markdown images
    table['previewImage'] = table.apply(
        lambda row: f'![{row.name}](preview_images/{row.assetId}.png)', 
        axis=1
    )
    
    # convert full video into Markdown links
    table['fullVideo'] = table['fullVideo'].apply(
        lambda url: f'[Link]({url})'
    )
    
    # change column names for Markdown
    table = table.drop('assetId', axis=1)
    table.index.name = 'Name'
    table.columns = ['Category', 'Preview Image', 'Full Video']
    
    # save to "table.md" by category
    with open('README.md', 'w') as f:
        # add header
        with open('README_header.md') as header:
            f.write(header.read())

        group_by_category = table.groupby('Category', sort=False)

        for category in group_by_category.groups.keys():
            f.write(f'- [{category}]({category.lower()})\n')
        
        f.write('\n')

        for category, category_table in group_by_category:
            f.write(f'## {category}\n\n')
            f.write(category_table.drop('Category', axis=1).to_markdown())
            f.write('\n')


if __name__ == "__main__":
    # download all preview images
    # asyncio.run(download_all(NAMES_AND_URLS['previewImage'], 'preview_images'))

    # create a README file
    save_screen_savers_url_as_markdown()
