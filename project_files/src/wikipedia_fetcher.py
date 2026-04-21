"""
Wikipedia Pageviews Data Fetcher
Fetches historical pageview data for keywords from Wikipedia Pageviews API
"""

import requests
import pandas as pd
from datetime import datetime
import json
import time
from typing import Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WikipediaPageviewsFetcher:
    """
    Fetches Wikipedia pageview data for given keywords

    API: https://pageviews.toolforge.org/
    No authentication required
    """

    BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
    RATE_LIMIT_DELAY = 0.5  # seconds between requests

    def __init__(self, keywords_json_path: str):
        """
        Initialize fetcher with keywords from JSON file

        Args:
            keywords_json_path: Path to keywords.json file
        """
        with open(keywords_json_path, "r") as f:
            self.keywords_config = json.load(f)

        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "DemandRadar/1.0 (https://example.com; academic-project)"}
        )

        # Map keywords to Wikipedia article names
        self.keyword_to_article = self._build_article_mapping()

    def _build_article_mapping(self) -> Dict[str, str]:
        """
        Build mapping from keywords to Wikipedia article names
        Using the mapping from API_GUIDE.md
        """
        mapping = {
            "influenza": "Influenza",
            "common cold": "Common_cold",
            "flu": "Influenza",  # Redirect to Influenza
            "respiratory infection": "Respiratory_infection",
            "cough": "Cough",
            "fever": "Fever",
            "sore throat": "Pharyngitis",
            "chills": "Chills",
            "nasal congestion": "Rhinitis",
            "runny nose": "Rhinorrhea",
            "body aches": "Myalgia",
            "fatigue": "Fatigue",
            "decongestant": "Decongestant",
            "antihistamine": "Antihistamine",
            "acetaminophen": "Acetaminophen",
            "ibuprofen": "Ibuprofen",
            "cough medicine": "Antitussive",
            "lozenges": "Lozenge",
        }
        return mapping

    def _build_date_range(self, start_date: str, end_date: str) -> Tuple[str, str]:
        """Convert YYYYMM dates into Wikimedia API timestamps."""
        start_ts = datetime.strptime(f"{start_date}01", "%Y%m%d").strftime("%Y%m%d")
        end_month = datetime.strptime(f"{end_date}01", "%Y%m%d")
        # Wikimedia accepts dates beyond month length (e.g., 31), so use 31 for simplicity.
        end_ts = end_month.strftime("%Y%m") + "31"
        return start_ts, end_ts

    def fetch_pageviews(
        self, keyword: str, start_date: str, end_date: str, granularity: str = "monthly"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch pageview data for a keyword

        Args:
            keyword: Keyword to fetch (must be in keywords_config)
            start_date: Start date in YYYYMM format (e.g., '202501')
            end_date: End date in YYYYMM format (e.g., '202603')
            granularity: 'daily', 'monthly' (default)

        Returns:
            DataFrame with columns [date, pageviews] or None if failed
        """

        if keyword not in self.keyword_to_article:
            logger.warning(f"Keyword '{keyword}' not found in mapping. Skipping.")
            return None

        article_name = self.keyword_to_article[keyword]

        if granularity not in {"daily", "monthly"}:
            logger.error(
                f"Invalid granularity '{granularity}'. Use 'daily' or 'monthly'."
            )
            return None

        start_ts, end_ts = self._build_date_range(start_date, end_date)

        # Build URL using Wikimedia REST API format
        url = (
            f"{self.BASE_URL}/en.wikipedia/all-access/user/"
            f"{article_name}/{granularity}/{start_ts}/{end_ts}"
        )

        logger.info(f"Fetching pageviews for '{keyword}' ({article_name})...")

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            data = response.json()

            if "items" not in data or len(data["items"]) == 0:
                logger.warning(f"No data returned for '{keyword}'")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(data["items"])
            df["keyword"] = keyword
            df["article"] = article_name

            # Parse timestamp (format: YYYYMMDD00)
            df["date"] = pd.to_datetime(
                df["timestamp"].astype(str).str[:8], format="%Y%m%d"
            )

            # Rename views column to pageviews
            df = df.rename(columns={"views": "pageviews"})

            # Keep relevant columns
            df = df[["date", "keyword", "article", "pageviews"]]

            logger.info(f"✓ Successfully fetched {len(df)} records for '{keyword}'")

            # Rate limiting
            time.sleep(self.RATE_LIMIT_DELAY)

            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to fetch '{keyword}': {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"✗ Invalid JSON response for '{keyword}'")
            return None

    def fetch_all_keywords(
        self, start_date: str, end_date: str, granularity: str = "monthly"
    ) -> pd.DataFrame:
        """
        Fetch pageviews for all keywords in keywords_config

        Args:
            start_date: Start date in YYYYMM format
            end_date: End date in YYYYMM format
            granularity: 'daily' or 'monthly'

        Returns:
            Combined DataFrame with all keywords
        """

        all_data = []
        keywords = [kw["keyword"] for kw in self.keywords_config["keywords"]]

        logger.info(
            f"Fetching data for {len(keywords)} keywords from {start_date} to {end_date}..."
        )

        for keyword in keywords:
            df = self.fetch_pageviews(keyword, start_date, end_date, granularity)
            if df is not None:
                all_data.append(df)

        if not all_data:
            logger.error("No data fetched for any keyword!")
            return pd.DataFrame()

        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values(["date", "keyword"]).reset_index(
            drop=True
        )

        logger.info(f"✓ Combined data: {len(combined_df)} total records")

        return combined_df

    def save_to_csv(self, df: pd.DataFrame, output_path: str):
        """Save dataframe to CSV"""
        df.to_csv(output_path, index=False)
        logger.info(f"✓ Saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    fetcher = WikipediaPageviewsFetcher("keywords.json")

    # Fetch data for past 6 months (Oct 2025 - Mar 2026)
    df = fetcher.fetch_all_keywords(
        start_date="202510", end_date="202603", granularity="monthly"
    )

    if not df.empty:
        print("\nSample of fetched data:")
        print(df.head(10))

        # Save to CSV
        fetcher.save_to_csv(df, "wikipedia_monthly_data.csv")
