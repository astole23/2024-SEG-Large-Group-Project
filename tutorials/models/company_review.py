from django.db import models
from tutorials.models.accounts import CustomUser  

class Review(models.Model):
    text = models.TextField(max_length=2000, blank=False)
    rating = models.PositiveIntegerField(default=1)
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_company': True})  # Link to companies

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), name="rating_range"),
        ]

    def __str__(self):
        return f"Review ({self.rating}/5): {self.text[:50]}"