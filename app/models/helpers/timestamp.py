import sqlalchemy as sa
from sqlalchemy import func


class Timestamp:
    created_at = sa.Column(sa.DateTime(timezone=True), default=func.now())
    modified_at = sa.Column(
        sa.DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
