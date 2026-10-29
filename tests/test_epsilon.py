import math

import pytest

import epsilon as ep


@pytest.mark.parametrize("bad", [0, 0.0, -1e-9, float("nan"), float("inf"), True, False, "1e-6", [1e-6]])
def test_eps_must_be_none_or_a_positive_finite_number(bad):
    with pytest.raises(ep.EpsilonError, match="greater than 0"):
        ep.check_eps(bad)


def test_eps_is_never_defaulted_and_none_means_off():
    assert ep.check_eps(None) is None
    assert ep.check_eps(1e-6) == 1e-6 and ep.check_eps(2) == 2.0 and isinstance(ep.check_eps(2), float)
    import inspect
    assert inspect.signature(ep.lift).parameters["eps"].default is inspect.Parameter.empty  # the caller always says it


def test_a_value_exactly_on_the_lower_bound_is_lifted_inside_by_eps():
    assert ep.lift(0.0, 1e-6, lo=0.0) == (1e-6, True)
    assert ep.lift(0, 0.25, lo=0) == (0.25, True)
    assert ep.lift(5, 0.5, lo=5) == (5.5, True)


def test_a_value_exactly_on_the_upper_bound_is_lifted_inside_by_eps():
    assert ep.lift(1.0, 1e-6, hi=1.0) == (1.0 - 1e-6, True)
    assert ep.lift(1.0, 0.25, lo=0.0, hi=1.0) == (0.75, True)


def test_without_eps_the_boundary_is_detected_and_the_value_is_untouched():
    assert ep.lift(0.0, None, lo=0.0) == (0.0, True)
    assert ep.lift(1.0, None, hi=1.0) == (1.0, True)


@pytest.mark.parametrize("x", [1e-300, 0.5, 1 - 1e-16, -0.0000001, 2.0])
def test_anything_not_exactly_on_a_bound_passes_through_and_is_not_a_hit(x):
    # exact equality only: a near-zero is the business of the named tolerances, not of ε
    assert ep.lift(x, 1e-6, lo=0.0, hi=1.0) == (x, False)
    assert ep.lift(x, None, lo=0.0, hi=1.0) == (x, False)


def test_negative_zero_is_zero():
    assert ep.lift(-0.0, 1e-3, lo=0.0) == (1e-3, True)


def test_a_bound_is_required_and_eps_must_fit_inside_two_bounds():
    with pytest.raises(ep.EpsilonError, match="needs a bound"):
        ep.lift(0.0, 1e-6)
    with pytest.raises(ep.EpsilonError, match="does not fit"):
        ep.lift(0.0, 0.5, lo=0.0, hi=1.0)
    with pytest.raises(ep.EpsilonError, match="greater than 0"):
        ep.lift(0.0, 0, lo=0.0)
    assert ep.lift(0.0, 0.49, lo=0.0, hi=1.0) == (0.49, True)


def test_the_lifted_value_is_strictly_inside_and_moves_with_eps():
    for eps in (1e-3, 1e-6, 1e-9):
        v, hit = ep.lift(0.0, eps, lo=0.0, hi=1.0)
        assert hit and 0 < v < 1 and math.isclose(v, eps)
