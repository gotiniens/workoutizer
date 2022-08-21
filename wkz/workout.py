import logging

from fit_tool.profile.profile_type import Intensity, WorkoutStepDuration

from wkz.models import Workout, WorkoutStep

log = logging.getLogger(__name__)


def CreateWorkout(form):
    workout = Workout()

    workout.name = form.cleaned_data["name"]
    workout.sport = form.cleaned_data["sport"]

    workout.save()
    return workout


def CreateInterval(form, workout):
    repeats = form.cleaned_data["repeats"]
    repeat = 0
    run_duration_sec = form.cleaned_data["run_duration_sec"]
    rest_duration_sec = form.cleaned_data["rest_duration_sec"]
    warm_up = form.cleaned_data["warm_up"]
    cool_down = form.cleaned_data["cool_down"]

    if warm_up:
        log.debug("warm up until lap key")
        WarmUp = WorkoutStep()

        WarmUp.workout = workout
        WarmUp.name = "Warm Up until lap key"
        WarmUp.duration_type = WorkoutStepDuration.OPEN.value
        WarmUp.intensity = Intensity.WARMUP.value
        WarmUp.save()

    while repeat < repeats:
        log.debug(f"repeat: {repeat}")
        log.debug(f"run for {run_duration_sec} secs")
        log.debug(f"rest for {rest_duration_sec} secs")
        repeat += 1

    if cool_down:
        log.debug("Cool down until lap key")
        CoolDown = WorkoutStep()

        CoolDown.workout = workout
        CoolDown.name = "Cool down until lap key"
        CoolDown.duration_type = WorkoutStepDuration.OPEN.value
        CoolDown.intensity = Intensity.COOLDOWN.value
        CoolDown.save()
