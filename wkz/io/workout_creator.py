import datetime
import logging
import os
import secrets

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.workout_message import WorkoutMessage
from fit_tool.profile.messages.workout_step_message import WorkoutStepMessage
from fit_tool.profile.profile_type import FileType, Intensity, Manufacturer, Sport, WorkoutStepDuration

from wkz.models import Workout, WorkoutStep, get_settings
from wkz.tools.utils import calc_md5

log = logging.getLogger(__name__)


def _get_creation_queue():
    # TODO: Recreate files deleted from filesystem
    return Workout.objects.filter(md5sum__isnull=True, file_name__isnull=True)


def _get_filename(workout):
    return f"{workout.id}-{secrets.token_hex(5)}.fit"


def workout_creator():
    settings = get_settings()
    path_to_workouts_dir = settings.path_to_workouts_dir
    log.debug(f"Creating workout files in {path_to_workouts_dir}")

    queue = _get_creation_queue()

    header_message = FileIdMessage()
    header_message.type = FileType.WORKOUT
    header_message.manufacturer = Manufacturer.DEVELOPMENT.value
    header_message.product = 0

    for workout in queue:
        header_message.time_created = round(datetime.datetime.now().timestamp() * 1000)  # TODO: tijd van workout.created
        header_message.serial_number = workout.id
        steps = WorkoutStep.objects.filter(workout=workout)
        message_index = 0
        print(workout.name)

        workout_message = WorkoutMessage()
        workout_message.workout_name = workout.name
        workout_message.sport = Sport(workout.sport_id)
        workout_message.num_valid_steps = len(steps)

        step_messages = []
        for step in steps:
            print(step.name)
            workoutStep_message = WorkoutStepMessage()
            workoutStep_message.workout_step_name = step.name
            workoutStep_message.message_index = message_index
            message_index += 1
            if step.intensity is not None:
                workoutStep_message.intensity = Intensity(step.intensity)
            if step.duration_type is not None:
                workoutStep_message.duration_type = WorkoutStepDuration(step.duration_type)
            if step.duration_step is not None:
                print(f"duration_step {step.duration_step}")
                workoutStep_message.duration_step = step.duration_step
            if step.target_repeat_steps is not None:
                workoutStep_message.target_repeat_steps = step.target_repeat_steps
            if step.duration_value is not None:
                if step.duration_type == WorkoutStepDuration.TIME.value:
                    workoutStep_message.duration_time = step.duration_value * 1000
                else:
                    workoutStep_message.duration_value = step.duration_value
            step_messages.append(workoutStep_message)

        builder = FitFileBuilder(auto_define=True, min_string_size=50)
        builder.add(header_message)
        builder.add(workout_message)
        builder.add_all(step_messages)

        workout_file = builder.build()
        filename = os.path.join(path_to_workouts_dir, _get_filename(workout))
        workout.file_name = filename
        workout_file.to_file(filename)
        workout.md5sum = calc_md5(filename)
        workout.save()
