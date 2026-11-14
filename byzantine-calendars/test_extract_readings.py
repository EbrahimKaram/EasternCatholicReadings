import unittest
from datetime import date

from distill_byzantine_lectionary import readings_from_row
from extract_readings import parse_reading_text


class GospelExtractionTests(unittest.TestCase):
    def test_twelve_gospels_is_not_a_reference(self):
        parsed = parse_reading_text(
            "GREAT AND HOLY THURSDAY Vespers with Divine Liturgy of St. Basil "
            "Reading of 12 Gospels"
        )
        self.assertIsNone(parsed["gospel"])
        self.assertIn("12 Gospels", parsed["notes"])

    def test_singular_gospel_reference_is_still_extracted(self):
        parsed = parse_reading_text("Epistle Heb. 2:11-18; Gospel Lk. 1:24-38.")
        self.assertEqual(parsed["epistle"], "Heb. 2:11-18")
        self.assertEqual(parsed["gospel"], "Lk. 1:24-38")

    def test_annunciation_epistle_book_is_restored_when_distilling(self):
        row = {"date": date(2026, 3, 25), "epistle": "2:11-18", "gospel": "Lk. 1:24-38"}
        self.assertEqual(readings_from_row(row)[0]["reference"], "Heb. 2:11-18")
        row["date"] = date(2026, 3, 26)
        self.assertEqual(readings_from_row(row)[0]["reference"], "2:11-18")

    def test_saint_demetrius_gospel_is_corrected_when_distilling(self):
        for gospel in ("John, 12:17-6:2", "John, 12:17 to 16:2"):
            row = {"date": date(2026, 10, 26), "epistle": None, "gospel": gospel}
            self.assertEqual(readings_from_row(row)[0]["reference"], "John 15:17-16:2")
            row["date"] = date(2026, 10, 27)
            self.assertEqual(readings_from_row(row)[0]["reference"], gospel)


if __name__ == "__main__":
    unittest.main()
