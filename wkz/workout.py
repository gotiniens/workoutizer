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
    active_duration_sec = form.cleaned_data["active_duration_sec"]
    rest_duration_sec = form.cleaned_data["rest_duration_sec"]
    warm_up = form.cleaned_data["warm_up"]
    cool_down = form.cleaned_data["cool_down"]
    workoutstep_counter = -1

    if warm_up:
        log.debug("warm up until lap key")
        WarmUp = WorkoutStep()

        WarmUp.workout = workout
        WarmUp.name = "Warm Up until lap key"
        WarmUp.duration_type = WorkoutStepDuration.OPEN.value
        WarmUp.intensity = Intensity.WARMUP.value
        WarmUp.save()
        workoutstep_counter += 1

    log.debug(f"repeats: {repeats}")
    log.debug(f"active for {active_duration_sec} secs")
    log.debug(f"rest for {rest_duration_sec} secs")

    active = WorkoutStep()
    active.workout = workout
    active.name = f"active for {active_duration_sec} secs"
    active.duration_type = WorkoutStepDuration.TIME.value
    active.duration_value = active_duration_sec
    active.intensity = Intensity.INTERVAL.value
    active.save()
    workoutstep_counter += 1
    repeat_from_workoutstep = workoutstep_counter

    rest = WorkoutStep()
    rest.workout = workout
    rest.name = f"rest for {rest_duration_sec} secs"
    rest.duration_type = WorkoutStepDuration.TIME.value
    rest.duration_value = rest_duration_sec
    rest.intensity = Intensity.REST.value
    rest.save()
    workoutstep_counter += 1

    repeat = WorkoutStep()
    repeat.workout = workout
    repeat.name = f"Repeat the last 2 steps {repeats} time"
    repeat.duration_type = WorkoutStepDuration.REPEAT_UNTIL_STEPS_CMPLT.value
    repeat.target_repeat_steps = repeats
    repeat.duration_step = repeat_from_workoutstep
    repeat.save()

    if cool_down:
        log.debug("Cool down until lap key")
        CoolDown = WorkoutStep()

        CoolDown.workout = workout
        CoolDown.name = "Cool down until lap key"
        CoolDown.duration_type = WorkoutStepDuration.OPEN.value
        CoolDown.intensity = Intensity.COOLDOWN.value
        CoolDown.save()
