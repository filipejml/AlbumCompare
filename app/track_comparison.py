import re
import unicodedata


FEATURE_CREDIT_PATTERN = re.compile(
    r"""
    \s*
    (?:
        [(\[]\s*(?:feat(?:uring)?|ft)\.?\s+.*?[)\]]
        |
        (?:[-–—,]\s*)?(?:feat(?:uring)?|ft)\.?\s+.+$
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

VERSION_MARKERS = (
    "acoustic",
    "ao vivo",
    "demo",
    "edit",
    "extended",
    "instrumental",
    "live",
    "mix",
    "mono",
    "orchestral",
    "radio",
    "remaster",
    "remastered",
    "remix",
    "stereo",
    "version",
    "versao",
)


def _plain_text(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return without_accents.casefold()


def _normalize_words(value):
    value = _plain_text(value)
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _has_version_marker(value):
    normalized = f" {_normalize_words(value)} "
    return any(f" {marker} " in normalized for marker in VERSION_MARKERS)


def _split_title_and_version(title):
    title = FEATURE_CREDIT_PATTERN.sub("", title or "").strip()

    bracket_match = re.search(r"\s*[\(\[]([^\(\)\[\]]+)[\)\]]\s*$", title)
    if bracket_match and _has_version_marker(bracket_match.group(1)):
        return title[: bracket_match.start()].strip(), bracket_match.group(1)

    dash_parts = re.split(r"\s+[-–—]\s+", title, maxsplit=1)
    if len(dash_parts) == 2 and _has_version_marker(dash_parts[1]):
        return dash_parts[0].strip(), dash_parts[1].strip()

    return title, ""


def _normalize_version(value):
    words = _normalize_words(value).split()
    aliases = {
        "remastered": "remaster",
        "versao": "version",
    }
    generic_words = {"the", "a", "an"}

    normalized = [
        aliases.get(word, word) for word in words if word not in generic_words
    ]

    if len(normalized) > 1 and "version" in normalized:
        normalized.remove("version")

    return " ".join(sorted(normalized))


def track_signature(track):
    """Cria uma assinatura estável sem confundir versões musicais diferentes."""
    title, version = _split_title_and_version(track.get("name", ""))
    return _normalize_words(title), _normalize_version(version)


def _primary_artist_signature(track):
    artists = track.get("artists") or []
    if not artists:
        return ""

    primary_artist = artists[0]
    return primary_artist.get("id") or _normalize_words(primary_artist.get("name", ""))


def _tracks_are_compatible(track1, track2):
    artist1 = _primary_artist_signature(track1)
    artist2 = _primary_artist_signature(track2)
    if artist1 and artist2 and artist1 != artist2:
        return False

    duration1 = track1.get("duration_ms")
    duration2 = track2.get("duration_ms")
    if isinstance(duration1, int) and isinstance(duration2, int):
        if abs(duration1 - duration2) > 5000:
            return False

    return True


def compare_track_lists(album1_tracks, album2_tracks):
    """Compara faixas em pares, preservando ordem e quantidade de duplicatas."""
    matched_album2 = set()
    common_tracks = []
    unique_to_album1 = []

    album2_by_id = {}
    album2_by_signature = {}

    for index, track in enumerate(album2_tracks):
        track_id = track.get("id")
        if track_id:
            album2_by_id.setdefault(track_id, []).append(index)
        album2_by_signature.setdefault(track_signature(track), []).append(index)

    def first_available(indexes, source_track, check_metadata=False):
        return next(
            (
                index
                for index in indexes or []
                if index not in matched_album2
                and (
                    not check_metadata
                    or _tracks_are_compatible(source_track, album2_tracks[index])
                )
            ),
            None,
        )

    for track in album1_tracks:
        match_index = None
        track_id = track.get("id")

        if track_id:
            match_index = first_available(album2_by_id.get(track_id), track)

        if match_index is None:
            signature = track_signature(track)
            if signature[0]:
                match_index = first_available(
                    album2_by_signature.get(signature),
                    track,
                    check_metadata=True,
                )

        if match_index is None:
            unique_to_album1.append(track)
        else:
            matched_album2.add(match_index)
            common_tracks.append(track)

    unique_to_album2 = [
        track
        for index, track in enumerate(album2_tracks)
        if index not in matched_album2
    ]

    return common_tracks, unique_to_album1, unique_to_album2
