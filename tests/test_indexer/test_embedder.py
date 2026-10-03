def test_embedder_mock(mock_embedder):
    res = mock_embedder.embed_batch(["hello world"])
    assert len(res) == 1
    assert len(res[0]) == 384


def test_embedder_reuses_model_instance(mocker):
    model = mocker.Mock()
    model_factory = mocker.patch("app.indexer.embedder.SentenceTransformer", return_value=model)

    from app.indexer.embedder import Embedder

    Embedder.clear_cache()
    first = Embedder("test-model", 384)
    second = Embedder("test-model", 384)

    assert first is second
    model_factory.assert_called_once_with("test-model")
    Embedder.clear_cache()
