from rest_framework.permissions import IsAuthenticated

from .models import (
    SubscriptionTier,
    SubscriptionFeature,
    SubscriptionPlan,
    PlanFeature,
    UserSubscription
)
from .serializers import (
    SubscriptionTierSerializer,
    SubscriptionFeatureSerializer,
    SubscriptionPlanSerializer,
    PlanFeatureSerializer,
    UserSubscriptionSerializer,
)

class SubscriptionTierUtil:
    queryset = SubscriptionTier.objects.all()
    serializer_class = SubscriptionTierSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionFeatureUtil:
    queryset = SubscriptionFeature.objects.all()
    serializer_class = SubscriptionFeatureSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionPlanUtil:
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]


class PlanFeatureUtil:
    queryset = PlanFeature.objects.all()
    serializer_class = PlanFeatureSerializer
    permission_classes = [IsAuthenticated]


class UserSubscriptionUtil:
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]
