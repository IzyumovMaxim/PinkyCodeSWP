import pytest

SAMPLE_CODE = """
// This is a top‑level comment
public class Example {
    /* Block comment
       spanning two lines */
    public void foo(int x) {
        // foo does something
        System.out.println(x);
    }

    public int bar() {
        return 42; // answer
    }
}

// trailing comment
"""

NO_COMMENT_CODE = """
public class Empty {
    public void nothing() {
        System.out.println("No comments here");
    }
}
"""

EMPTY_CODE = ""


@pytest.mark.integration
def test_get_density(metrics_funcs):
    density = metrics_funcs["density"](SAMPLE_CODE)
    assert isinstance(density, float)
    assert density > 50.0

@pytest.mark.integration
def test_get_comments_full_coverage(metrics_funcs):
    commented_pct = metrics_funcs["comments"](SAMPLE_CODE)
    assert commented_pct == pytest.approx(100.0, rel=1e-3)

@pytest.mark.integration
def test_get_readability_high_score(metrics_funcs):
    score = metrics_funcs["readability"](SAMPLE_CODE)
    assert isinstance(score, float)
    assert 0.0 < score <= 100.0
    assert score > 70.0

@pytest.mark.integration
def test_no_comments_edge_cases(metrics_funcs):
    assert metrics_funcs["density"](NO_COMMENT_CODE) == pytest.approx(0.0)
    assert metrics_funcs["comments"](NO_COMMENT_CODE) == pytest.approx(0.0)
    assert metrics_funcs["readability"](NO_COMMENT_CODE) == pytest.approx(0.0)

@pytest.mark.integration
def test_empty_input(metrics_funcs):
    assert metrics_funcs["density"](EMPTY_CODE) == pytest.approx(0.0)
    assert metrics_funcs["comments"](EMPTY_CODE) == pytest.approx(0.0)
    assert metrics_funcs["readability"](EMPTY_CODE) == pytest.approx(0.0)
