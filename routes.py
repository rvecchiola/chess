from flask import render_template, request, jsonify
import chess
import random

# Global state
board = chess.Board()
move_history = []
captured_pieces = {'white': [], 'black': []}

def register_routes(app):

    @app.route("/")
    def home():
        return render_template("chess.html")
    
    @app.route("/move", methods=["POST"])
    def move():
        global board, move_history, captured_pieces

        data = request.get_json()
        from_sq = data.get("from")
        to_sq = data.get("to")
        promotion = data.get("promotion")

        # Build UCI move string including promotion
        if promotion:
            uci = f"{from_sq}{to_sq}{promotion}"
        else:
            uci = f"{from_sq}{to_sq}"

        print("\n--- DEBUG ---")
        print("Board before move:", board.fen())
        print("Move received:", uci)

        try:
            move = chess.Move.from_uci(uci)
            legal_moves = [m.uci() for m in board.legal_moves]

            print("Legal moves:", legal_moves)

            if move not in board.legal_moves:
                print("Move is illegal")
                return jsonify({"status": "illegal", "fen": board.fen()})

            # Compute SAN before pushing
            move_san = board.san(move)

            # Track capture by player
            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    color_key = "white" if captured.color == chess.WHITE else "black"
                    captured_pieces[color_key].append(captured.symbol())
                    print("Player captured:", captured.symbol())

            board.push(move)
            move_history.append(move_san)

            # AI automatically moves
            if not board.is_game_over():
                ai_move = random.choice(list(board.legal_moves))
                ai_san = board.san(ai_move)

                if board.is_capture(ai_move):
                    captured = board.piece_at(ai_move.to_square)
                    if captured:
                        color_key = "white" if captured.color == chess.WHITE else "black"
                        captured_pieces[color_key].append(captured.symbol())
                        print("AI captured:", captured.symbol())

                board.push(ai_move)
                move_history.append(ai_san)

            turn = "white" if board.turn == chess.WHITE else "black"
            check = board.is_check()
            checkmate = board.is_checkmate()
            stalemate = board.is_stalemate()

            print("Board after moves:", board.fen())
            print("--- END DEBUG ---\n")

            return jsonify({
                "status": "ok",
                "fen": board.fen(),
                "turn": turn,
                "check": check,
                "checkmate": checkmate,
                "stalemate": stalemate,
                "move_history": move_history,
                "captured_pieces": captured_pieces
            })

        except Exception as e:
            print("ERROR:", e)
            return jsonify({"status": "illegal", "message": str(e)})

    @app.route("/reset", methods=["POST"])
    def reset():
        global board, move_history, captured_pieces
        board.reset()
        move_history = []
        captured_pieces = {'white': [], 'black': []}
        return jsonify({"status": "ok"})
