from django.contrib import admin
from .models import SkillsCategory , Skills, UserSkills

@admin.register(SkillsCategory)
class SkillsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name' , 'description' , 'icon_class','image']
    

@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ['name', 'category' , 'image' , 'description' , 'level']


@admin.register(UserSkills)
class UserSkillsAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'added_at']
    list_filter = ['skill__category', 'added_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'skill__name']
    date_hierarchy = 'added_at'
