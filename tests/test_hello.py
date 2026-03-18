from src import hello


def test_hello_default() -> None:
    assert hello() == "Hello, world!"


def test_hello_with_name() -> None:
    assert hello("Mario") == "Hello, Mario!"
