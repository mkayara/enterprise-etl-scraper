import asyncio
from pathlib import Path

import pandas as pd
import streamlit as st
from playwright.async_api import Error as PlaywrightError

from app.pipelines.etl import DataPipeline
from app.scrapers.engine import WebScraperEngine


st.set_page_config(
    page_title="Enterprise ETL & Scraping Dashboard",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Enterprise ETL & Web Scraping Suite")
st.markdown(
    "Automated data ingestion framework featuring modular Playwright extraction, "
    "Pandas cleaning pipelines, and multi-format exports."
)

st.sidebar.header("Pipeline Controls")
record_limit = st.sidebar.slider(
    "Extraction Limit (Records)",
    min_value=1,
    max_value=25,
    value=5,
)
run_button = st.sidebar.button("Run Extraction & ETL Pipeline", type="primary")

data_dir = Path(__file__).resolve().parents[2] / "data"
data_dir.mkdir(parents=True, exist_ok=True)
csv_path = data_dir / "latest_scrape.csv"
excel_path = data_dir / "latest_scrape.xlsx"

if run_button:
    with st.spinner("Executing Playwright scraper and processing data pipeline..."):
        try:
            scraper = WebScraperEngine(headless=True)
            raw_data = asyncio.run(scraper.scrape_quotes(limit=record_limit))
            result = DataPipeline(output_dir=str(data_dir)).process_and_save(
                raw_data,
                filename="latest_scrape",
            )
        except (PlaywrightError, OSError, ValueError) as error:
            st.sidebar.error(f"Pipeline failed: {error}")
            st.exception(error)
        else:
            st.sidebar.success(
                f"Successfully processed {result['row_count']} rows!"
            )

if csv_path.is_file():
    df = pd.read_csv(csv_path)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Processed Dataset Preview")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📈 Quick Statistics & Info")
        st.metric(label="Total Records Extracted", value=len(df))
        st.metric(label="Columns Detected", value=len(df.columns))

        st.markdown("### Download Exports")
        st.download_button(
            "Download CSV",
            data=csv_path.read_bytes(),
            file_name=csv_path.name,
            mime="text/csv",
        )
        if excel_path.is_file():
            st.download_button(
                "Download Excel (.xlsx)",
                data=excel_path.read_bytes(),
                file_name=excel_path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.info("Excel export is not available yet.")
else:
    st.info("No scraped dataset found. Use the sidebar controls to run your first extraction job.")
