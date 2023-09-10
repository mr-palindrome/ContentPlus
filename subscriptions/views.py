from rest_framework import generics

from .mixins import (
    SubscriptionTierUtil,
    SubscriptionPlanUtil,
    SubscriptionFeatureUtil,
    PlanFeatureUtil,
    UserSubscriptionUtil,
)


class SubscriptionTierList(generics.ListCreateAPIView, SubscriptionTierUtil):
    pass

class SubscriptionTierDetail(generics.RetrieveUpdateDestroyAPIView, SubscriptionTierUtil):
    pass

class SubscriptionFeatureList(generics.ListCreateAPIView, SubscriptionFeatureUtil):
    pass

class SubscriptionFeatureDetail(generics.RetrieveUpdateDestroyAPIView, SubscriptionFeatureUtil):
    pass

class SubscriptionPlanList(generics.ListCreateAPIView, SubscriptionPlanUtil):
    pass

class SubscriptionPlanDetail(generics.RetrieveUpdateDestroyAPIView, SubscriptionPlanUtil):
    pass

class PlanFeatureList(generics.ListCreateAPIView, PlanFeatureUtil):
    pass

class PlanFeatureDetail(generics.RetrieveUpdateDestroyAPIView, PlanFeatureUtil):
    pass

class UserSubscriptionList(generics.ListCreateAPIView, UserSubscriptionUtil):
    pass

class UserSubscriptionDetail(generics.RetrieveUpdateDestroyAPIView, UserSubscriptionUtil):
    pass
