from django.contrib import admin
from .models import (
    SubscriptionTier,
    SubscriptionFeature,
    SubscriptionPlan,
    PlanFeature,
    UserSubscription
)

# Register your models here.

admin.site.register(SubscriptionTier)
admin.site.register(SubscriptionFeature)
admin.site.register(SubscriptionPlan)
admin.site.register(PlanFeature)
admin.site.register(UserSubscription)