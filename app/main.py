from fastapi import FastAPI, Query

from app.pipelines.etl import DataPipeline
from app.scrapers.engine import WebScraperEngine


app = FastAPI(
    title="Enterprise ETL & Scraping API",
    version="1.0.0",
    description="Automated Web Scraping and Data Ingestion Pipeline",
)

scraper = WebScraperEngine(headless=True)
pipeline = DataPipeline(output_dir="data")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "active", "service": "Enterprise ETL Scraper API"}


@app.post("/api/v1/run-etl")
async def run_etl_job(limit: int = Query(5, ge=1, le=50)) -> dict[str, object]:
    raw_data = await scraper.scrape_quotes(limit=limit)
    result = pipeline.process_and_save(raw_data, filename="latest_scrape")
    return {
        "status": "success",
        "message": f"Successfully extracted and processed {result['row_count']} records.",
        "exports": result,
    }