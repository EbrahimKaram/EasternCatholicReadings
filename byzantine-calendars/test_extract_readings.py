import unittest
from datetime import date

from distill_byzantine_lectionary import DEFAULT_INPUT, distill, load_rows, readings_from_row
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

    def test_calendar_readings_survive_distillation(self):
        lectionary, _ = distill(load_rows(DEFAULT_INPUT))
        temporal = lectionary["temporal"]
        self.assertEqual(
            temporal["lent:sunday:1"]["readingsByYear"]["2024"][0]["reference"],
            "Heb. 11: 24-26, 32-12:1",
        )
        self.assertEqual(
            temporal["lent:sunday:1"]["readingsByYear"]["2026"][0]["reference"],
            "Heb. 11: 24-26",
        )
        self.assertEqual(
            temporal["afterPentecost:sunday:5"]["readingsByYear"]["2024"][1]["reference"],
            "Matt. 8: 28-9:1",
        )
        self.assertEqual(
            temporal["afterPentecost:sunday:5"]["readingsByYear"]["2026"][1]["reference"],
            "Matt.8:28-34",
        )
        self.assertEqual(temporal["nativity:sunday:before"]["readings"][0]["reference"], "Heb. 11: 9-10; 17-23; 32-40")
        self.assertEqual(temporal["councils:sunday:first-six"]["readings"][1]["reference"], "Matt. 5: 14-19")
        self.assertEqual(lectionary["sanctoral"]["01-06"]["readings"][0]["reference"], "Titus 2:11-14; 3:4-7")


if __name__ == "__main__":
    unittest.main()
