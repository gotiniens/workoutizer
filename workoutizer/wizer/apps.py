import time
import os
import logging
from multiprocessing import Process

from django.apps import AppConfig
from django.db.utils import OperationalError
from wizer.format.gpx import GPXParser
from wizer.format.fit import FITParser
from wizer.tools.utils import sanitize, calc_md5

log = logging.getLogger('wizer.apps')

sport_naming_map = {
    'Jogging': ['jogging', 'running'],
    'Cycling': ['cycle', 'cycling'],
    'Mountainbiking': ['mountainbiking', 'mountainbike', 'mountain biking', 'mountain bike', 'mountain-biking',
                       'mountain-bike', 'mtbing', 'mtb', 'cycling_mountain'],
    'Hiking': ['hiking', 'hike', 'wandern', 'walking', 'mountaineering'],
    'Triathlon': ['triathlon', 'tria'],
    'Swimming': ['swimming', 'swim', 'pool'],
    'Yoga': ['yoga', 'yogi'],
}


formats = [".gpx", ".fit"]


class WizerFileDaemon(AppConfig):
    name = 'wizer'
    verbose_name = 'Workoutizer'

    def ready(self):
        from .models import Settings, Traces, Activity, Sport
        try:
            # TODO get settings of current logged in user, maybe start GPXFileImporter only after login?
            settings = Settings.objects.all().order_by('-id').first()
            if settings:
                p = Process(target=FileImporter, args=(settings, Traces, Activity, Sport))
                p.start()
        except OperationalError:
            log.warning(f"could not find table: wizer_settings - won't run FileImporter. Run django migrations first.")
            # TODO create notification here


class FileImporter:
    def __init__(self, settings_model, trace_files_model, activities_model, sport_model):
        self.settings = settings_model
        self.path = self.settings.path_to_trace_dir
        self.trace_files_model = trace_files_model
        self.activities_model = activities_model
        self.sport_model = sport_model
        self.interval = self.settings.gpx_checker_interval
        self.start_listening()

    def start_listening(self):
        while True:
            # find activity files in directory
            trace_files = [os.path.join(root, name)
                           for root, dirs, files in os.walk(self.path)
                           for name in files if name.endswith(tuple(formats))]
            log.debug(f"found {len(trace_files)} files in trace dir: {self.path}")
            self.add_objects_to_models(trace_files)
            time.sleep(self.interval)

    def add_objects_to_models(self, trace_files):
        md5sums_from_db = list(self.trace_files_model.objects.all())
        md5sums_from_db = [m.md5sum for m in md5sums_from_db]
        for file in trace_files:
            md5sum = calc_md5(file)
            if md5sum not in md5sums_from_db:   # current file is not stored in model yet
                log.debug(f"importing file {file}...")
                if file.endswith(".gpx"):
                    log.debug(f"parsing GPX file")
                    parser = GPXParser(path_to_file=file)
                elif file.endswith(".fit"):
                    log.debug(f"parsing FIT file")
                    parser = FITParser(path_to_file=file)
                else:
                    log.warning(f"file type: {file} unknown")
                    parser = None
                sport = parser.sport
                mapped_sport = map_sport_name(sport, sport_naming_map)
                log.info(f"saving trace file {file} to traces model")
                t = self.trace_files_model(
                    path_to_file=file,
                    md5sum=md5sum,
                    coordinates=parser.coordinates,
                    altitude=parser.altitude,
                )
                t.save()
                trace_file_instance = self.trace_files_model.objects.get(pk=t.pk)
                sport_instance = self.sport_model.objects.filter(slug=sanitize(mapped_sport)).first()
                a = self.activities_model(
                    title=parser.title,
                    sport=sport_instance,
                    date=parser.date,
                    duration=parser.duration,
                    distance=parser.distance,
                    trace_file=trace_file_instance,
                )
                a.save()
                log.info(f"created new {sport_instance} activity: {parser.title}")
            else:  # means file is stored in db already
                trace_file_paths_model = self.trace_files_model.objects.get(md5sum=md5sum)
                if trace_file_paths_model.path_to_file != file:
                    log.debug(f"path of file: {trace_file_paths_model.path_to_file} has changed, updating to {file}")
                    trace_file_paths_model.path_to_file = file
                    trace_file_paths_model.save()


def map_sport_name(sport_name, map_dict):
    sport = None
    for k, v in map_dict.items():
        if sanitize(sport_name) in v:
            log.debug(f"mapped activity sport: {sport_name} to {k}")
            sport = k
    if not sport:
        log.warning(f"could not map {sport_name} to given sport names, use None instead")
    return sport
