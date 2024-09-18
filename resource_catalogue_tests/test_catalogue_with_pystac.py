import logging
import os
from pprint import pprint

import pytest
from pystac_client import Client
from pystac_client.exceptions import APIError


@pytest.fixture(scope="module")
def client():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    catalogue_url = os.getenv("CATALOGUE_URL", "https://dev.eodatahub.org.uk/api/catalogue/stac")
    return Client.open(catalogue_url)


@pytest.mark.parametrize(
    "collection_id",
    [
        "airbus_sar_data",
        "cordex",
        "land_cover",
        "ukcp",
    ],
)
def test_search(client, collection_id):
    """Test searching in the catalogue"""

    def recursive_search(catalog, collection_id, limit=5):
        try:
            search = catalog.search(collections=[collection_id], limit=limit)
            items = list(search.items())
            if items:
                return items
        except APIError as e:
            logging.debug(f"APIError: {e}")
        except AttributeError as e:
            logging.debug(f"AttributeError: {e} - This might be a collection, not a catalog.")
        except Exception as e:
            logging.debug(f"Exception: {e}")

        sub_catalogs = list(catalog.get_children())
        for sub_catalog in sub_catalogs:
            if sub_catalog.STAC_OBJECT_TYPE == "Catalog":
                items = recursive_search(sub_catalog, collection_id, limit)
                if items:
                    return items
        return []

    root_catalog = client.get_root()
    items = recursive_search(root_catalog, collection_id, limit=5)
    pprint(items)
    assert len(items) > 0, "Search should return at least one item"


def test_walk_catalogue_hierarchy(client):
    """Test walking the catalogue hierarchy"""

    def walk_catalog(catalog, depth=0):
        print("  " * depth + f"Catalog: {catalog.id}")
        sub_catalogs = list(catalog.get_children())
        for sub_catalog in sub_catalogs:
            if sub_catalog.STAC_OBJECT_TYPE == "Catalog":
                walk_catalog(sub_catalog, depth + 1)
            else:
                print("  " * (depth + 1) + f"Collection: {sub_catalog.id}")

    root_catalog = client.get_root()
    walk_catalog(root_catalog)


def test_get_items(client):
    """Test getting all items in the catalogue"""
    items = list(client.get_all_items())
    assert items, "No items found in the catalogue"


if __name__ == "__main__":
    pytest.main()
