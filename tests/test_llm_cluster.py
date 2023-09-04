from click.testing import CliRunner
import json
from llm.cli import cli
from llm_sentence_transformers import SentenceTransformerModel
import llm
import pytest
import sqlite_utils


@pytest.fixture
def db_path(tmpdir):
    db_path = tmpdir / "data.db"
    db = sqlite_utils.Database(str(db_path))
    embed_model = SentenceTransformerModel(
        "sentence-transformers/all-MiniLM-L6-v2", "all-MiniLM-L6-v2"
    )
    collection = llm.Collection("entries", db, model=embed_model)
    collection.embed_multi(
        [
            (1, "hello world"),
            (2, "goodbye world"),
            (3, "third thing"),
            (4, "fourth thing"),
            (5, "fifth thing"),
            (6, "sixth thing"),
            (7, "seventh thing"),
            (8, "eighth thing"),
            (9, "ninth thing"),
            (10, "tenth thing"),
        ]
    )
    return db_path


@pytest.mark.parametrize("n", (2, 5))
def test_cluster(db_path, n):
    db = sqlite_utils.Database(str(db_path))
    assert db["embeddings"].count == 10
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "cluster",
            "entries",
            "--database",
            str(db_path),
            str(n),
        ],
    )
    assert result.exit_code == 0, result.output
    clusters = json.loads(result.output)
    assert len(clusters) == n
    for cluster in clusters:
        assert isinstance(cluster["id"], str)
        assert isinstance(cluster["items"], list)
