import unittest

from tools.notion_sync import published_posts_query


class PublishedPostsQueryTests(unittest.TestCase):
    def test_query_requires_both_published_status_and_post_type(self):
        query = published_posts_query()

        self.assertEqual(
            query["filter"],
            {
                "and": [
                    {"property": "status", "select": {"equals": "Published"}},
                    {"property": "type", "select": {"equals": "Post"}},
                ]
            },
        )
        self.assertEqual(
            query["sorts"],
            [{"property": "date", "direction": "descending"}],
        )

    def test_new_query_is_not_mutated_by_previous_pagination(self):
        first = published_posts_query()
        first["start_cursor"] = "cursor-1"

        self.assertNotIn("start_cursor", published_posts_query())


if __name__ == "__main__":
    unittest.main()
