from rest_framework.routers import SimpleRouter
from django.urls import path, include

from rest_framework_nested import routers as nested_routes

from workouts.views import (
    workout_views,
    exercise_category_views,
    exercise_plan_views,
    comment_views,
    scheduled_date_views,
    recurring_alert_views,
)

router = SimpleRouter()

router.register(
    "exercise_categories",
    exercise_category_views.ExerciseCategoryViews,
    basename="exercise-categories",
)
router.register("workouts", workout_views.WorkoutViews, basename="workouts")

# Workout nested routes
exercise_plan_routers = nested_routes.NestedSimpleRouter(
    router, "workouts", lookup="workout"
)
exercise_plan_routers.register(
    "exercise_plans",
    exercise_plan_views.ExercisePlanViews,
    basename="exercise-plans",
)

comment_routers = nested_routes.NestedSimpleRouter(router, "workouts", lookup="workout")
comment_routers.register("comments", comment_views.CommentViews, basename="comments")

scheduled_date_routers = nested_routes.NestedSimpleRouter(
    router, "workouts", lookup="workout"
)
scheduled_date_routers.register(
    "scheduled_dates",
    scheduled_date_views.ScheduledDateViews,
    basename="scheduled-dates",
)

recurring_alert_routers = nested_routes.NestedSimpleRouter(
    router, "workouts", lookup="workout"
)
recurring_alert_routers.register(
    "recurring_alerts",
    recurring_alert_views.RecurringAlertViews,
    basename="recurring-alerts",
)


urlpatterns = [
    path("", include(router.urls)),
    path("", include(exercise_plan_routers.urls)),
    path("", include(comment_routers.urls)),
    path("", include(scheduled_date_routers.urls)),
    path("", include(recurring_alert_routers.urls)),
]
