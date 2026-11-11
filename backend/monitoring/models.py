import uuid

from django.db import models
from django.utils import timezone


class Post(models.Model):
    class Platform(models.TextChoices):
        TWITTER = "TWITTER", "Twitter / X"
        LINKEDIN = "LINKEDIN", "LinkedIn"
        YOUTUBE = "YOUTUBE", "YouTube"
        REDDIT = "REDDIT", "Reddit"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.CharField(max_length=50, choices=Platform.choices)
    platform_post_id = models.CharField(max_length=255)
    account_handle = models.CharField(max_length=255)

    text = models.TextField(blank=True, default="")
    url = models.URLField(max_length=500)

    # Timestamps
    published_at = models.DateTimeField()
    collected_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        constraints = (
            # Enforces uniqueness ONLY per platform + post ID combination
            models.UniqueConstraint(
                fields=["platform", "platform_post_id"],
                name="unique_platform_post_id",
            ),
        )

    def __str__(self):
        return f"[{self.platform}] @{self.account_handle} - {self.platform_post_id}"
