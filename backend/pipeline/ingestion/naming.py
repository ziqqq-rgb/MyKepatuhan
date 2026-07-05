# pipeline/ingestion/naming.py
"""
Parses versioned document filenames like 'act_203_v1' into structured
metadata, so a specific old version can be found and deleted before
its replacement is ingested.
"""
import re

_VERSION_PATTERN = re.compile(r"^(?P<name>.+)_v(?P<version>\d+)$", re.IGNORECASE)


def parse_document_name(doc_stem: str) -> tuple[str, int]:
    """
    'act_203_v1' -> ('act_203', 1)
    Falls back to (doc_stem, 1) if the filename doesn't follow the
    '<name>_v<N>' convention — ingestion never fails on a bad filename,
    it just won't be version-trackable.
    """
    match = _VERSION_PATTERN.match(doc_stem)
    if not match:
        return doc_stem, 1
    return match.group("name"), int(match.group("version"))