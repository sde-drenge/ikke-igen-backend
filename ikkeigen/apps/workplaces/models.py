from django.core.cache import cache
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from users.models import BaseModel, User


class Category(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class TopCategory(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    categories = models.ManyToManyField(
        Category, related_name="top_categories", blank=True
    )

    def __str__(self):
        return self.name


class Workplace(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    vat = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name="workplaces", blank=True)

    def __str__(self):
        return f"{self.name} - {self.vat}"


class Review(BaseModel):
    stars = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField()
    title = models.CharField(max_length=255)

    author = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="workplace_reviews"
    )
    workplace = models.ForeignKey(
        Workplace, on_delete=models.CASCADE, related_name="reviews"
    )

    verifiedBy = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="verifiedWorkPlaceReviews",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Review by {self.author} for {self.workplace}: {self.stars} stars"

    def deleteCache(self):
        workplace: Workplace = self.workplace

        cacheKeys = [
            f"workplace:{workplace.pk}:AverageStars",
            f"workplace:{workplace.pk}:amountOfReviews",
            f"workplace:{workplace.pk}:reviews:page:1",
        ]

        for cachekey in cacheKeys:
            cache.delete(cachekey)


@receiver(pre_save, sender=Category)
@receiver(pre_save, sender=TopCategory)
def deleteCacheOnCategoryChange(sender, instance=None, **kwargs):
    if not instance.pk:
        return

    category = sender.objects.filter(pk=instance.pk).first()
    if not category:
        return

    fields = [
        "name",
        "top_categories",
        "categories",
        "deletedAt",
    ]

    hasImportantChange = False
    for field in fields:
        old_value = getattr(category, field)
        new_value = getattr(instance, field)
        if old_value != new_value:
            hasImportantChange = True
            break

    if hasImportantChange:
        cacheKey = "workplace:categories"
        cache.delete(cacheKey)


@receiver(pre_save, sender=Review)
def deleteCacheOnReviewChange(sender, instance=None, **kwargs):
    if not instance.pk:
        return

    review = Review.objects.filter(pk=instance.pk).first()
    if not review:
        return

    # Check for any changes in these fields
    fields = [
        "stars",
        "verifiedBy",
        "workplace",
        "deletedAt",
    ]
    hasImportantChange = False
    for field in fields:
        old_value = getattr(review, field)
        new_value = getattr(instance, field)
        if old_value != new_value:
            hasImportantChange = True
            break

    if hasImportantChange:
        # Updating workplace stars
        review.deleteCache()
