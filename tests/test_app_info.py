from ict_cockpit.app_info import APP_NAME, APP_VERSION, window_title


def test_window_title_contains_app_name_and_version() -> None:
    title = window_title()

    assert APP_NAME in title
    assert APP_VERSION in title
