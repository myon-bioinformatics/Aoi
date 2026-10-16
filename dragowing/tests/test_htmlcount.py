from dragowing.htmlcount import count_elements


def test_count_elements_limits_tags():
    html = "<html><body><div><p>x</p><p>y</p><img></body></html>"
    assert count_elements(html, ("p", "img")) == {"p": 2, "img": 1}
    assert count_elements(html) == {
        "html": 1,
        "body": 1,
        "div": 1,
        "p": 2,
        "img": 1,
    }
