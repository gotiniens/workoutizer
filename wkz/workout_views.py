import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View

from wkz import models
from wkz.forms import AddWorkoutIntervalsForm, AddWorkoutMainForm
from wkz.tools.style import Style
from wkz.views import get_all_form_field_ids
from wkz.workout import CreateInterval, CreateWorkout

log = logging.getLogger(__name__)


class WorkoutsView(View):
    template_name = "workout/workouts.html"

    def get(self, request):
        sports = models.Sport.objects.all().order_by("name")
        workouts = models.Workout.objects.all().order_by("name")
        for workout in workouts:
            setattr(workout, "number_of_steps", len(models.WorkoutStep.objects.filter(workout=workout.id)))

        return render(
            request,
            self.template_name,
            {
                "sports": sports,
                "page_name": "Workouts",
                "style": Style,
                "workouts": workouts,
            },
        )


class AddWorkoutView(View):
    main_form_class = AddWorkoutMainForm
    interval_form_class = AddWorkoutIntervalsForm

    def get(self, request):
        sports = models.Sport.objects.all().order_by("name")
        main_form = self.main_form_class
        interval_form = self.interval_form_class
        return render(
            request,
            "workout/add_workout.html",
            {
                "sports": sports,
                "page_name": "Add Workout",
                "style": Style,
                "main_form": main_form,
                "interval_form": interval_form,
                "form_field_ids": get_all_form_field_ids(),
            },
        )

    def post(self, request):
        main_form = self.main_form_class(request.POST)
        interval_form = self.interval_form_class(request.POST)
        print(request)
        if main_form.is_valid():
            log.debug("Valid Form")
            workout = CreateWorkout(main_form)
            if interval_form.is_valid():
                log.debug("Valid Interval Workout")
                CreateInterval(interval_form, workout)
            messages.success(request, f"Successfully created workout '{main_form.cleaned_data['name']}'")
            return HttpResponseRedirect(reverse("workout"))
        else:
            log.warning(f"form invalid: {main_form.errors}")
