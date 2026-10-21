import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_places", ROOT / "tools" / "build_places.py")
build_places = importlib.util.module_from_spec(SPEC)


class BuildPlacesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SPEC.loader.exec_module(build_places)

    def test_cached_place_with_local_image_is_reused_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            image = root / "source" / "images" / "map" / "bari.jpg"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"image")
            cached = {"id": "bari", "name": "Bari", "wgs84": [16, 41], "image": "/images/map/bari.jpg", "description": "Bari"}

            result = build_places.reusable_cached_place("Bari", cached, root)

            self.assertEqual(result, cached)

    def test_cached_coordinates_survive_a_later_offline_build(self):
        cached = {"wgs84": [-117.234, 32.88]}

        coordinates = build_places.select_coordinates({}, "La Jolla", {"cities": {}}, cached)

        self.assertEqual(coordinates, [-117.234, 32.88])

    def test_city_fields_are_extracted_from_frontmatter(self):
        raw = "---\ntitle: Paper\nvenue_city: Singapore\naffil_city: [Beijing, Shanghai]\n---\nBody"
        metadata = build_places.parse_frontmatter(raw)
        self.assertEqual(metadata["venue_city"], "Singapore")
        self.assertEqual(metadata["affil_city"], ["Beijing", "Shanghai"])

    def test_affiliation_prefers_explicit_city(self):
        metadata = {"location_type": "Affiliation", "affil_city": ["Shenzhen"], "corresponding_city": "Beijing"}
        resolved = build_places.resolve_location(metadata, {"schools": {}, "companies": {}, "publishers": {}})
        self.assertEqual(resolved["city"], "Shenzhen")
        self.assertEqual(resolved["location_type"], "affiliation")

    def test_explicit_affiliation_city_keeps_school_semantics_from_dictionary(self):
        metadata = {"location_type": "Affiliation", "affil_city": ["Boston"], "affiliation_name": "Harvard Medical School"}
        dictionaries = {"institutions": {"harvard medical school": {
            "name": "Harvard Medical School", "city": "Boston", "kind": "school",
            "aliases": ["HMS"], "wgs84": [-71.103, 42.336]
        }}}
        resolved = build_places.resolve_location(metadata, dictionaries)
        self.assertEqual(resolved["location_type"], "school")
        self.assertEqual(resolved["wgs84"], [-71.103, 42.336])

    def test_affiliation_name_uses_company_dictionary_when_city_is_missing(self):
        metadata = {"location_type": "Affiliation", "affiliation_name": "Google"}
        dictionaries = {"institutions": {"google": {
            "name": "Google", "city": "Mountain View", "kind": "company",
            "aliases": ["Google LLC"], "wgs84": [-122.084, 37.422]
        }}}
        resolved = build_places.resolve_location(metadata, dictionaries)
        self.assertEqual(resolved["city"], "Mountain View")
        self.assertEqual(resolved["location_type"], "company")
        self.assertEqual(resolved["location_label"], "Google")

    def test_verified_first_author_institution_can_be_geocoded_without_city_text(self):
        metadata = {
            "location_type": "school",
            "affiliation_name": "University of California San Diego",
            "first_author": "Junda Wu",
        }

        resolved = build_places.resolve_location(metadata, {"institutions": {}, "publishers": {}, "cities": {}})

        self.assertEqual(resolved["city"], "University of California San Diego")
        self.assertEqual(resolved["location_label"], "University of California San Diego")
        self.assertEqual(resolved["source"], "verified_first_author_affiliation")

    def test_empty_primary_location_falls_back_to_corresponding_city(self):
        metadata = {"location_type": "Venue", "venue_city": "", "corresponding_city": "Hangzhou"}
        resolved = build_places.resolve_location(metadata, {"schools": {}, "companies": {}, "publishers": {}})
        self.assertEqual(resolved["city"], "Hangzhou")
        self.assertEqual(resolved["source"], "corresponding_city")

    def test_virtual_location_skips_physical_city_lookup(self):
        resolved = build_places.resolve_location({"location_type": "Virtual"}, {"schools": {}, "companies": {}, "publishers": {}})
        self.assertEqual(resolved["city"], "Virtual")
        self.assertEqual(resolved["location_type"], "virtual")

    def test_static_overseas_coordinate_is_used_when_available(self):
        dictionaries = {"cities": {"london": {"wgs84": [-0.1276, 51.5072]}}}
        self.assertEqual(build_places.static_city_coordinates("London", dictionaries), (-0.1276, 51.5072))

    def test_institution_alias_resolves_to_local_coordinate_without_geocoder(self):
        dictionaries = {"institutions": {"tsinghua university": {
            "name": "Tsinghua University", "city": "Beijing", "kind": "school",
            "aliases": ["THU", "清华大学"], "wgs84": [116.326, 40.003]
        }}}
        resolved = build_places.resolve_location(
            {"location_type": "Affiliation", "affiliation_name": "THU"}, dictionaries
        )
        self.assertEqual(resolved["city"], "Beijing")
        self.assertEqual(resolved["wgs84"], [116.326, 40.003])
        self.assertEqual(resolved["source"], "location_dictionary")

    def test_department_prefix_still_matches_the_parent_institution(self):
        dictionaries = {"institutions": {"the university of hong kong": {
            "name": "The University of Hong Kong", "city": "Hong Kong", "kind": "school",
            "aliases": ["HKU"], "wgs84": [114.1378, 22.283]
        }}}

        entry = build_places.find_dictionary_entry(
            "Department of Computer Science, University of Hong Kong", dictionaries
        )

        self.assertEqual(entry["name"], "The University of Hong Kong")

    def test_nominatim_result_is_parsed_as_wgs84_longitude_latitude(self):
        result = build_places.first_nominatim_coordinate([
            {"lon": "-122.1697", "lat": "37.4275", "display_name": "Stanford University"}
        ])
        self.assertEqual(result, (-122.1697, 37.4275))

    def test_city_presentation_supplies_hover_copy_and_local_gallery(self):
        dictionaries = {"cities": {"hong kong": {
            "description": "Long description",
            "hover_text": "香港：繁华与竞争之地",
            "city_images": ["/images/map/hong-kong.jpg", "/images/map/hong-kong-2.jpg"]
        }}}

        presentation = build_places.city_presentation("Hong Kong", dictionaries)

        self.assertEqual(presentation["hover_text"], "香港：繁华与竞争之地")
        self.assertEqual(len(presentation["city_images"]), 2)

    def test_unknown_city_gets_enough_unique_local_gallery_slots_for_its_papers(self):
        presentation = build_places.city_presentation("La Jolla", {"cities": {}}, image_count=4)

        self.assertEqual(presentation["city_images"], [
            "/images/map/la-jolla.jpg",
            "/images/map/la-jolla-2.jpg",
            "/images/map/la-jolla-3.jpg",
            "/images/map/la-jolla-4.jpg",
        ])

    def test_unknown_city_copy_describes_an_academic_location_without_generic_slogan(self):
        presentation = build_places.city_presentation("Bari", {"cities": {}})

        self.assertIn("学术地点", presentation["description"])
        self.assertNotIn("论文、机构与城市在这里相遇", presentation["description"])

    def test_local_gallery_prefers_webp_and_discovers_numbered_images(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            image_dir = root / "source" / "images" / "map"
            image_dir.mkdir(parents=True)
            (image_dir / "bari.webp").write_bytes(b"webp-one")
            (image_dir / "bari-2.webp").write_bytes(b"webp-two")
            (image_dir / "bari.jpg").write_bytes(b"jpg-one")

            result = build_places.local_gallery_urls("bari", root)

            self.assertEqual(result, ["/images/map/bari.webp", "/images/map/bari-2.webp"])

    def test_local_gallery_deduplicates_identical_file_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            first = root / "first.jpg"
            duplicate = root / "duplicate.jpg"
            different = root / "different.jpg"
            first.write_bytes(b"same")
            duplicate.write_bytes(b"same")
            different.write_bytes(b"different")

            result = build_places.unique_local_images([first, duplicate, different])

            self.assertEqual(result, [first, different])

    def test_dictionary_affiliation_carries_institution_description(self):
        dictionaries = {"institutions": {"tsinghua university": {
            "name": "Tsinghua University", "city": "Beijing", "kind": "school",
            "wgs84": [116.326, 40.003], "inst_desc": "清华大学的推荐系统研究连接基础方法与产业问题。"
        }}}

        resolved = build_places.resolve_location(
            {"location_type": "Affiliation", "affiliation_name": "Tsinghua University"}, dictionaries
        )

        self.assertEqual(resolved["institution"]["name"], "Tsinghua University")
        self.assertIn("推荐系统", resolved["institution"]["description"])

    def test_wikimedia_gallery_candidates_are_unique_and_limited(self):
        pages = [
            {"title": "Hong Kong skyline", "imageinfo": [{"thumburl": "https://img/one.jpg"}]},
            {"title": "Hong Kong harbour", "imageinfo": [{"thumburl": "https://img/two.jpg"}]},
            {"title": "Duplicate", "imageinfo": [{"thumburl": "https://img/one.jpg"}]},
        ]

        candidates = build_places.wikimedia_image_candidates(pages, "Hong Kong", 2)

        self.assertEqual([item[0] for item in candidates], ["https://img/one.jpg", "https://img/two.jpg"])

    def test_wikimedia_candidates_respect_global_exclusion_set(self):
        pages = [
            {"title": "Used", "imageinfo": [{"thumburl": "https://img/used.jpg"}]},
            {"title": "Fresh", "imageinfo": [{"thumburl": "https://img/fresh.jpg"}]},
        ]

        candidates = build_places.wikimedia_image_candidates(
            pages, "City", 2, excluded_urls={"https://img/used.jpg"}
        )

        self.assertEqual(candidates, [("https://img/fresh.jpg", "Fresh")])

    def test_wikimedia_candidates_do_not_repeat_the_primary_image_title(self):
        pages = [
            {"title": "File:Primary.jpg", "imageinfo": [{"thumburl": "https://img/primary.jpg"}]},
            {"title": "File:Alternate.jpg", "imageinfo": [{"thumburl": "https://img/alternate.jpg"}]},
        ]

        candidates = build_places.wikimedia_image_candidates(
            pages, "City", 2, excluded_titles={"File:Primary.jpg"}
        )

        self.assertEqual(candidates, [("https://img/alternate.jpg", "File:Alternate.jpg")])

    def test_wikimedia_gallery_queries_cover_five_distinct_city_views(self):
        queries = build_places.wikimedia_gallery_queries("Hong Kong")

        self.assertEqual(len(queries), 5)
        self.assertTrue(all('"Hong Kong"' in query for query in queries))
        joined = " ".join(queries).casefold()
        for subject in ("street", "people", "nature", "art", "skyline"):
            self.assertIn(subject, joined)

    def test_build_places_always_includes_virtual_fallback(self):
        payload = build_places.build_places(dry_run=True)

        self.assertFalse(any(place["id"] == "virtual" for place in payload["places"]))

    def test_affiliation_override_supplies_verified_first_author_location(self):
        metadata = {"slug": "paper-2403.06447"}
        overrides = {"paper-2403.06447": {
            "first_author": "Junda Wu",
            "affiliation_name": "University of California San Diego",
            "affil_city": "La Jolla",
            "location_type": "school",
        }}

        merged = build_places.apply_affiliation_override(metadata, overrides)

        self.assertEqual(merged["first_author"], "Junda Wu")
        self.assertEqual(merged["affiliation_name"], "University of California San Diego")


if __name__ == "__main__":
    unittest.main()
