import pytest
import json
import chess
from app import app  # make sure your Flask app is imported correctly

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def reset_board(client):
    client.post("/reset")

def make_move(client, from_sq, to_sq, promotion=None):
    payload = {"from": from_sq, "to": to_sq}
    if promotion:
        payload["promotion"] = promotion
    rv = client.post("/move", data=json.dumps(payload), content_type="application/json")
    return rv.get_json()

def test_home(client, monkeypatch):
    # Monkeypatch render_template to avoid TemplateNotFound
    monkeypatch.setattr("routes.render_template", lambda x: "OK")
    rv = client.get("/")
    assert rv.status_code == 200

def test_reset(client):
    reset_board(client)
    # After reset, board should be at starting position
    rv = make_move(client, "e2", "e4")
    assert rv["status"] == "ok"

def test_legal_move(client):
    reset_board(client)
    rv = make_move(client, "e2", "e4")
    assert rv["status"] == "ok"
    # Verify e4 has white pawn
    board = chess.Board(rv["fen"])
    assert board.piece_at(chess.E4).symbol() == "P"

def test_illegal_move(client):
    reset_board(client)
    rv = make_move(client, "e2", "e5")  # invalid move
    assert rv["status"] == "illegal"

def test_promotion(client):
    reset_board(client)
    # Move a white pawn to promotion square
    moves = [("h2", "h4"), ("g7", "g5"), ("h4", "h5"), ("g5", "g4"), ("h5", "h6"), ("g4", "g3"), ("h6", "h7")]
    for from_sq, to_sq in moves:
        make_move(client, from_sq, to_sq)
    # Now promote pawn to queen
    rv = make_move(client, "h7", "h8", promotion="q")
    assert rv["status"] == "ok"
    board = chess.Board(rv["fen"])
    piece = board.piece_at(chess.H8)
    assert piece.symbol().upper() == "Q"

def test_capture(client):
    reset_board(client)
    # Move white pawn to capture
    make_move(client, "e2", "e4")
    make_move(client, "d7", "d5")
    rv = make_move(client, "e4", "d5")
    assert rv["status"] == "ok"
    board = chess.Board(rv["fen"])
    piece = board.piece_at(chess.D5)
    assert piece.symbol() == "P"

def test_en_passant(client):
    reset_board(client)
    # Set up en passant via API
    make_move(client, "e2", "e4")
    make_move(client, "d7", "d5")
    make_move(client, "e4", "e5")
    make_move(client, "f7", "f5")
    rv = make_move(client, "e5", "f6")
    assert rv["status"] == "ok"
    board = chess.Board(rv["fen"])
    assert board.piece_at(chess.F5) is None
    assert board.piece_at(chess.F6).symbol() == "P"
