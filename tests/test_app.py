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
        application.app.config.update(TESTING=True, LOGIN_DISABLED=True)
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


class LoginRouteTests(unittest.TestCase):
    def setUp(self):
        application.app.config.update(TESTING=True, LOGIN_DISABLED=False)
        self.client = application.app.test_client()

    def tearDown(self):
        application.app.config.update(LOGIN_DISABLED=True)

    def test_index_redirects_to_login_without_session(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    @patch.object(
        application,
        "authenticate_user",
        return_value={"username": "tester", "role": "user"},
    )
    def test_login_accepts_configured_credentials(self, _authenticate_user):
        response = self.client.post(
            "/login",
            data={"username": "tester", "password": "secret"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")

    @patch.object(application, "authenticate_user", return_value=None)
    def test_login_rejects_invalid_credentials(self, _authenticate_user):
        response = self.client.post(
            "/login",
            data={"username": "tester", "password": "wrong"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("inv", response.get_data(as_text=True).lower())

    @patch.object(
        application,
        "create_user",
        return_value={"username": "newuser", "role": "user"},
    )
    def test_register_creates_user_and_redirects_to_login(self, create_user):
        response = self.client.post(
            "/register",
            data={
                "username": "newuser",
                "password": "secret123",
                "password_confirmation": "secret123",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")
        create_user.assert_called_once_with("newuser", "secret123")

    def test_register_rejects_password_confirmation_mismatch(self):
        response = self.client.post(
            "/register",
            data={
                "username": "newuser",
                "password": "secret123",
                "password_confirmation": "different",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("confirma", response.get_data(as_text=True).lower())

    @patch.object(application, "create_user", side_effect=ValueError("Usuário já existe."))
    def test_register_shows_validation_error(self, _create_user):
        response = self.client.post(
            "/register",
            data={
                "username": "tester",
                "password": "secret123",
                "password_confirmation": "secret123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("existe", response.get_data(as_text=True).lower())


if __name__ == "__main__":
    unittest.main()
