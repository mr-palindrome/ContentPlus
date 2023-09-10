from django.db import models
from django.utils import timezone

from common.models import BaseModel
from authentication.models import BaseUser

class SubscriptionTier(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

class SubscriptionFeature(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

class SubscriptionPlan(BaseModel):
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.CASCADE)
    features = models.ManyToManyField(SubscriptionFeature, through='PlanFeature')
    price_mn = models.DecimalField(max_digits=10, decimal_places=2)
    price_yr = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.tier.name

    def save(self, *args, **kwargs):
        # Automatically set the plan's name based on the associated tier's name
        self.name = self.tier.name
        super(SubscriptionPlan, self).save(*args, **kwargs)

class PlanFeature(models.Model):
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    feature = models.ForeignKey(SubscriptionFeature, on_delete=models.CASCADE)
    included = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.plan} - {self.feature}'

class UserSubscription(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.plan}"

    def is_active(self):
        """
        Check if the user's subscription is currently active.
        """
        return self.active and self.start_date <= timezone.now().date() <= self.end_date
