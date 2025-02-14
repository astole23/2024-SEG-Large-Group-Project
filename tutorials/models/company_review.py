from django.db import models

class Review(models.Model):
    text = models.TextField(max_length=2000, blank=False)  # Limit review length
    rating = models.PositiveIntegerField(default=1)  # Default rating to 1

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), name="rating_range"),  # Rating between 1 and 5
        ]

    def __str__(self):
        return f"Review ({self.rating}/5): {self.text[:50]}"  # Show a preview of the review
