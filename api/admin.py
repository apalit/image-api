from django.contrib import admin
from api.models import Plan, UserPlan


# Register your models here.
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan']
