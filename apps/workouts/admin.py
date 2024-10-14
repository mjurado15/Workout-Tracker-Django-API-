from django.contrib import admin

from .models import ExerciseCategory, Exercise


class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name", "id")


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    ordering = ("name", "category", "id")


admin.site.register(ExerciseCategory, ExerciseCategoryAdmin)
admin.site.register(Exercise, ExerciseAdmin)
