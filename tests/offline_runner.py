"""Run a server file with requests.get/post replaced by offline fakes (no network)."""
import json, runpy, sys
import requests

class _Resp:
    def __init__(self, url, data=None, text=None, status=200):
        self.url, self._data, self.status_code = url, data, status
        self.text = text if text is not None else json.dumps(data)
        self.ok = status < 400
    def json(self): return self._data if self._data is not None else json.loads(self.text)
    def raise_for_status(self):
        if not self.ok: raise requests.HTTPError(f"{self.status_code}", response=self)

RSS = ('<rss><channel><item><title>T1</title><link>https://e.org/1</link>'
       '<pubDate>D</pubDate><description>S</description></item></channel></rss>')

def fake_get(url, params=None, **kw):
    if url.endswith(".rss"): return _Resp(url, text=RSS)
    if url.endswith(".json"): return _Resp(url, {"data": {"items": [{"name": "first"}]}})
    return _Resp(url, text="<html><body>offline</body></html>")

def fake_post(url, json=None, **kw):
    return _Resp(url, {"ok": True})

requests.get, requests.post = fake_get, fake_post
sys.argv = [sys.argv[1]]
runpy.run_path(sys.argv[0], run_name="__main__")
