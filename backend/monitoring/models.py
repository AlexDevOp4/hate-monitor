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


class PostAnalysis(models.Model):
    class Category(models.TextChoices):
        NONE = "NONE", "None"
        CRITICISM = "CRITICISM", "Criticism"
        HOSTILITY = "HOSTILITY", "Hostility"
        DEHUMANIZATION = "DEHUMANIZATION", "Dehumanization"
        HARASSMENT = "HARASSMENT", "Harassment"
        INCITEMENT = "INCITEMENT", "Incitement"
        THREAT = "THREAT", "Threat"
        HIGH_PRIORITY_THREAT = "HIGH_PRIORITY_THREAT", "High Priority Threat"

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="analyses")
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.NONE
    )
    confidence = models.FloatField()
    reasoning = models.TextField(blank=True, default="")
    requires_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Post Analysis"
        verbose_name_plural = "Post Analyses"
        constraints = (
            models.CheckConstraint(
                condition=models.Q(confidence__gte=0.0, confidence__lte=1.0),
                name="post_analysis_confidence_between_0_and_1",
            ),
        )

    def __str__(self):
        return f"[{self.Category(self.category).label}] Post {self.post_id}"  # pyright: ignore[reportAttributeAccessIssue]
