import os
from pathlib import Path
from packaging import version
import subprocess

import pytest

from workoutizer import settings as django_settings
from workoutizer import __version__ as current_version


workoutizer = "workoutizer"


@pytest.fixture
def venv_with_latest_wkz_from_pypi(venv):
    os.environ["WKZ_ENV"] = "devel"
    venv.install(workoutizer, upgrade=True)
    yield venv


@pytest.fixture
def venv_with_current_wkz(venv):
    # build wheel
    subprocess.check_call([venv.python, "setup.py", "bdist_wheel"])
    # install wheel
    path_to_wheel = Path(django_settings.WORKOUTIZER_DIR) / "dist" / f"workoutizer-{current_version}-py3-none-any.whl"
    venv.install(str(path_to_wheel))
    # change dir to new home (in order to pick up correct django settings)
    new_wkz_home = list((Path(venv.path) / "lib").iterdir())[0] / "site-packages"
    os.chdir(new_wkz_home)
    # add wkz path as attribute to venv
    wkz = Path(venv.bin) / "wkz"
    setattr(venv, "wkz", wkz)
    yield venv


@pytest.fixture
def venv_with_current_wkz__initialized(venv_with_current_wkz):
    subprocess.check_call([venv_with_current_wkz.wkz, "init"])
    yield venv_with_current_wkz


@pytest.fixture
def venv_with_current_wkz__initialized_demo(venv_with_current_wkz):
    subprocess.check_call([venv_with_current_wkz.wkz, "init", "--demo"])
    yield venv_with_current_wkz


def test_install_current_local_version(venv_with_current_wkz__initialized_demo):
    installed_version = str(venv_with_current_wkz__initialized_demo.get_version(workoutizer))

    # check that the installed version equals the current version
    assert version.parse(current_version) == version.parse(installed_version)


def test_install_latest_version_from_pypi(venv_with_latest_wkz_from_pypi):
    latest_version_on_pypi = str(venv_with_latest_wkz_from_pypi.get_version(workoutizer))

    # check that the latest version from pypi is always smaller than or equal to the current version
    assert version.parse(current_version) >= version.parse(latest_version_on_pypi)


# def test_migration_from_latest_pypi_version_to_current(latest_pypi_wkz_venv):
#     wkz = Path(latest_pypi_wkz_venv.bin) / "wkz"
#     subprocess.check_call([wkz, "init", "--demo"])
#     subprocess.check_call([wkz, "check"])
