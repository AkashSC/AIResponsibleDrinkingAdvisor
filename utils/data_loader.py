import pandas as pd
import os

def load_csv(file_name: str) -> pd.DataFrame:
    data_path = os.path.join("data", file_name)
    return pd.read_csv(data_path)

def load_all():
    events = load_csv("rd_events.csv")
    sessions = load_csv("rd_sessions.csv")
    users = load_csv("rd_user_profiles.csv")
    bac_series = load_csv("rd_bac_series_session1.csv")
    return events, sessions, users, bac_series
