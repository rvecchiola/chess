from flask import render_template, request, jsonify
import chess
import random

# Global board for single-player vs AI
board = chess.Board()

def register_routes(app):

    @app.route("/")
    def home():
        return render_template("chess.html")

    @app.route("/move", methods=["POST"])
    def move():
        global board
        data = request.get_json()
        from_square = data.get("from")
        to_square = data.get("to")
        move_uci = from_square + to_square

        try:
            player_move = chess.Move.from_uci(move_uci)
            if player_move in board.legal_moves:
                board.push(player_move)

                # AI move (random)
                if not board.is_game_over():
                    ai_move = random.choice(list(board.legal_moves))
                    board.push(ai_move)

                turn = 'white' if board.turn == chess.WHITE else 'black'
                check = board.is_check()
                checkmate = board.is_checkmate()
                stalemate = board.is_stalemate()
                return jsonify({
                    "status": "ok",
                    "fen": board.fen(),
                    "turn": turn,
                    "check": check,
                    "checkmate": checkmate,
                    "stalemate": stalemate
                })
            else:
                return jsonify({"status": "illegal"})
        except:
            return jsonify({"status": "error"})

    @app.route("/reset", methods=["POST"])
    def reset():
        global board
        board.reset()
        return jsonify({"status": "ok"})
