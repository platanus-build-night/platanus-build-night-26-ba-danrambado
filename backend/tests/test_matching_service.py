"""Unit tests for MatchingService: Phase 1 retrieval, Phase 2 wiring, get_matches."""
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.entities import (
    Connection,
    Opportunity,
    RankedMatch,
    User,
)
from app.core.enums import ConnectionSource, OpportunityType
from app.services.matching_service import (
    FIRST_DEGREE_BOOST,
    SECOND_DEGREE_BOOST,
    MatchingService,
)


def _make_user(
    user_id: str,
    name: str = "User",
    open_to: list[str] | None = None,
) -> User:
    return User(
        id=user_id,
        name=name,
        bio="",
        skills=[],
        interests=[],
        open_to=open_to or ["job", "project"],
        created_at=datetime.now(timezone.utc),
    )


def _make_opportunity(
    opp_id: str = "opp-1",
    posted_by: str = "poster-1",
    opp_type: OpportunityType = OpportunityType.JOB,
) -> Opportunity:
    return Opportunity(
        id=opp_id,
        title="Test role",
        description="Test description",
        type=opp_type,
        posted_by=posted_by,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def user_repo():
    return MagicMock()


@pytest.fixture
def match_repo():
    repo = MagicMock()
    repo.create_batch = MagicMock(side_effect=lambda matches: matches)
    repo.get_by_opportunity = MagicMock(return_value=[])
    return repo


@pytest.fixture
def connection_repo():
    repo = MagicMock()
    repo.get_connections = MagicMock(return_value=[])
    repo.get_second_degree = MagicMock(return_value={})
    return repo


@pytest.fixture
def embedding_port():
    return MagicMock()


@pytest.fixture
def ai_port():
    return MagicMock()


@pytest.fixture
def matching_service(user_repo, match_repo, connection_repo, embedding_port, ai_port):
    return MatchingService(
        user_repo=user_repo,
        match_repo=match_repo,
        connection_repo=connection_repo,
        embedding=embedding_port,
        ai=ai_port,
    )


def _run_async(coro):
    return asyncio.run(coro)


# ----- Phase 1: poster excluded -----


def test_phase1_poster_excluded_from_candidates(
    matching_service, user_repo, connection_repo, embedding_port, ai_port
):
    poster_id = "poster-1"
    candidate_id = "candidate-1"
    opp = _make_opportunity(posted_by=poster_id)
    poster = _make_user(poster_id, "Poster", open_to=["job"])
    candidate = _make_user(candidate_id, "Candidate", open_to=["job"])

    embedding_port.search_similar = MagicMock(
        return_value=[
            {"user_id": poster_id, "score": 0.9},
            {"user_id": candidate_id, "score": 0.8},
        ]
    )
    user_repo.get_by_id = MagicMock(
        side_effect=lambda uid: poster if uid == poster_id else (candidate if uid == candidate_id else None)
    )
    ai_port.rank_and_explain = AsyncMock(
        return_value=[
            RankedMatch(user_id=candidate_id, rank=1, score=0.85, explanation="Good fit"),
        ]
    )

    matches = _run_async(matching_service.find_matches(opp, top_k=5))

    assert len(matches) == 1
    assert matches[0].user_id == candidate_id
    # Poster must not appear in candidates passed to AI
    call_args = ai_port.rank_and_explain.call_args
    candidates_passed = call_args[0][1]
    user_ids = [c.user.id for c in candidates_passed]
    assert poster_id not in user_ids
    assert candidate_id in user_ids


# ----- Phase 1: open_to filter -----


def test_phase1_excludes_user_when_opp_type_not_in_open_to(
    matching_service, user_repo, connection_repo, embedding_port, ai_port
):
    poster_id = "poster-1"
    candidate_id = "candidate-1"
    opp = _make_opportunity(posted_by=poster_id, opp_type=OpportunityType.JOB)
    candidate = _make_user(candidate_id, open_to=["project"])  # no "job"

    embedding_port.search_similar = MagicMock(
        return_value=[{"user_id": candidate_id, "score": 0.9}]
    )
    user_repo.get_by_id = MagicMock(return_value=candidate)

    matches = _run_async(matching_service.find_matches(opp, top_k=5))

    assert matches == []
    ai_port.rank_and_explain.assert_not_called()


# ----- Phase 1: network boosts -----


def test_phase1_first_degree_gets_boost(
    matching_service, user_repo, match_repo, connection_repo, embedding_port, ai_port
):
    poster_id = "poster-1"
    first_degree_id = "first-1"
    opp = _make_opportunity(posted_by=poster_id)
    first_degree_user = _make_user(first_degree_id, open_to=["job"])
    poster_user = _make_user(poster_id, open_to=["job"])

    embedding_port.search_similar = MagicMock(
        return_value=[{"user_id": first_degree_id, "score": 0.5}]
    )
    user_repo.get_by_id = MagicMock(
        side_effect=lambda uid: first_degree_user if uid == first_degree_id else (poster_user if uid == poster_id else None)
    )
    conn = Connection(
        id="conn-1",
        user_a=poster_id,
        user_b=first_degree_id,
        source=ConnectionSource.MANUAL,
    )
    connection_repo.get_connections = MagicMock(return_value=[conn])
    connection_repo.get_second_degree = MagicMock(return_value={})

    ai_port.rank_and_explain = AsyncMock(
        return_value=[
            RankedMatch(user_id=first_degree_id, rank=1, score=0.65, explanation="Match"),
        ]
    )

    matches = _run_async(matching_service.find_matches(opp, top_k=5))

    assert len(matches) == 1
    assert matches[0].user_id == first_degree_id
    assert matches[0].embedding_score == 0.5
    assert matches[0].network_score == FIRST_DEGREE_BOOST
    assert matches[0].score == 0.65


def test_phase1_second_degree_gets_boost(
    matching_service, user_repo, match_repo, connection_repo, embedding_port, ai_port
):
    poster_id = "poster-1"
    second_degree_id = "second-1"
    opp = _make_opportunity(posted_by=poster_id)
    second_user = _make_user(second_degree_id, open_to=["job"])

    embedding_port.search_similar = MagicMock(
        return_value=[{"user_id": second_degree_id, "score": 0.5}]
    )
    user_repo.get_by_id = MagicMock(return_value=second_user)
    connection_repo.get_connections = MagicMock(return_value=[])
    connection_repo.get_second_degree = MagicMock(
        return_value={second_degree_id: ["Alice"]}
    )

    ai_port.rank_and_explain = AsyncMock(
        return_value=[
            RankedMatch(user_id=second_degree_id, rank=1, score=0.58, explanation="Match"),
        ]
    )

    matches = _run_async(matching_service.find_matches(opp, top_k=5))

    assert len(matches) == 1
    assert matches[0].network_score == SECOND_DEGREE_BOOST
    assert matches[0].embedding_score == 0.5


# ----- Phase 1: top_k -----


def test_phase1_returns_only_top_k_candidates_to_ai(
    matching_service, user_repo, connection_repo, embedding_port, ai_port
):
    poster_id = "poster-1"
    opp = _make_opportunity(posted_by=poster_id)
    top_k = 2
    # Return 4 valid candidates from embedding
    ids = ["u1", "u2", "u3", "u4"]
    embedding_port.search_similar = MagicMock(
        return_value=[{"user_id": i, "score": 0.9 - j * 0.1} for j, i in enumerate(ids)]
    )
    user_repo.get_by_id = MagicMock(
        side_effect=lambda uid: _make_user(uid, open_to=["job"]) if uid in ids else None
    )

    ai_port.rank_and_explain = AsyncMock(
        return_value=[
            RankedMatch(user_id=ids[0], rank=1, score=0.9, explanation=""),
            RankedMatch(user_id=ids[1], rank=2, score=0.8, explanation=""),
        ]
    )

    matches = _run_async(matching_service.find_matches(opp, top_k=top_k))

    assert len(matches) == 2
    call_args = ai_port.rank_and_explain.call_args
    candidates_passed = call_args[0][1]
    assert len(candidates_passed) == top_k


# ----- Phase 1: empty retrieval -----


def test_phase1_empty_embedding_returns_empty_no_ai_call(
    matching_service, user_repo, connection_repo, embedding_port, ai_port
):
    opp = _make_opportunity()
    embedding_port.search_similar = MagicMock(return_value=[])

    matches = _run_async(matching_service.find_matches(opp, top_k=5))

    assert matches == []
    ai_port.rank_and_explain.assert_not_called()


# ----- Phase 2: Match build and persist -----


def test_phase2_match_has_correct_fields_from_ranked_and_candidate(
    matching_service, user_repo, match_repo, connection_repo, embedding_port, ai_port
):
    candidate_id = "candidate-1"
    opp_id = "opp-1"
    opp = _make_opportunity(opp_id=opp_id, posted_by="poster-1")
    candidate = _make_user(candidate_id, open_to=["job"])

    embedding_port.search_similar = MagicMock(
        return_value=[{"user_id": candidate_id, "score": 0.7}]
    )
    user_repo.get_by_id = MagicMock(return_value=candidate)
    ai_port.rank_and_explain = AsyncMock(
        return_value=[
            RankedMatch(
                user_id=candidate_id,
                rank=1,
                score=0.82,
                explanation="Strong fit for the role",
            ),
        ]
    )

    matches = _run_async(matching_service.find_matches(opp, top_k=5))

    assert len(matches) == 1
    m = matches[0]
    assert m.opportunity_id == opp_id
    assert m.user_id == candidate_id
    assert m.score == 0.82
    assert m.embedding_score == 0.7
    assert m.network_score == 0.0
    assert m.explanation == "Strong fit for the role"
    assert m.rank == 1
    assert m.id is not None


def test_phase2_create_batch_called_with_matches(
    matching_service, user_repo, match_repo, connection_repo, embedding_port, ai_port
):
    candidate_id = "candidate-1"
    opp = _make_opportunity(opp_id="opp-1")
    embedding_port.search_similar = MagicMock(
        return_value=[{"user_id": candidate_id, "score": 0.8}]
    )
    user_repo.get_by_id = MagicMock(return_value=_make_user(candidate_id, open_to=["job"]))
    ai_port.rank_and_explain = AsyncMock(
        return_value=[
            RankedMatch(user_id=candidate_id, rank=1, score=0.8, explanation="Ok"),
        ]
    )

    _run_async(matching_service.find_matches(opp, top_k=5))

    match_repo.create_batch.assert_called_once()
    batch = match_repo.create_batch.call_args[0][0]
    assert len(batch) == 1
    assert batch[0].user_id == candidate_id


# ----- get_matches -----


def test_get_matches_delegates_to_repo(matching_service, match_repo):
    opportunity_id = "opp-123"
    stored = [
        MagicMock(
            id="m1",
            opportunity_id=opportunity_id,
            user_id="u1",
            score=0.9,
            embedding_score=0.8,
            network_score=0.1,
            explanation="Good",
            rank=1,
            created_at=datetime.now(timezone.utc),
        ),
    ]
    match_repo.get_by_opportunity = MagicMock(return_value=stored)

    result = matching_service.get_matches(opportunity_id)

    match_repo.get_by_opportunity.assert_called_once_with(opportunity_id)
    assert result is stored


# ----- Integration-style: real DB, mocked embedding/AI -----


def test_find_matches_integration_real_repos_mocked_embedding_ai():
    """Full flow with real SQLite + repos; embedding and AI mocked."""
    import os
    import tempfile

    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.adapters.persistence.database import Base
    from app.adapters.persistence import models  # noqa: F401
    from app.adapters.persistence.connection_repo import SqlConnectionRepository
    from app.adapters.persistence.match_repo import SqlMatchRepository
    from app.adapters.persistence.opportunity_repo import SqlOpportunityRepository
    from app.adapters.persistence.user_repo import SqlUserRepository

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        engine = create_engine(
            f"sqlite:///{path}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = session_factory()

        user_repo = SqlUserRepository(session)
        connection_repo = SqlConnectionRepository(session)
        match_repo = SqlMatchRepository(session)
        opportunity_repo = SqlOpportunityRepository(session)

        poster = User(
            id="poster-1",
            name="Poster",
            bio="",
            skills=[],
            interests=[],
            open_to=["job"],
            created_at=datetime.now(timezone.utc),
        )
        candidate = User(
            id="candidate-1",
            name="Candidate",
            bio="",
            skills=[],
            interests=[],
            open_to=["job"],
            created_at=datetime.now(timezone.utc),
        )
        user_repo.create(poster)
        user_repo.create(candidate)

        conn = Connection(
            id="conn-1",
            user_a=poster.id,
            user_b=candidate.id,
            source=ConnectionSource.MANUAL,
        )
        connection_repo.create(conn)

        opp = Opportunity(
            id="opp-1",
            title="Backend role",
            description="Python backend",
            type=OpportunityType.JOB,
            posted_by=poster.id,
            created_at=datetime.now(timezone.utc),
        )
        opportunity_repo.create(opp)

        embedding = MagicMock()
        embedding.search_similar = MagicMock(
            return_value=[{"user_id": candidate.id, "score": 0.75}]
        )
        ai = MagicMock()
        ai.rank_and_explain = AsyncMock(
            return_value=[
                RankedMatch(
                    user_id=candidate.id,
                    rank=1,
                    score=0.9,
                    explanation="Great fit",
                ),
            ]
        )

        service = MatchingService(
            user_repo=user_repo,
            match_repo=match_repo,
            connection_repo=connection_repo,
            embedding=embedding,
            ai=ai,
        )

        matches = _run_async(service.find_matches(opp, top_k=5))

        assert len(matches) == 1
        assert matches[0].user_id == candidate.id
        assert matches[0].network_score == FIRST_DEGREE_BOOST
        assert matches[0].embedding_score == 0.75

        stored = service.get_matches(opp.id)
        assert len(stored) == 1
        assert stored[0].user_id == candidate.id
        assert stored[0].explanation == "Great fit"

        session.close()
    finally:
        Base.metadata.drop_all(bind=engine)
        try:
            os.unlink(path)
        except OSError:
            pass
