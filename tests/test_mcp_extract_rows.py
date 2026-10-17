"""web_extract answers every requested URL: rows past the cap, requested_url."""

import os
import socket
from unittest import mock

import pytest

from web_search_plus_mcp import extract, providers, server
from web_search_plus_mcp.compat_v3 import legacy_request_to_v3
from web_search_plus_mcp.contract_v3 import Capability


@pytest.fixture(autouse=True)
def _public_example_hosts(monkeypatch):
    resolve = socket.getaddrinfo

    def fake(host, port, *args, **kwargs):
        if str(host).endswith("example.com"):
            host = "93.184.216.34"
        return resolve(host, port, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", fake)


def _extract_through_projection(urls, answer, **options):
    """Real v3 engine with a fixed Firecrawl answer, then the MCP projection."""
    with mock.patch.dict(os.environ, {"FIRECRAWL_API_KEY": "fc-test"}, clear=True), mock.patch.object(
        providers, "extract_firecrawl", side_effect=answer
    ):
        request = legacy_request_to_v3(
            Capability.EXTRACT, {"urls": urls, "provider": "firecrawl", **options}
        )
        response = extract.run_extract_request_v3(request, config=extract.load_config()).to_dict()
    return server._project_v3_payload(response, capability="extract", urls=urls)


def _page(url, final_url=None):
    return {
        "url": final_url or url,
        "requested_url": url,
        "title": "T",
        "content": f"text of {url}",
        "raw_content": f"text of {url}",
        "provider": "firecrawl",
    }


def _answer(batch, *args, **kwargs):
    return {"provider": "firecrawl", "results": [_page(url) for url in batch]}


def test_urls_past_the_cap_get_a_not_tried_row_in_the_mcp_output():
    urls = [f"https://example.com/page-{index}" for index in range(12)]

    projected = _extract_through_projection(urls, _answer)

    assert [item["url"] for item in projected["results"]] == urls
    assert all(item["content"] for item in projected["results"][:10])
    for item in projected["results"][10:]:
        assert item["error"] == "not tried: limit of 10 URLs per call reached"
        assert item["content"] == ""
    assert projected["limits_applied"]["extract"]["omitted_urls"] == urls[10:]


def test_requests_within_the_cap_get_no_extra_rows():
    urls = [f"https://example.com/page-{index}" for index in range(3)]

    projected = _extract_through_projection(urls, _answer)

    assert [item["url"] for item in projected["results"]] == urls
    assert not any(item.get("error") for item in projected["results"])
