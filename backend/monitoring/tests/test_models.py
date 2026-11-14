import pytest
from django.db import IntegrityError
from django.utils import timezone

from monitoring.models import Post, PostAnalysis


@pytest.mark.django_db
def test_create_valid_post():
    post = Post.objects.create(
        platform=Post.Platform.TWITTER,
        platform_post_id="1855678901234567890",
        account_handle="dev_lead",
        url="https://x.com/dev_lead/status/1855678901234567890",
        published_at=timezone.now(),
    )
    assert post.pk is not None
    assert Post.objects.count() == 1


@pytest.mark.django_db
def test_duplicate_platform_and_post_id_fails():
    Post.objects.create(
        platform=Post.Platform.TWITTER,
        platform_post_id="1001",
        account_handle="user_one",
        url="https://x.com/user_one/status/1001",
        published_at=timezone.now(),
    )

    with pytest.raises(IntegrityError):
        Post.objects.create(
            platform=Post.Platform.TWITTER,
            platform_post_id="1001",
            account_handle="user_two",
            url="https://x.com/user_two/status/1001",
            published_at=timezone.now(),
        )


@pytest.mark.django_db
def test_same_post_id_different_platforms_succeeds():
    Post.objects.create(
        platform=Post.Platform.TWITTER,
        platform_post_id="1001",
        account_handle="user_one",
        url="https://x.com/user_one/status/1001",
        published_at=timezone.now(),
    )
    reddit_post = Post.objects.create(
        platform=Post.Platform.REDDIT,
        platform_post_id="1001",
        account_handle="user_one",
        url="https://reddit.com/r/python/comments/1001",
        published_at=timezone.now(),
    )

    assert Post.objects.count() == 2
    assert reddit_post.pk is not None


@pytest.mark.django_db
def test_create_valid_post_analysis():
    post = Post.objects.create(
        platform=Post.Platform.TWITTER,
        platform_post_id="2001",
        account_handle="user_one",
        url="https://x.com/user_one/status/2001",
        published_at=timezone.now(),
    )
    analysis = PostAnalysis.objects.create(
        post=post,
        category=PostAnalysis.Category.HOSTILITY,
        confidence=0.87,
        requires_review=True,
    )

    analysis.refresh_from_db()
    assert analysis.post == post
    assert analysis.category == PostAnalysis.Category.HOSTILITY
    assert analysis.confidence == 0.87
    assert analysis.requires_review is True


@pytest.mark.django_db
def test_post_can_have_multiple_analyses():
    post = Post.objects.create(
        platform=Post.Platform.TWITTER,
        platform_post_id="2002",
        account_handle="user_one",
        url="https://x.com/user_one/status/2002",
        published_at=timezone.now(),
    )
    PostAnalysis.objects.create(
        post=post, category=PostAnalysis.Category.NONE, confidence=0.4
    )
    PostAnalysis.objects.create(
        post=post, category=PostAnalysis.Category.THREAT, confidence=0.9
    )

    assert post.analyses.count() == 2  # pyright: ignore[reportAttributeAccessIssue]


@pytest.mark.django_db
@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_confidence_outside_range_fails(confidence):
    post = Post.objects.create(
        platform=Post.Platform.TWITTER,
        platform_post_id="2003",
        account_handle="user_one",
        url="https://x.com/user_one/status/2003",
        published_at=timezone.now(),
    )

    with pytest.raises(IntegrityError):
        PostAnalysis.objects.create(post=post, confidence=confidence)
