from django.shortcuts import render
from django.views.generic import View

from wkz import models
from wkz.tools.style import Style


class WorkoutsView(View):
    template_name = "workout/workouts.html"

    def get(self, request):
        workouts = models.Workout.objects.all().order_by("name")
        for workout in workouts:
            setattr(workout, "number_of_steps", len(models.WorkoutStep.objects.filter(workout=workout.id)))

        return render(
            request,
            self.template_name,
            {
                "page_name": "Workouts",
                "style": Style,
                "workouts": workouts,
            },
        )
