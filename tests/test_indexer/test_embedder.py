def test_embedder_mock(mock_embedder):
    res = mock_embedder.embed_batch(["hello world"])
    assert len(res) == 1
    assert len(res[0]) == 384
