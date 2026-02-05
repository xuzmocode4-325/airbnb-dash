import pandas as pd
from typing import List


class NormaliseReviews:
    """Utilities to normalise and split a reviews DataFrame into smaller tables.

    This class accepts a DataFrame (expected to come from an Airbnb reviews export)
    and exposes methods that return DataFrames for downstream processing / loading
    into relational stores.

    Attributes:
        df: The original reviews DataFrame supplied at construction.
    """

    def __init__(self, reviews: pd.DataFrame) -> None:
        """Store the incoming DataFrame.

        Args:
            reviews: Raw reviews DataFrame with columns such as
                'id', 'reviewer_id', 'reviewer_name', 'listing_id', 'comments', 'date'.
        """
        self.df = reviews
        self.preprocessed = self._general_reviews_preprocessing()


    def _general_reviews_preprocessing(self) -> pd.DataFrame:
        """Apply common preprocessing steps to the reviews DataFrame.

        Steps performed:
        - Drop rows with all NA values
        - Drop exact duplicate rows
        - Convert id columns to integers

        Returns:
            A cleaned DataFrame with rows containing all NA values and exact
            duplicates removed.
        """
        df = self.df.copy()
        # Remove rows with all missing values and exact duplicates.
        df = df.dropna(axis=0, how='all').drop_duplicates()
        # Convert id columns to integers
        for col in df.columns:
            if "id" in col:
                df[col] = df[col].astype(int)
        return df


    def normalise_reviewers(self) -> pd.DataFrame:
        """Return a deduplicated table of reviewers.

        The returned DataFrame contains unique pairs of `reviewer_id` and
        `reviewer_name`. Useful as a lightweight 'users' table.

        Returns:
            A DataFrame with columns ['reviewer_id', 'reviewer_name'] and
            duplicates dropped.
        """
        df = self.preprocessed
        # Select only the reviewer identifying columns and remove duplicates.
        users = df[['reviewer_id', 'reviewer_name']].drop_duplicates()
        return users


    def normalise_reviews(self) -> pd.DataFrame:
        """Return a deduplicated reviews table with canonical column names.

        Performs the following transformations:
        - Drops rows containing NA values (entire row NA)
        - Drops exact duplicate rows
        - Renames 'id' -> 'review_id'
        - Removes reviewer_name (to avoid duplication with the reviewers table)
        - Restricts columns to the commonly used review fields

        Returns:
            A DataFrame with columns ['review_id', 'reviewer_id', 'listing_id',
            'comments', 'date'] and duplicates removed.
        """
        df = self.preprocessed
        # Remove rows with any missing values and exact duplicates.
        new_df = df.dropna(axis=0).drop_duplicates()
        # Rename the primary key column to a more explicit name.
        new_df.rename(columns={'id': 'review_id'}, inplace=True)
        # We keep reviewer references by id only; textual reviewer_name is stored
        # in the reviewers table to avoid redundancy.
        new_df = new_df.drop(columns=['reviewer_name'])
        new_df = new_df[['review_id', 'reviewer_id', 'listing_id', 'comments', 'date']]
        return new_df


