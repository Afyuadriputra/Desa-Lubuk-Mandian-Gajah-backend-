import pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_call(item):
    doc = item.function.__doc__
    class_name = item.cls.__name__ if item.cls else ""

    if doc:
        print(f"\n [{class_name}] {doc.strip()}")
    yield