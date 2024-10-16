from django.contrib import admin

from .models import ExerciseCategory, Exercise, WorkoutPlan, ExercisePlan


class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name", "id")


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    ordering = ("name", "category", "id")


class ExercisePlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sets",
        "reps",
        "weight",
        "weight_measure_unit",
        "created_at",
    )
    ordering = ("name", "created_at")


class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "status",
        "is_completed",
        "started_at",
        "finished_at",
        "created_at",
    )
    ordering = ("name", "status", "id")


admin.site.register(ExerciseCategory, ExerciseCategoryAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(ExercisePlan, ExercisePlanAdmin)
admin.site.register(WorkoutPlan, WorkoutPlanAdmin)
