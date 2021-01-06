import os
import subprocess

import pytest

from wizer import models

from workoutizer import __main__ as cli
from workoutizer import __version__
from workoutizer import settings as django_settings


def test_cli__version():
    output = cli._version()
    assert output == __version__


def test_cli_version():
    output = subprocess.check_output(["wkz", "version"]).decode("utf-8")
    assert output == f"{__version__}\n"


def test_cli__init(db):
    cli._init(answer="n")
    assert os.path.isdir(django_settings.WORKOUTIZER_DIR)
    assert len(models.Sport.objects.all()) == 5
    assert len(models.Settings.objects.all()) == 1
    assert len(models.Activity.objects.all()) > 1


def test_cli__check(db):
    # if wkz is not initialized expect to raise error
    with pytest.raises(cli.NotInitializedError):
        cli._check()

    # now initialized wkz first and then run check
    cli._init(answer="n")
    cli._check()