from itertools import chain

import pytest
from pystac import Collection
from pystac_client import Client as PystacClient
from pystac_client.errors import ClientTypeError


def is_valid_url(url: str, source_url: str) -> bool:
    """Verify URL is a valid link for harvesting"""
    if url and url.startswith(source_url) and not any(x in url for x in ["?", "thumbnail"]):
        return True
    return False


@pytest.mark.parametrize(
    "source_url",
    [
        pytest.param("https://api.stac.ceda.ac.uk", id="CEDA"),
    ],
)
def test_check_catalogue(source_url):
    """Collects all links to URLs that are children of the given source URL"""
    urls = set()
    print(f"URL: {source_url}")
    urls.add(source_url)

    try:
        client = PystacClient.open(source_url)
        all_items = client.get_all_items()
    except ClientTypeError:
        collection = Collection.from_file(source_url)
        root_catalogue = [link.target for link in collection.links if link.rel == "root"][0]

        client = PystacClient.open(root_catalogue)
        all_collections = client.get_collections()
        all_items = []

        for collection in all_collections:
            print(f"Collection: {collection}")
            self_link = [link.target for link in collection.links if link.rel == "self"][0]
            if self_link == source_url:
                collection = client.get_collection(collection.id)
                all_items = chain(all_items, collection.get_items(recursive=True))

    for item in all_items:
        print(f"Item: {item}")
        for link in item.links:
            if target := link.target:
                if link.rel in {
                    "child",
                    "items",
                    "item",
                    "self",
                    "parent",
                    "collection",
                } and is_valid_url(target, source_url):
                    urls.add(target)

    assert urls
