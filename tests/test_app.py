import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import app as application  # noqa: E402


VALID_ID_1 = "A" * 22
VALID_ID_2 = "B" * 22


class AppRouteTests(unittest.TestCase):
    def setUp(self):
        application.app.config.update(TESTING=True)
        self.client = application.app.test_client()

    def test_search_rejects_short_query(self):
        response = self.client.get("/search_artist?query=ab")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_albums_reject_invalid_artist_id(self):
        response = self.client.get("/get_albums?artist_id=invalid")

        self.assertEqual(response.status_code, 400)

    def test_compare_rejects_same_album(self):
        response = self.client.post(
            "/compare",
            data={"album1": VALID_ID_1, "album2": VALID_ID_1},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("dois álbuns diferentes", response.get_data(as_text=True))

    @patch.object(application, "spotify")
    def test_compare_renders_complete_result(self, spotify):
        spotify.get_album.side_effect = [
            {
                "name": "Álbum 1",
                "release_date": "2020",
                "total_tracks": 2,
                "popularity": 50,
                "external_urls": {"spotify": "https://open.spotify.com/album/1"},
                "images": [],
            },
            {
                "name": "Álbum 2",
                "release_date": "2021",
                "total_tracks": 2,
                "popularity": 60,
                "external_urls": {"spotify": "https://open.spotify.com/album/2"},
                "images": [],
            },
        ]
        spotify.get_album_tracks.side_effect = [
            [
                {"name": "Comum", "preview_url": None},
                {"name": "Só no primeiro", "preview_url": None},
            ],
            [
                {"name": "Comum", "preview_url": None},
                {"name": "Só no segundo", "preview_url": None},
            ],
        ]

        response = self.client.post(
            "/compare",
            data={"album1": VALID_ID_1, "album2": VALID_ID_2},
        )

        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Comum", body)
        self.assertIn("Só no primeiro", body)
        self.assertIn("Só no segundo", body)


if __name__ == "__main__":
    unittest.main()
