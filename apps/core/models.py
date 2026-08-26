from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model providing creation and modification timestamps.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Created At",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """
    Abstract base model providing active status.
    """

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Is Active",
    )

    class Meta:
        abstract = True


class TimeStampedActiveModel(
    TimeStampedModel,
    ActiveModel,
):
    """
    Abstract base model providing audit timestamps and active status.
    """

    class Meta:
        abstract = True