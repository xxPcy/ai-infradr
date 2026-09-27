from ai_infradr.app import InfraDr
from ai_infradr.probes.base import Probe, ProbeResult


class GoodProbe(Probe):
    name = "system"

    def collect(self):
        return ProbeResult(self.name, {"os": "Linux"})


class BadProbe(Probe):
    name = "cuda"

    def collect(self):
        raise RuntimeError("boom")


def test_infradr_degrades_gracefully_when_probe_fails():
    snapshot = InfraDr(probes=[GoodProbe(), BadProbe()]).snapshot()
    assert snapshot.system["os"] == "Linux"
    assert "cuda" in snapshot.probe_errors
    assert "RuntimeError" in snapshot.probe_errors["cuda"]
