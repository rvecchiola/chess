import chess
import pytest
from ai import material_score

@pytest.mark.unit
def test_material_even_start():
    board = chess.Board()
    assert material_score(board) == 0


@pytest.mark.unit
def test_white_up_pawn():
    board = chess.Board()
    board.remove_piece_at(chess.A7)  # remove black pawn
    assert material_score(board) == 100


@pytest.mark.unit
def test_black_up_queen():
    board = chess.Board()
    board.remove_piece_at(chess.D1)  # remove white queen
    assert material_score(board) == -900


@pytest.mark.unit
def test_multiple_piece_difference():
    board = chess.Board()
    board.remove_piece_at(chess.B1)  # knight
    board.remove_piece_at(chess.C1)  # bishop
    assert material_score(board) == -(320 + 330)


@pytest.mark.unit
def test_promotion_results_in_queen_material():
    board = chess.Board("8/P7/8/8/8/8/8/8 w - - 0 1")
    board.push(chess.Move.from_uci("a7a8q"))
    assert material_score(board) == 900