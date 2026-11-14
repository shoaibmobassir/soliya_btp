"""Offline checks for the Stage 0 evidence package."""

import csv
import json
from pathlib import Path, PurePosixPath
import unittest
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


class StageZeroEvidenceTests(unittest.TestCase):
    def test_manifest_pins_metadata_and_distinguishes_local_observations(self):
        manifest_path = ROOT / "data" / "source_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        sources = {source["id"]: source for source in manifest["sources"]}
        self.assertEqual(set(sources), {"companionharm", "aicompanionbench"})

        for source in sources.values():
            with self.subTest(source=source["id"]):
                revision = source["revision"]
                self.assertRegex(revision, r"^[0-9a-f]{40}$")
                self.assertIn(f"/git/trees/{revision}?", source["tree_endpoint"])
                for document in source["documentation"]:
                    self.assertRegex(document["sha256"], r"^[0-9a-f]{64}$")
                for data_object in source["data_objects"]:
                    self.assertRegex(data_object["git_blob_oid"], r"^[0-9a-f]{40}$")
                    self.assertGreater(data_object["reported_bytes"], 0)
                    path = PurePosixPath(data_object["path"])
                    self.assertFalse(path.is_absolute())
                    self.assertNotIn("..", path.parts)
                    if source["local_status"] == "missing":
                        self.assertIsNone(data_object["raw_bytes_sha256"])
                        self.assertIsNone(data_object["observed_rows"])
                        self.assertIsNone(data_object["observed_conversations"])

        split_paths = {item["path"] for item in sources["companionharm"]["data_objects"]}
        self.assertEqual(
            split_paths,
            {"data/splits/train.csv", "data/splits/dev.csv", "data/splits/test.csv"},
        )

    def test_literature_matrix_covers_required_sources_and_evidence(self):
        path = ROOT / "results" / "PRIOR_ART_MATRIX.csv"
        with path.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))

        urls = {row["url"] for row in rows}
        self.assertGreaterEqual(len(urls), 15)
        self.assertEqual(len(urls), len(rows))
        self.assertEqual(len({row["paper_id"] for row in rows}), len(rows))
        required_sources = {
            "CompanionHarm",
            "AICompanionBench",
            "CompanionSafe",
            "ConCI",
            "When Context Flips, Safety Breaks",
            "No Convo!",
            "Pavlopoulos et al. 2020",
            "Xenos et al. 2021",
            "SIM-VAIL",
            "CHIVE",
            "Persona-Grounded Safety Evaluation",
        }
        self.assertLessEqual(required_sources, {row["paper_id"] for row in rows})
        for row in rows:
            with self.subTest(paper=row["paper_id"]):
                self.assertNotIn(None, row)
                self.assertTrue(all(row.values()))
                self.assertEqual(urlparse(row["url"]).scheme, "https")
                self.assertRegex(row["publication_date"], r"^\d{4}-\d{2}(-\d{2})?$")
                self.assertIn(
                    row["verdict"],
                    {"direct duplicate", "substantial overlap", "background", "unresolved"},
                )


if __name__ == "__main__":
    unittest.main()
