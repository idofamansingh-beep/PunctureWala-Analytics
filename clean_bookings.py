from pathlib import Path
import pandas as pd

VALID_STATUSES = {"Accepted", "Cancelled", "Completed", "Pending", "Rejected"}
NUMERIC_COLUMNS = [
    "booking_hour", "service_charge", "discount", "final_amount",
    "response_time_minutes", "repair_time_minutes", "customer_rating",
]

def clean_bookings(bookings: pd.DataFrame) -> pd.DataFrame:
    cleaned = bookings.copy()

    # Remove spaces and make blank text values missing.
    for column in cleaned.select_dtypes(include="object"):
        cleaned[column] = cleaned[column].str.strip().replace("", pd.NA)

    # Convert fields into useful data types; malformed values become NaN.
    cleaned["booking_datetime"] = pd.to_datetime(cleaned["booking_datetime"], errors="coerce")
    cleaned["booking_date"] = pd.to_datetime(cleaned["booking_date"], errors="coerce")
    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    # Only remove true duplicate rows and records without a booking ID.
    cleaned = cleaned.drop_duplicates().dropna(subset=["booking_id"])

    # Flag invalid values rather than guessing replacements.
    cleaned.loc[~cleaned["booking_status"].isin(VALID_STATUSES), "booking_status"] = pd.NA
    cleaned.loc[~cleaned["booking_hour"].between(0, 23), "booking_hour"] = pd.NA
    cleaned.loc[~cleaned["customer_rating"].between(1, 5), "customer_rating"] = pd.NA

    # Do not impute repair/rating for non-completed bookings or response time for rejected bookings.
    return cleaned

if __name__ == "__main__":
    root = Path(__file__).parent
    cleaned = clean_bookings(pd.read_csv(root / "data" / "bookings.csv"))
    cleaned.to_csv(root / "data" / "bookings_cleaned.csv", index=False)
