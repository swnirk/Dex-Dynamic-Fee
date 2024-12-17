import pytest

from exponential_moving_average import ExponentialMovingAverage


def test_initialization():
    ema = ExponentialMovingAverage(alpha=0.8, initial_value=10)
    assert ema.average() == 10, "Initial EMA should match the given initial value."


def test_single_update():
    ema = ExponentialMovingAverage(alpha=0.5, initial_value=10)
    ema.update(20)
    expected = 0.5 * 20 + 0.5 * 10
    assert (
        pytest.approx(ema.average(), 0.0001) == expected
    ), "EMA after one update is incorrect."


def test_multiple_updates():
    ema = ExponentialMovingAverage(alpha=0.5, initial_value=10)
    ema.update(20)
    ema.update(30)
    expected = 0.5 * 30 + 0.5 * (0.5 * 20 + 0.5 * 10)
    assert (
        pytest.approx(ema.average(), 0.0001) == expected
    ), "EMA after multiple updates is incorrect."


def test_alpha_boundaries():
    with pytest.raises(ValueError):
        ExponentialMovingAverage(alpha=1.1, initial_value=10)
    with pytest.raises(ValueError):
        ExponentialMovingAverage(alpha=0.0, initial_value=10)


def test_explicit_formula():
    initial_value = 10
    alpha = 0.5

    ema = ExponentialMovingAverage(alpha=alpha, initial_value=initial_value)

    value_1 = 20
    ema.update(value_1)
    expected_1 = initial_value * (1 - alpha) + value_1 * alpha
    assert pytest.approx(ema.average(), 0.0001) == expected_1

    value_2 = 30
    ema.update(value_2)
    expected_2 = (
        initial_value * (1 - alpha) ** 2
        + value_1 * alpha * (1 - alpha)
        + value_2 * alpha
    )
    assert pytest.approx(ema.average(), 0.0001) == expected_2

    value_3 = 40
    ema.update(value_3)
    expected_3 = (
        initial_value * (1 - alpha) ** 3
        + value_1 * alpha * (1 - alpha) ** 2
        + value_2 * alpha * (1 - alpha)
        + value_3 * alpha
    )
    assert pytest.approx(ema.average(), 0.0001) == expected_3

    value_4 = 50
    ema.update(value_4)
    expected_4 = (
        initial_value * (1 - alpha) ** 4
        + value_1 * alpha * (1 - alpha) ** 3
        + value_2 * alpha * (1 - alpha) ** 2
        + value_3 * alpha * (1 - alpha)
        + value_4 * alpha
    )
    assert pytest.approx(ema.average(), 0.0001) == expected_4
