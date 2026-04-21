"""
GDELT News Mentions Data Fetcher
Fetches historical news mention counts for keywords from GDELT API
"""

import requests
import pandas as pd
import json
import time
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GDELTNewsFetcher:
    """
    Fetches GDELT news mention data for given keywords

    API: https://api.gdelt.org/api/v2/search/gkg
    Uses GDELT 2.0 Search API
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
    RATE_LIMIT_DELAY = 5.2  # GDELT requires roughly one request every 5 seconds
    MAX_RETRIES = 5

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
        self._last_request_ts = 0.0

    def _respect_rate_limit(self):
        elapsed = time.time() - self._last_request_ts
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)

    def fetch_mentions(
        self, keyword: str, timespan: str = "90d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch news mention counts for a keyword using GDELT timeline mode

        Args:
            keyword: Keyword to search for
            timespan: Time span for query (e.g., '90d', '1y', '6m')

        Returns:
            DataFrame with columns [date, keyword, mention_count] or None if failed
        """

        params = {
            "query": keyword,
            "mode": "timelinevolraw",
            "timespan": timespan,
            "format": "json",
        }

        logger.info(
            f"Fetching GDELT mentions for '{keyword}' (timespan: {timespan})..."
        )

        try:
            response = None
            for attempt in range(1, self.MAX_RETRIES + 1):
                self._respect_rate_limit()
                response = self.session.get(self.BASE_URL, params=params, timeout=20)
                self._last_request_ts = time.time()
                if response.status_code == 429 and attempt < self.MAX_RETRIES:
                    wait_seconds = self.RATE_LIMIT_DELAY * (attempt + 1)
                    logger.warning(
                        f"Rate limited for '{keyword}'. Retrying in {wait_seconds:.1f}s..."
                    )
                    time.sleep(wait_seconds)
                    continue
                response.raise_for_status()
                break

            payload = response.json()
            timeline = payload.get("timeline", [])
            if not timeline:
                logger.warning(f"No timeline returned for '{keyword}'")
                return None

            data_points = timeline[0].get("data", [])
            if not data_points:
                logger.warning(f"No data points returned for '{keyword}'")
                return None

            df = pd.DataFrame(data_points)
            df["date"] = pd.to_datetime(
                df["date"], format="%Y%m%dT%H%M%SZ", errors="coerce"
            )
            df = df.dropna(subset=["date"])
            df["keyword"] = keyword
            df = df.rename(
                columns={"value": "mention_count", "norm": "normalized_mentions"}
            )
            df["source_count"] = pd.NA
            df = df[
                [
                    "date",
                    "keyword",
                    "mention_count",
                    "source_count",
                    "normalized_mentions",
                ]
            ]

            logger.info(f"✓ Successfully fetched {len(df)} records for '{keyword}'")

            return df

        except requests.exceptions.Timeout:
            logger.error(f"✗ Timeout fetching '{keyword}' (GDELT may be slow)")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to fetch '{keyword}': {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"✗ Invalid JSON response for '{keyword}': {e}")
            return None

    def fetch_all_keywords(self, timespan: str = "90d") -> pd.DataFrame:
        """
        Fetch news mentions for all keywords in keywords_config

        Args:
            timespan: Time span for query (e.g., '90d', '1y')

        Returns:
            Combined DataFrame with all keywords
        """

        all_data = []
        keywords = [kw["keyword"] for kw in self.keywords_config["keywords"]]

        logger.info(f"Fetching GDELT data for {len(keywords)} keywords...")

        for index, keyword in enumerate(keywords, start=1):
            logger.info(f"GDELT progress {index}/{len(keywords)}: starting '{keyword}'")
            started_at = time.time()
            df = self.fetch_mentions(keyword, timespan)
            elapsed_seconds = time.time() - started_at
            if df is not None:
                all_data.append(df)
                logger.info(
                    f"GDELT progress {index}/{len(keywords)}: finished '{keyword}' in {elapsed_seconds:.1f}s with {len(df)} rows"
                )
            else:
                logger.warning(
                    f"GDELT progress {index}/{len(keywords)}: skipped '{keyword}' after {elapsed_seconds:.1f}s"
                )

        if not all_data:
            logger.error("No data fetched for any keyword!")
            return pd.DataFrame()

        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values(["date", "keyword"]).reset_index(
            drop=True
        )

        logger.info(f"✓ Combined GDELT data: {len(combined_df)} total records")

        return combined_df

    def save_to_csv(self, df: pd.DataFrame, output_path: str):
        """Save dataframe to CSV"""
        df.to_csv(output_path, index=False)
        logger.info(f"✓ Saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    fetcher = GDELTNewsFetcher("keywords.json")

    # Fetch GDELT data for past 90 days
    df = fetcher.fetch_all_keywords(timespan="90d")

    if not df.empty:
        print("\nSample of fetched data:")
        print(df.head(10))

        # Save to CSV
        fetcher.save_to_csv(df, "gdelt_news_data.csv")
