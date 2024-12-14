import pytest
from exponential_counter import ExponentialCounter


def test_initialization():
    counter = ExponentialCounter(decay=2, initial_value=10)
    assert counter.get_value() == 10

    with pytest.raises(ValueError):
        ExponentialCounter(decay=0, initial_value=10)  # Decay must be greater than 0

    with pytest.raises(ValueError):
        ExponentialCounter(decay=-1, initial_value=10)  # Negative decay is invalid


def test_update_behavior():
    counter = ExponentialCounter(decay=2, initial_value=10)

    counter.update(20)
    expected_value = (0.5 * 10 + 20) / (0.5 + 1)
    assert counter.get_value() == pytest.approx(expected_value, rel=1e-6)

    expected_value = (0.5 * counter.get_value() + 30) / (0.5 + 1)
    counter.update(30)
    assert counter.get_value() == pytest.approx(expected_value, rel=1e-6)


def test_high_decay():
    counter = ExponentialCounter(decay=100, initial_value=10)

    counter.update(20)
    expected_value = (1 / 100 * 10 + 20) / (1 / 100 + 1)
    assert counter.get_value() == pytest.approx(expected_value, rel=1e-6)


def test_low_decay():
    counter = ExponentialCounter(decay=0.5, initial_value=10)

    counter.update(20)
    expected_value = (2 * 10 + 20) / (2 + 1)
    assert counter.get_value() == pytest.approx(expected_value, rel=1e-6)


def test_multiple_updates():
    counter = ExponentialCounter(decay=2, initial_value=10)

    counter.update(20)
    first_update_value = (0.5 * 10 + 20) / (0.5 + 1)
    assert counter.get_value() == pytest.approx(first_update_value, rel=1e-6)

    counter.update(30)
    second_update_value = (0.5 * first_update_value + 30) / (0.5 + 1)
    assert counter.get_value() == pytest.approx(second_update_value, rel=1e-6)

    counter.update(40)
    third_update_value = (0.5 * second_update_value + 40) / (0.5 + 1)
    assert counter.get_value() == pytest.approx(third_update_value, rel=1e-6)
