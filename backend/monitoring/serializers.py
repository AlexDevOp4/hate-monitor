from rest_framework import serializers

from .models import Post, PostAnalysis


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "platform",
            "platform_post_id",
            "account_handle",
            "text",
            "url",
            "published_at",
            "collected_at",
        )

        read_only_fields = ("id", "collected_at")


class PostAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostAnalysis
        fields = (
            "id",
            "post",
            "category",
            "confidence",
            "reasoning",
            "requires_review",
            "created_at",
        )

        read_only_fields = ("id", "created_at")
        extra_kwargs = {"confidence": {"min_value": 0.0, "max_value": 1.0}}  # noqa: RUF012
