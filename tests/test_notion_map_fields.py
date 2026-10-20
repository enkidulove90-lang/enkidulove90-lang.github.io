import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("notion_sync", ROOT / "tools" / "notion_sync.py")
notion_sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(notion_sync)


class NotionMapFieldTests(unittest.TestCase):
    def test_text_or_select_city_property(self):
        props = {"venue_city": {"select": {"name": "Singapore"}}}
        self.assertEqual(notion_sync.notion_text_property(props, "venue_city"), "Singapore")

    def test_affiliation_cities_accept_multi_select(self):
        props = {"affil_city": {"multi_select": [{"name": "Beijing"}, {"name": "Shanghai"}]}}
        self.assertEqual(notion_sync.notion_city_list(props, "affil_city"), ["Beijing", "Shanghai"])

    def test_location_metadata_reads_all_supported_fields(self):
        props = {
            "location_type": {"select": {"name": "Affiliation"}},
            "venue_city": {"rich_text": [{"plain_text": "Singapore"}]},
            "affil_city": {"multi_select": [{"name": "Beijing"}]},
            "corresponding_city": {"select": {"name": "Shanghai"}},
            "affiliation_name": {"rich_text": [{"plain_text": "Tsinghua University"}]},
        }
        fields = notion_sync.notion_location_fields(props)
        self.assertEqual(fields["location_type"], "Affiliation")
        self.assertEqual(fields["venue_city"], "Singapore")
        self.assertEqual(fields["affil_city"], ["Beijing"])
        self.assertEqual(fields["corresponding_city"], "Shanghai")
        self.assertEqual(fields["affiliation_name"], "Tsinghua University")


if __name__ == "__main__":
    unittest.main()
