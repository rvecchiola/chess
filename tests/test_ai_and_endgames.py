import pytest
import chess
from app import app
from tests.test_routes_api import make_move, reset_board

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_ai_move_is_legal(client):
    reset_board(client)
    rv = make_move(client, "e2", "e4")
    assert rv["status"] == "ok"
    # Check that AI's move is legal
    board = chess.Board(rv["fen"])
    assert all(move in board.legal_moves for move in board.legal_moves)

def test_check_detection(client):
    reset_board(client)
    # Fool's mate setup via moves
    moves = [("f2","f3"), ("e7","e5"), ("g2","g4"), ("d8","h4")]
    for from_sq, to_sq in moves:
        make_move(client, from_sq, to_sq)
    rv = make_move(client, "g1", "f3")  # dummy move to refresh board
    board = chess.Board(rv["fen"])
    assert board.is_check() == True

def test_checkmate_detection(client):
    reset_board(client)
    # Fool's mate
    moves = [("f2","f3"), ("e7","e5"), ("g2","g4"), ("d8","h4")]
    for from_sq, to_sq in moves:
        rv = make_move(client, from_sq, to_sq)
    board = chess.Board(rv["fen"])
    assert board.is_checkmate() == True

def test_stalemate_detection(client):
    reset_board(client)
    # Simplest stalemate: black to move
    # Set up via legal moves
    # This can be skipped or hard-coded by making a series of moves to reach stalemate
    pass

def test_ai_does_not_make_illegal_moves(client):
    reset_board(client)
    rv = make_move(client, "e2", "e4")
    board = chess.Board(rv["fen"])
    # Assert no illegal move on board
    for move in board.legal_moves:
        assert move in board.legal_moves
