from scripts.fetch_contributions import fetch_contribution_html


class FakeResponse:
    text = "<table></table>"

    def __init__(self):
        self.status_checked = False

    def raise_for_status(self):
        self.status_checked = True


def test_fetch_contribution_html_uses_public_endpoint_and_timeout():
    response = FakeResponse()
    request = {}

    def fake_get(url, *, headers, timeout):
        request.update(url=url, headers=headers, timeout=timeout)
        return response

    assert fetch_contribution_html("reckless-sherixx", get=fake_get) == response.text
    assert request == {
        "url": "https://github.com/users/reckless-sherixx/contributions",
        "headers": {"User-Agent": "reckless-sherixx-profile-readme/1.0"},
        "timeout": 30,
    }
    assert response.status_checked
