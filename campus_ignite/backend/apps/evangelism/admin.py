from django.contrib import admin
from .models import EvangelismCampaign, CampaignCellGoal, Recruit


class CampaignCellGoalInline(admin.TabularInline):
    model = CampaignCellGoal
    extra = 3


@admin.register(EvangelismCampaign)
class EvangelismCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'semester_label', 'campus_goal', 'is_active']
    inlines = [CampaignCellGoalInline]


@admin.register(Recruit)
class RecruitAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'cell', 'category', 'phone', 'added_by', 'date_added']
    list_filter = ['campaign', 'cell', 'category']
    search_fields = ['full_name', 'phone', 'referral_name']
