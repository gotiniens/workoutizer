from wizer.file_helper.fit_collector import _find_complete_garmin_device_path, _find_activity_sub_dir_in_path


def test__find_complete_garmin_device_path(tmpdir):

    # no device path is available, expect to get None
    assert _find_complete_garmin_device_path(tmpdir) is None

    # dummy device path is available, expect to get it
    device_path = tmpdir.mkdir("mtp:host=092e_4b58_0000c4fa0519")
    assert _find_complete_garmin_device_path(tmpdir) == device_path


def test__find_activity_sub_dir_in_path(tmp_path):

    # desired sub dir is in first level
    d = tmp_path / "first"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="first", path=tmp_path, depth=1) == str(d)

    # desired sub dir is in first level and algorithm should not be case sensitive
    d = tmp_path / "FIRST"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="first", path=tmp_path, depth=1) == str(d).lower()

    # desired sub dir is in second level
    d = tmp_path / "first" / "second"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="second", path=tmp_path, depth=2) == str(d)

    # desired sub dir is in third level
    d = tmp_path / "first" / "second" / "third"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="third", path=tmp_path, depth=3) == str(d)

    # if dir in fourth level is searched for but depth is specified as 3 only, function should return False
    d = tmp_path / "first" / "second" / "third" / "fourth"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="fourth", path=tmp_path, depth=3) is False

    # a more realistic example
    d = tmp_path / "mtp:something" / "GARMIN" / "Primary" / "Activity"
    d.mkdir(parents=True)
    assert _find_activity_sub_dir_in_path(name_of_dir="Activity", path=tmp_path, depth=4) == str(d)
