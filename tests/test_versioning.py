from ai_infradr.diagnosis.versioning import version_lt, version_tuple


def test_version_tuple_handles_common_cuda_versions():
    assert version_tuple("12.6") == (12, 6, 0)
    assert version_tuple("11.8.0") == (11, 8, 0)


def test_version_lt():
    assert version_lt("12.4", "12.6") is True
    assert version_lt("12.8", "12.6") is False
