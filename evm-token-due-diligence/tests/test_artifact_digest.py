from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
from artifact_digest import digest  # noqa: E402


class ArtifactDigestTests(unittest.TestCase):
    def test_streaming_digest_matches_hashlib(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "artifact.bin"
            content = (b"evidence\x00" * 200_000) + b"tail"
            artifact.write_bytes(content)
            self.assertEqual(digest(artifact), hashlib.sha256(content).hexdigest())


if __name__ == "__main__":
    unittest.main()