class NormaliseListings:
    """Split and normalise a listings DataFrame into related tables.

    The class performs light preprocessing (renaming, boolean conversion,
    simple neighbourhood id extraction) then offers a suite of methods that
    return DataFrames representing hosts, neighbourhoods, availabilities, etc.
    """

    def __init__(self, listings: pd.DataFrame) -> None:
        """Initialise with the raw listings DataFrame and run preprocessing.

        Args:
            listings: Raw listings DataFrame from an Airbnb export.
        """
        self.df = listings
        # Run general preprocessing once and reuse the result for all normalisers.
        self.preprocessed = self._general_listings_preprocessing()
        # Construct a list of columns to drop when creating the flattened listings
        # relation. This is derived from the preprocessed DataFrame.
        self.droplist = self._construct_droplist()


    def _construct_droplist(self) -> List[str]:
        """Build a list of columns to drop from the listings relation.

        The method collects all columns containing certain keywords and
        filters out identifier columns so that joined tables can keep ids.
        """
        df = self.preprocessed

        keys = ['neighbourhood', 'host', 'availability', 'nights', 'review', 'scrape']

        droplist: List[str] = []
        for key in keys:
            # Aggregate any column that contains the keyword
            subset = [col for col in df.columns if key in col]
            droplist += subset

        # Remove columns that include 'id' — those are the keys we'll keep.
        droplist = [col for col in droplist if 'id' not in col]
        # Explicitly drop hosting identity verification flags from the flattened
        # relation; they are better represented in the hosts table.
        droplist += ['host_identity_verified']
        return droplist


    def _extract_url_cols(self, df: pd.DataFrame, id_str: str, drop: bool) -> pd.DataFrame:
        """Either drop URL columns or return the id + url columns deduplicated.

        Args:
            df: DataFrame to operate on.
            id_str: The column name to treat as the id (must exist in df).
            drop: If True, remove all columns containing 'url' and return df.
                  If False, return a DataFrame with the id column and all url
                  columns, with duplicates removed.

        Returns:
            A DataFrame: either the input with url columns removed, or a small
            deduplicated DataFrame containing the id and url columns.
        """
        url_cols = [col for col in df.columns if 'url' in col]

        if drop:
            # Remove URL columns from the provided DataFrame.
            df = df.drop(columns=url_cols)
            return df
        else:
            # Locate the id column position robustly and return id + url cols.
            id_col = df.columns[df.columns.get_loc(id_str)]
            return df[[id_col] + url_cols].drop_duplicates()


    def _general_listings_preprocessing(self) -> pd.DataFrame:
        """Apply common preprocessing steps to the listings DataFrame.

        Steps performed:
        - Drop listings missing night-related columns
        - Drop columns with >90% missing values
        - Rename some columns to more explicit names
        - Extract a simplified neighbourhood id
        - Convert common boolean-like string flags to real booleans
        """
        df = self.df.copy()
        night_data_cols = [col for col in df.columns if 'nights' in col]
        # Ensure rows missing essential night data are removed.
        df.dropna(subset=night_data_cols, inplace=True)
        # Drop columns that are mostly empty (keeping columns with at least
        # 10% non-null values).
        df.dropna(thresh=int(0.1 * df.shape[0]), axis=1, inplace=True)
        df.rename(
            columns={
                'id': 'listing_id',
                'source': 'scrape_source',
                'neighborhood_overview': 'neighbourhood_overview',
            },
            inplace=True,
        )
        # Create a neighbourhood id by stripping known prefixes; this is a
        # lightweight transformation suitable for grouping.
        df['neighbourhood_id'] = df['neighbourhood_cleansed'].str.replace('Ward', '').str.strip()
        
        # Convert common boolean-like flags encoded as 't'/'f' to real bools.
        bool_cols = [
            'has_availability', 'instant_bookable', 'host_is_superhost',
            'host_has_profile_pic', 'host_identity_verified'
        ]
        
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col] == 't'
        
        # Convert id columns to integers
        for col in df.columns:
            if "id" in col and col not in bool_cols:
                df[col] = df[col].astype(int)
        
        return df


    def normalise_hosts(self) -> pd.DataFrame:
        """Return a hosts table with host-specific columns.

        The method selects all columns containing 'host', drops duplicates and
        removes url columns (which are typically not needed in the flattened
        hosts table) using _extract_url_cols.
        """
        df = self.preprocessed
        # Collect host-related columns and deduplicate
        host_cols = [col for col in df.columns if 'host' in col]
        hosts = df[host_cols].drop_duplicates()

        # Remove url columns from the hosts relation (they will be handled
        # separately if required).
        hosts = self._extract_url_cols(hosts, 'host_id', drop=True)
        
        # Convert rate columns to float
        for col in hosts.columns:
            if 'rate' in col:
                hosts[col] = hosts[col].str.replace('%', '').astype('Float64')
        
        # Convert object columns to string (except id and boolean columns)
        bool_cols = ['host_is_superhost', 'host_has_profile_pic', 'host_identity_verified']
        for col in hosts.columns:
            if 'id' not in col and col not in bool_cols and hosts[col].dtype == 'object':
                hosts[col] = hosts[col].astype('string')

        # Boolean columns are already converted in preprocessing, but handle if they're not
        for col in bool_cols:
            if col in hosts.columns and hosts[col].dtype != 'bool':
                # Map various representations to boolean values
                hosts[col] = hosts[col].map({True: True, False: False, 't': True, 'f': False, 
                                            'True': True, 'False': False, 1: True, 0: False}).astype('boolean')

        return hosts


    def normalise_neighbourhoods(self) -> pd.DataFrame:
        """Return a minimal neighbourhoods table (id + name).

        Useful for building a lookup table for neighbourhood metadata.
        """
        df = self.preprocessed
        neighborhoods = df[['neighbourhood_id', 'neighbourhood_cleansed']].drop_duplicates()
        return neighborhoods


    def normalise_neighbourhood_overview(self) -> pd.DataFrame:
        """Return neighbourhood overview text associated with listings.

        This keeps the longer 'neighbourhood_overview' text alongside listing and
        neighbourhood ids so the descriptions can be linked back to listings.
        """
        df = self.preprocessed
        neighborhoods = df[['listing_id', 'neighbourhood_id', 'neighbourhood', 'neighbourhood_overview']].drop_duplicates()
        return neighborhoods


    def normalise_availabilities(self) -> pd.DataFrame:
        """Return availability-related columns keyed by `listing_id`.

        The method collects all columns containing the word 'availability' and
        returns them together with the listing identifier.
        """
        df = self.preprocessed
        availability_cols = [col for col in df.columns if 'availability' in col]
        availability = df[['listing_id'] + availability_cols]
        return availability


    def normalise_night_data(self) -> pd.DataFrame:
        """Return night-related metrics keyed by `listing_id`.

        Collects columns containing 'nights' (e.g. minimum_nights, maximum_nights)
        and returns them for analysis or loading into a dedicated table.
        """
        df = self.preprocessed
        nights_cols = [col for col in df.columns if 'nights' in col]
        nights_data = df[['listing_id'] + nights_cols]
        return nights_data


    def normalise_listing_reviews(self) -> pd.DataFrame:
        """Return listing-level review metrics keyed by `listing_id`.

        Gathers any column containing 'review' (review scores, counts, etc.)
        and returns them with the listing id.
        """
        df = self.preprocessed
        reviews_cols = [col for col in df.columns if 'review' in col]
        reviews = df[['listing_id'] + reviews_cols]
        return reviews


    def normalise_scrape_details(self) -> pd.DataFrame:
        """Return unique scrape-related metadata.

        This captures fields like `scrape_source` or timestamps related to when
        the listing was scraped and deduplicates them.
        """
        df = self.preprocessed
        scrape_cols = [col for col in df.columns if 'scrape' in col]
        scrapes = df[scrape_cols].drop_duplicates()
        return scrapes


    def normalise_listings(self) -> pd.DataFrame:
        """Return a flattened listings relation with non-relational columns removed.

        This method drops columns collected in `self.droplist` (which typically
        represent attributes better stored in separate tables) and also removes
        url columns via `_extract_url_cols`.
        """
        df = self.preprocessed
        listings_df = df.drop(columns=self.droplist)
        listings_df = self._extract_url_cols(listings_df, 'listing_id', drop=True)
        listings_df.rename(columns={'price': 'price_usd'}, inplace=True)
        listings_df['price_usd'] = listings_df['price_usd'].str.replace('$', '').str.replace(',', '').astype('Float64')
        listings_df['listing_id'] = listings_df['listing_id'].astype(int)
        listings_df['room_type'] = listings_df['room_type'].str.replace('home/apt', 'residence')
        listings_df['property_type'] = listings_df['property_type'].str.replace('Entire', '')
        listings_df['property_type'] = listings_df['property_type'].str.replace('Private', '')
        listings_df['property_type'] = listings_df['property_type'].str.lower().str.strip().astype('category')
        listings_df['room_type'] = listings_df['room_type'].str.lower().str.strip().astype('category')
        return listings_df