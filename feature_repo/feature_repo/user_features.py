from datetime import timedelta
import pandas as pd
from feast import (
    Entity,
    FeatureView,
    Field,
    FileSource,
    PushSource,
    RequestSource,
)
from feast.types import Int64, String

# Define the user entity
user = Entity(name="user", join_keys=["user_id"])

# File source for user features
user_stats_source = FileSource(
    path="/home/franz/Documents/Prompt Project/feature_repo/feature_repo/data/user_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# Feature view for user statistics
user_features_view = FeatureView(
    name="user_features",
    entities=[user],
    ttl=timedelta(days=1),
    schema=[
        Field(name="expertise_level", dtype=String),
        Field(name="preferred_language", dtype=String),
        Field(name="last_task_type", dtype=String),
    ],
    online=True,
    source=user_stats_source,
    tags={"team": "prompt_engineering"},
)
