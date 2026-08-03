from django.db import models

class TimeStampedActiveModel(models.Model):
    """
    Abstract base model providing audit timestamps and active status.
    """

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True