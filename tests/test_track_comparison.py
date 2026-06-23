import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from track_comparison import compare_track_lists, track_signature  # noqa: E402


def track(name, track_id=None, artist_id=None, duration_ms=None):
    artists = [{"id": artist_id, "name": artist_id}] if artist_id else []
    return {
        "id": track_id,
        "name": name,
        "preview_url": None,
        "artists": artists,
        "duration_ms": duration_ms,
    }


class TrackSignatureTests(unittest.TestCase):
    def test_normalizes_case_accents_punctuation_and_spaces(self):
        first = track_signature(track("  CANÇÃO—DO   MAR! "))
        second = track_signature(track("cancao do mar"))

        self.assertEqual(first, second)

    def test_ignores_feature_credit_in_title(self):
        self.assertEqual(
            track_signature(track("Minha Música (feat. Artista)")),
            track_signature(track("Minha Musica")),
        )
        self.assertEqual(
            track_signature(track("Minha Música - ft. Artista")),
            track_signature(track("Minha Musica")),
        )

    def test_equivalent_remaster_labels_match(self):
        self.assertEqual(
            track_signature(track("Song - 2009 Remaster")),
            track_signature(track("Song (Remastered 2009)")),
        )

    def test_different_versions_do_not_match(self):
        studio = track_signature(track("Song"))
        live = track_signature(track("Song - Live"))
        acoustic = track_signature(track("Song (Acoustic Version)"))

        self.assertNotEqual(studio, live)
        self.assertNotEqual(studio, acoustic)
        self.assertNotEqual(live, acoustic)

    def test_non_version_parenthetical_is_part_of_title(self):
        self.assertNotEqual(
            track_signature(track("Escape")),
            track_signature(track("Escape (The Pina Colada Song)")),
        )


class TrackComparisonTests(unittest.TestCase):
    def test_same_spotify_id_has_priority(self):
        common, unique1, unique2 = compare_track_lists(
            [track("Nome antigo", "same-id")],
            [track("Nome novo", "same-id")],
        )

        self.assertEqual(len(common), 1)
        self.assertEqual(unique1, [])
        self.assertEqual(unique2, [])

    def test_duplicate_tracks_are_paired_only_once(self):
        common, unique1, unique2 = compare_track_lists(
            [track("Song"), track("Song")],
            [track("song")],
        )

        self.assertEqual(len(common), 1)
        self.assertEqual(len(unique1), 1)
        self.assertEqual(unique2, [])

    def test_preserves_original_order(self):
        common, unique1, unique2 = compare_track_lists(
            [track("Primeira"), track("Comum"), track("Terceira")],
            [track("Outra"), track("comum")],
        )

        self.assertEqual([item["name"] for item in common], ["Comum"])
        self.assertEqual(
            [item["name"] for item in unique1],
            ["Primeira", "Terceira"],
        )
        self.assertEqual([item["name"] for item in unique2], ["Outra"])

    def test_same_title_from_different_artists_does_not_match(self):
        common, unique1, unique2 = compare_track_lists(
            [track("Home", artist_id="artist-1")],
            [track("Home", artist_id="artist-2")],
        )

        self.assertEqual(common, [])
        self.assertEqual(len(unique1), 1)
        self.assertEqual(len(unique2), 1)

    def test_large_duration_difference_does_not_match_without_same_id(self):
        common, unique1, unique2 = compare_track_lists(
            [track("Intro", duration_ms=30000)],
            [track("Intro", duration_ms=90000)],
        )

        self.assertEqual(common, [])
        self.assertEqual(len(unique1), 1)
        self.assertEqual(len(unique2), 1)

    def test_small_duration_difference_is_tolerated(self):
        common, unique1, unique2 = compare_track_lists(
            [track("Song", duration_ms=180000)],
            [track("song", duration_ms=183000)],
        )

        self.assertEqual(len(common), 1)
        self.assertEqual(unique1, [])
        self.assertEqual(unique2, [])


if __name__ == "__main__":
    unittest.main()
