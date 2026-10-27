from pathlib import Path
from typing import Any

import pandas as pd


class DataPipeline:
    def __init__(self, output_dir: str = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_and_save(
        self,
        raw_data: list[dict[str, Any]],
        filename: str = "scraped_data",
    ) -> dict[str, str | int]:
        """
        Cleans extracted records, converts them to a DataFrame, and exports CSV and Excel.
        """
        if not raw_data:
            raise ValueError("No data provided to pipeline.")
        if not filename or Path(filename).name != filename or filename in {".", ".."}:
            raise ValueError("filename must be a non-empty file name without a path.")

        df = pd.DataFrame(raw_data)
        df = df.drop_duplicates()
        df.columns = [column.strip().lower().replace(" ", "_") for column in df.columns]

        csv_path = self.output_dir / f"{filename}.csv"
        excel_path = self.output_dir / f"{filename}.xlsx"

        df.to_csv(csv_path, index=False)
        df.to_excel(excel_path, index=False, engine="openpyxl")

        return {
            "csv_path": str(csv_path),
            "excel_path": str(excel_path),
            "row_count": len(df),
        }
