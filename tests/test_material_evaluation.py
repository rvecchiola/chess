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

@pytest.mark.unit
def test_promotion_material_gain():
    """Test that promoting from pawn to queen is +800 material gain"""
    board = chess.Board("8/P7/8/8/8/8/8/8 w - - 0 1")
    
    # Before promotion: white has 1 pawn = +100
    assert material_score(board) == 100
    
    # After promotion: white has 1 queen = +900
    board.push(chess.Move.from_uci("a7a8q"))
    assert material_score(board) == 900
    
    # Net gain = 900 - 100 = 800
    assert 900 - 100 == 800

@pytest.mark.unit
def test_en_passant_material_tracking():
    """Test material count after en passant capture"""
    # Set up en passant position: white pawn on e5, black pawn moves d7-d5
    board = chess.Board("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    
    # Before en passant: material is equal (both sides have same pieces)
    initial_material = material_score(board)
    
    # White captures en passant e5xd6
    board.push(chess.Move.from_uci("e5d6"))
    
    # After en passant: white captured black pawn, so white is +100 material
    final_material = material_score(board)
    assert final_material == initial_material + 100