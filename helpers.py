from flask import session
import chess
# -------------------------------------------------------------------
# Session Helpers
# -------------------------------------------------------------------

def init_game():
    session['fen'] = chess.STARTING_FEN
    session['move_history'] = []
    session['captured_pieces'] = {'white': [], 'black': []}
    session['special_moves'] = []


def get_game_state():
    if 'fen' not in session or session['fen'] is None:
        init_game()

    board = chess.Board()
    move_history = session.get('move_history', [])
    if move_history:
        for san in move_history:
            board.push_san(san)
    else:
        board = chess.Board(session['fen'])
    captured_pieces = session.get('captured_pieces', {'white': [], 'black': []})
    special_moves = session.get('special_moves', [])

    return board, move_history, captured_pieces, special_moves


def save_game_state(board, move_history, captured_pieces, special_moves):
    session['fen'] = board.fen()
    session['move_history'] = move_history
    session['captured_pieces'] = captured_pieces
    session['special_moves'] = special_moves

## illegal moves helper

def explain_illegal_move(board, move):
    # Move not even pseudo-legal (wrong movement)
    if not board.is_pseudo_legal(move):
        return "That piece cannot move like that."

    # Move would leave king in check (pins, discovered checks)
    if board.is_into_check(move):
        return "Illegal move — your king would be in check."

    # Castling specific checks
    if board.piece_at(move.from_square).piece_type == chess.KING:
        if board.is_check():
            return "You cannot castle while in check."

    return "Illegal move."    