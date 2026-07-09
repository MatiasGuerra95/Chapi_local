"""T-211/T-212: MockEmbedder + coseno + ranking semántico (lógica del endpoint)."""
import math

from app.services.embeddings_service import MockEmbedder, cosine


def test_embedding_determinista_y_dimension():
    emb = MockEmbedder(dim=32)
    a = emb.embed("Estafa residencial")
    b = emb.embed("Estafa residencial")
    assert a == b
    assert len(a) == 32


def test_embedding_normalizado():
    v = MockEmbedder(dim=32).embed("hurto simple reiterado")
    assert math.isclose(math.sqrt(sum(x * x for x in v)), 1.0, rel_tol=1e-9)


def test_texto_vacio_da_vector_cero():
    v = MockEmbedder(dim=16).embed("")
    assert v == [0.0] * 16
    assert cosine(v, MockEmbedder(dim=16).embed("algo")) == 0.0


def test_coseno_identico_vs_disjunto():
    emb = MockEmbedder(dim=128)
    base = emb.embed("robo con intimidacion")
    igual = emb.embed("robo con intimidacion")
    distinto = emb.embed("pension alimentos familia")
    assert math.isclose(cosine(base, igual), 1.0, rel_tol=1e-9)
    assert cosine(base, distinto) < cosine(base, igual)


def test_ranking_semantico_prioriza_solapamiento():
    # Reproduce la lógica del endpoint /similar sin BD.
    emb = MockEmbedder(dim=256)
    q = "estafa"
    casos = {
        "c1": "Estafa y otros delitos economicos",
        "c2": "Divorcio de común acuerdo",
        "c3": "Estafa residencial reiterada",
    }
    qv = emb.embed(q)
    ranked = sorted(casos, key=lambda k: cosine(qv, emb.embed(casos[k])), reverse=True)
    assert ranked[0] in ("c1", "c3")
    assert ranked[-1] == "c2"
