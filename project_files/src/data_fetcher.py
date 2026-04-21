"""
Main Data Fetcher Orchestrator
Coordinates fetching from both Wikipedia and GDELT sources
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Optional

# Import fetchers
from wikipedia_fetcher import WikipediaPageviewsFetcher
from gdelt_fetcher import GDELTNewsFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcherOrchestrator:
    """
    Orchestrates data fetching from multiple sources
    """

    def __init__(self, keywords_json_path: str, data_dir: str = "data"):
        """
        Initialize orchestrator

        Args:
            keywords_json_path: Path to keywords.json
            data_dir: Directory to save fetched data
        """
        self.keywords_path = keywords_json_path
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.wiki_fetcher = WikipediaPageviewsFetcher(keywords_json_path)
        self.gdelt_fetcher = GDELTNewsFetcher(keywords_json_path)

    def fetch_wikipedia_data(
        self, start_date: str, end_date: str, granularity: str = "monthly"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch Wikipedia pageviews data

        Args:
            start_date: YYYYMM format
            end_date: YYYYMM format
            granularity: 'daily' or 'monthly'

        Returns:
            DataFrame or None
        """
        logger.info("=" * 60)
        logger.info("FETCHING WIKIPEDIA DATA")
        logger.info("=" * 60)

        try:
            df = self.wiki_fetcher.fetch_all_keywords(start_date, end_date, granularity)

            if not df.empty:
                # Save intermediate
                output_path = self.data_dir / "wikipedia_data.csv"
                self.wiki_fetcher.save_to_csv(df, str(output_path))
                logger.info(f"Wikipedia data shape: {df.shape}")
                return df
            else:
                logger.error("Wikipedia data is empty!")
                return None

        except Exception as e:
            logger.error(f"Error fetching Wikipedia data: {e}")
            return None

    def fetch_gdelt_data(self, timespan: str = "90d") -> Optional[pd.DataFrame]:
        """
        Fetch GDELT news mentions data

        Args:
            timespan: e.g., '90d', '6m', '1y'

        Returns:
            DataFrame or None
        """
        logger.info("=" * 60)
        logger.info("FETCHING GDELT DATA")
        logger.info("=" * 60)

        try:
            df = self.gdelt_fetcher.fetch_all_keywords(timespan)

            if not df.empty:
                # Save intermediate
                output_path = self.data_dir / "gdelt_data.csv"
                self.gdelt_fetcher.save_to_csv(df, str(output_path))
                logger.info(f"GDELT data shape: {df.shape}")
                return df
            else:
                logger.error("GDELT data is empty!")
                return None

        except Exception as e:
            logger.error(f"Error fetching GDELT data: {e}")
            return None

    def fetch_all_data(
        self,
        start_date: str,
        end_date: str,
        wiki_granularity: str = "monthly",
        gdelt_timespan: str = "1y",
    ) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Fetch both Wikipedia and GDELT data

        Args:
            start_date: Wikipedia start date (YYYYMM)
            end_date: Wikipedia end date (YYYYMM)
            wiki_granularity: 'daily' or 'monthly'
            gdelt_timespan: e.g., '90d', '6m', '1y'

        Returns:
            Tuple of (wiki_df, gdelt_df)
        """

        wiki_df = self.fetch_wikipedia_data(start_date, end_date, wiki_granularity)
        gdelt_df = self.fetch_gdelt_data(gdelt_timespan)

        return wiki_df, gdelt_df

    def create_summary(self, wiki_df: pd.DataFrame, gdelt_df: pd.DataFrame):
        """Create summary of fetched data"""

        logger.info("\n" + "=" * 60)
        logger.info("DATA FETCH SUMMARY")
        logger.info("=" * 60)

        if wiki_df is not None and not wiki_df.empty:
            logger.info(f"\n📊 Wikipedia Data:")
            logger.info(f"  - Shape: {wiki_df.shape}")
            logger.info(
                f"  - Date range: {wiki_df['date'].min()} to {wiki_df['date'].max()}"
            )
            logger.info(f"  - Unique keywords: {wiki_df['keyword'].nunique()}")
            logger.info(f"  - Missing values: {wiki_df.isnull().sum().sum()}")
            logger.info(f"\n  Top 5 keywords by pageviews:")
            top_wiki = wiki_df.groupby("keyword")["pageviews"].sum().nlargest(5)
            for kw, pv in top_wiki.items():
                logger.info(f"    - {kw}: {pv:,.0f}")

        if gdelt_df is not None and not gdelt_df.empty:
            logger.info(f"\n📰 GDELT Data:")
            logger.info(f"  - Shape: {gdelt_df.shape}")
            logger.info(
                f"  - Date range: {gdelt_df['date'].min()} to {gdelt_df['date'].max()}"
            )
            logger.info(f"  - Unique keywords: {gdelt_df['keyword'].nunique()}")
            logger.info(f"  - Missing values: {gdelt_df.isnull().sum().sum()}")
            if "source_count" in gdelt_df.columns:
                logger.info(
                    f"  - Average sources per mention: {gdelt_df['source_count'].mean():.1f}"
                )
            logger.info(f"\n  Top 5 keywords by mentions:")
            top_gdelt = gdelt_df.groupby("keyword")["mention_count"].sum().nlargest(5)
            for kw, mc in top_gdelt.items():
                logger.info(f"    - {kw}: {mc:,.0f}")

        logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    import os

    # Get the src directory
    src_dir = Path(__file__).parent

    # Change to project root for relative imports
    os.chdir(src_dir.parent)

    # Initialize orchestrator
    keywords_path = "keywords.json"
    orchestrator = DataFetcherOrchestrator(keywords_path, data_dir="data")

    # Fetch data for Oct 2025 - Mar 2026 (6 months)
    logger.info("Starting data fetch pipeline...")
    wiki_df, gdelt_df = orchestrator.fetch_all_data(
        start_date="202510",
        end_date="202603",
        wiki_granularity="monthly",
        gdelt_timespan="6m",
    )

    # Create summary
    orchestrator.create_summary(wiki_df, gdelt_df)

    logger.info("\n✓ Data fetch complete! Check 'data/' directory for CSV files.")
