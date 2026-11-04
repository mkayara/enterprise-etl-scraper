import tempfile
import unittest
from pathlib import Path

import pandas as pd

from app.pipelines.etl import DataPipeline


class DataPipelineTests(unittest.TestCase):
    def test_saves_normalized_csv_and_excel_without_duplicate_rows(self):
        records = [
            {" Quote Text ": "Keep moving", "Author": "A. Person"},
            {" Quote Text ": "Keep moving", "Author": "A. Person"},
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory) / "exports"
            pipeline = DataPipeline(output_dir=str(output_directory))

            result = pipeline.process_and_save(records, filename="quotes")

            csv_path = Path(result["csv_path"])
            excel_path = Path(result["excel_path"])
            self.assertTrue(csv_path.is_file())
            self.assertTrue(excel_path.is_file())
            self.assertEqual(result["row_count"], 1)

            csv_data = pd.read_csv(csv_path)
            excel_data = pd.read_excel(excel_path)
            self.assertEqual(list(csv_data.columns), ["quote_text", "author"])
            self.assertEqual(list(excel_data.columns), ["quote_text", "author"])
            self.assertEqual(csv_data.to_dict(orient="records"), [
                {"quote_text": "Keep moving", "author": "A. Person"},
            ])

    def test_rejects_empty_data(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            pipeline = DataPipeline(output_dir=temporary_directory)

            with self.assertRaisesRegex(ValueError, "No data provided"):
                pipeline.process_and_save([])

    def test_rejects_filename_that_escapes_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory) / "exports"
            pipeline = DataPipeline(output_dir=str(output_directory))

            with self.assertRaisesRegex(ValueError, "without a path"):
                pipeline.process_and_save(
                    [{"quote": "Example"}],
                    filename="../outside",
                )

            self.assertFalse((Path(temporary_directory) / "outside.csv").exists())

    def test_rejects_empty_or_special_filenames(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            pipeline = DataPipeline(output_dir=temporary_directory)

            for filename in ("", ".", ".."):
                with self.subTest(filename=filename):
                    with self.assertRaisesRegex(ValueError, "without a path"):
                        pipeline.process_and_save(
                            [{"quote": "Example"}],
                            filename=filename,
                        )


if __name__ == "__main__":
    unittest.main()
