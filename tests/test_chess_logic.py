import chess
import pytest

@pytest.fixture
def new_board():
    """Return a fresh chess board."""
    return chess.Board()

def test_initial_position(new_board):
    assert new_board.fen().startswith("rnbqkbnr")

def test_legal_pawn_move(new_board):
    move = chess.Move.from_uci("e2e4")
    assert move in new_board.legal_moves
    new_board.push(move)
    assert new_board.piece_at(chess.E4).symbol() == "P"

def test_illegal_pawn_move(new_board):
    move = chess.Move.from_uci("e2e5")
    assert move not in new_board.legal_moves

def test_capture(new_board):
    new_board.set_fen("8/8/8/3p4/4P3/8/8/8 w - - 0 1")
    move = chess.Move.from_uci("e4d5")
    assert move in new_board.legal_moves
    new_board.push(move)
    assert new_board.piece_at(chess.D5).symbol() == "P"

def test_promotion(new_board):
    new_board.set_fen("8/P7/8/8/8/8/8/8 w - - 0 1")
    move = chess.Move.from_uci("a7a8q")
    assert move in new_board.legal_moves
    new_board.push(move)
    assert new_board.piece_at(chess.A8).symbol().lower() == "q"

def test_en_passant(new_board):
    new_board.set_fen("8/8/8/1pP5/8/8/8/8 w - b6 0 1")
    move = chess.Move.from_uci("c5b6")
    assert move in new_board.legal_moves
    new_board.push(move)
    assert new_board.piece_at(chess.B6).symbol() == "P"
