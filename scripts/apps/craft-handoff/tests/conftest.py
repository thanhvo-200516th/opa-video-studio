def pytest_configure(config):
    config.addinivalue_line("markers", "craft: builds a real project in FilmCraft / EffectCraft (slow, needs Xephyr)")
