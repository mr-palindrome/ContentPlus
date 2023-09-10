from django.urls import path
from .views import (
    SubscriptionTierList,
    SubscriptionTierDetail,
    SubscriptionFeatureList,
    SubscriptionFeatureDetail,
    SubscriptionPlanList,
    SubscriptionPlanDetail,
    PlanFeatureList,
    PlanFeatureDetail,
    UserSubscriptionList,
    UserSubscriptionDetail,
)

urlpatterns = [
    # path('subscription-tiers/', SubscriptionTierList.as_view(), name='subscription-tier-list'),
    # path('subscription-tiers/<int:pk>/', SubscriptionTierDetail.as_view(), name='subscription-tier-detail'),
    # path('subscription-features/', SubscriptionFeatureList.as_view(), name='subscription-feature-list'),
    # path('subscription-features/<int:pk>/', SubscriptionFeatureDetail.as_view(), name='subscription-feature-detail'),
    # path('subscription-plans/', SubscriptionPlanList.as_view(), name='subscription-plan-list'),
    # path('subscription-plans/<int:pk>/', SubscriptionPlanDetail.as_view(), name='subscription-plan-detail'),
    # path('plan-features/', PlanFeatureList.as_view(), name='plan-feature-list'),
    # path('plan-features/<int:pk>/', PlanFeatureDetail.as_view(), name='plan-feature-detail'),
    # path('user-subscriptions/', UserSubscriptionList.as_view(), name='user-subscription-list'),
    # path('user-subscriptions/<int:pk>/', UserSubscriptionDetail.as_view(), name='user-subscription-detail'),
]
