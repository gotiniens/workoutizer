import os
import subprocess

from rest_framework.test import APIClient
import pytest

from wizer.file_helper import fit_collector
from wizer.file_helper.initial_data_handler import copy_demo_fit_files_to_track_dir
from wizer import models


@pytest.fixture
def client():
    yield APIClient()


def test_missing_endpoint(client):
    res = client.post("/this-endpoint-is-not-implemented/")

    assert res.status_code == 404


def test_stop(client):
    with pytest.raises(KeyboardInterrupt):
        client.post("/stop/")


def test_mount_device__not_importing(db, monkeypatch, client):
    # mock output of subprocess to prevent function from failing
    def dummy_output(dummy):
        return "dummy-string"

    monkeypatch.setattr(subprocess, "check_output", dummy_output)
    res = client.post("/mount-device/")

    # mounting a device is barely possible in testing, thus at least assert that the endpoint returns 500
    assert res.status_code == 500


def test_mount_device__importing(db, monkeypatch, demo_data_dir, tmpdir, client):
    # prepare settings
    target_dir = tmpdir.mkdir("tracks")
    settings = models.Settings(
        path_to_garmin_device=tmpdir,  # source
        path_to_trace_dir=target_dir,  # target
    )
    settings.save()

    def check_output(dummy):
        return "dummy\nstring\nsome\ncontent\ncontaining\nGarmin"

    monkeypatch.setattr(subprocess, "check_output", check_output)

    # mock output of subprocess to prevent function from failing
    def try_to_mount_device():
        return "dummy-string"

    monkeypatch.setattr(fit_collector, "try_to_mount_device", try_to_mount_device)

    # mock output of actual mounting command
    def mount(bus, dev):
        return "Mounted"

    monkeypatch.setattr(fit_collector, "_mount_device_using_gio", mount)

    # create directory to import the fit files from
    fake_device_dir = os.path.join(tmpdir, "mtp:host/Primary/GARMIN/Activity/")
    os.makedirs(fake_device_dir)

    # copy demo data to fake device dir
    copy_demo_fit_files_to_track_dir(source_dir=demo_data_dir, targe_dir=fake_device_dir)

    res = client.post("/mount-device/")

    assert res.status_code == 200
    assert len(models.Activity.objects.all()) == 10
