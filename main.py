import asyncio
import json
import pathlib

import aiofiles
import aiohttp
import duckdb
import pyarrow as pa
from tabulate import tabulate

LANG = "en"
ENTRIES = duckdb.read_json("./data/entries.json")
ASSETS = ENTRIES.query(
    "entries",
    """
    SELECT asset.* replace(upper(cast(asset.id as string)) as id)
    FROM (
        SELECT unnest(assets) AS asset
        FROM entries
    );
    """,
)
CATEGORIES = ENTRIES.query(
    "entries",
    """
    SELECT category.*
    FROM (
        SELECT unnest(categories) AS category
        FROM entries
    );
    """,
)


async def download(session: aiohttp.ClientSession, url: str, filename: str):
    """
    Download content from the given URL into the file.
    """
    async with session.get(url, ssl=False) as response:
        async with aiofiles.open(filename, mode="wb") as f:
            await f.write(await response.read())


async def download_all(
    table: duckdb.DuckDBPyRelation,
    url_field: str,
    output_file_name_field: str,
    output_folder: str,
):
    """
    Download URLs from a DuckDB table.

    `output_file_name_field` determines the downloaded file name.
    """
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    rows = table.query(
        "assets",
        f"""
        SELECT "{output_file_name_field}", "{url_field}"
        FROM assets
        WHERE "{url_field}" IS NOT NULL
        """,
    ).fetchall()

    async with aiohttp.ClientSession() as session:
        tasks = [
            download(
                session,
                url,
                f"{output_folder}/{filename}.{url.split('.')[-1].split('?')[0]}",
            )
            for filename, url in rows
        ]

        await asyncio.gather(*tasks)


def summarize_assets_for_markdown(lang=LANG) -> duckdb.DuckDBPyRelation:
    with pathlib.Path(f"./data/locales/{lang}.json").open(encoding="utf-8") as f:
        translations = json.load(f)
    localized_names = duckdb.from_arrow(
        pa.table({"key": list(translations), "value": list(translations.values())})
    )
    assert len(localized_names) > 0, f"Language '{lang}' not supported"

    assets_w_names = (
        ASSETS.select(
            "id",
            "localizedNameKey",
            "previewImage",
            "url-4K-SDR-240FPS",
            "categories",
            "subcategories",
            "preferredOrder",
            duckdb.col("variant", "orientation").alias("orientation"),
        )
        .unnest("categories")
        .unnest("subcategories")
        .rename(categories="categoryId", subcategories="subcategoryId")
        .join(
            localized_names.rename(key="localizedNameKey", value="localizedNameValue"),
            condition=["localizedNameKey"],
            how="left",
        )
    )
    categories_w_names = (
        CATEGORIES.unnest("subcategories")
        .rename(subcategories="subcategory")
        .select(
            duckdb.col("id").alias("categoryId"),
            duckdb.col("localizedNameKey").alias("categoryLocalizedNameKey"),
            duckdb.col("preferredOrder").alias("categoryPreferredOrder"),
            duckdb.col("subcategory", "id").alias("subcategoryId"),
            duckdb.col("subcategory", "localizedNameKey").alias(
                "subcategoryLocalizedNameKey"
            ),
            duckdb.col("subcategory", "preferredOrder").alias(
                "subcategoryPreferredOrder"
            ),
        )
        .join(
            localized_names.rename(
                key="categoryLocalizedNameKey", value="categoryLocalizedNameValue"
            ),
            condition=["categoryLocalizedNameKey"],
            how="left",
        )
        .join(
            localized_names.rename(
                key="subcategoryLocalizedNameKey", value="subcategoryLocalizedNameValue"
            ),
            condition=["subcategoryLocalizedNameKey"],
            how="left",
        )
    )
    assets_w_categories = (
        assets_w_names.join(
            categories_w_names, condition=["categoryId", "subcategoryId"], how="left"
        )
        .query(
            "t",
            """
            select
              t.*,
              row_number() over (order by categoryPreferredOrder, subcategoryPreferredOrder, preferredOrder) as assetOrder
            from t""",
        )
        .select(
            duckdb.col("id").alias("assetId"),
            "previewImage",
            duckdb.col("url-4K-SDR-240FPS").alias("fullVideo"),
            duckdb.col("localizedNameValue").alias("name"),
            duckdb.col("categoryLocalizedNameValue").alias("category"),
            duckdb.col("subcategoryLocalizedNameValue").alias("subcategory"),
            "orientation",
            "assetOrder",
        )
    )
    return assets_w_categories


def save_screen_savers_url_as_markdown():
    table = summarize_assets_for_markdown()
    categories = [
        category
        for category, _ in table.group_by("category")
        .agg("min(assetOrder) as categoryOrder")
        .order("categoryOrder")
        .fetchall()
    ]

    # save to README.md by category
    with open("README.md", "w") as f:
        # add header
        with open("README_header.md") as header:
            f.write(header.read())

        for category in categories:
            anchor = category.lower().replace(" ", "-")
            f.write(f"- [{category}](#{anchor})\n")

        f.write("\n")

        for category in categories:
            f.write(f"## {category}\n\n")
            formatted_list = [
                (
                    subcategory,
                    name + (f" - {orientation}" if orientation else ""),
                    f"![{name}](preview_images/{asset_id.upper()}.png)",
                    f"[Link]({full_video})",
                )
                for asset_id, name, subcategory, full_video, orientation in table.filter(
                    duckdb.col("category") == category
                )
                .select("assetId", "name", "subcategory", "fullVideo", "orientation")
                .fetchall()
            ]
            f.write(
                tabulate(
                    formatted_list,
                    headers=("Subcategory", "Name", "Preview Image", "Full Video"),
                    tablefmt="pipe",
                )
            )
            f.write("\n")


def main():
    asyncio.run(
        download_all(
            ASSETS,
            url_field="previewImage",
            output_file_name_field="id",
            output_folder="preview_images",
        )
    )

    save_screen_savers_url_as_markdown()


if __name__ == "__main__":
    main()
