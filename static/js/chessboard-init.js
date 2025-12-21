$(document).ready(function () {

    let board;
    let pendingPromotion = null;
    let lastPosition = null;   // NEW - always store before move

    board = Chessboard('board', {
        draggable: true,
        position: 'start',
        pieceTheme: '/static/images/chesspieces/wikipedia/{piece}.png',

        onDragStart: function () {
            // snapshot BEFORE illegal moves
            lastPosition = board.position();
        },

        onDrop: function (source, target, piece) {

            const promotionCheck = detectPromotion(source, target, piece);

            if (promotionCheck.promotionNeeded) {

                pendingPromotion = { source, target, oldPos: lastPosition };
                board.draggable = false;  // Disable dragging during promotion choice

                showPromotionDialog(function(selectedPiece) {
                    sendMove(pendingPromotion.source, pendingPromotion.target, selectedPiece);
                });

                return;
            }

            sendMove(source, target);
        }
    });

    // Send move to server
    function sendMove(source, target, promotionPiece=null) {

        board.draggable = false;  // Disable dragging during move

        const payload = { from: source, to: target };
        if (promotionPiece) payload.promotion = promotionPiece;

        $.ajax({
            url: "/move",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(payload),

            success: function (response) {

                board.draggable = true;  // Re-enable dragging

                if (response.status === "ok") {

                    pendingPromotion = null;

                    board.position(response.fen);
                    updateStatus(response.turn, response.check, response.checkmate, response.stalemate);
                    updateMoveHistory(response.move_history);
                    updateCaptured(response.captured_pieces);

                } else {

                    rollbackPosition();   // unified rollback
                    alert("Illegal move!");
                }
            },

            error: function(xhr) {
                board.draggable = true;  // Re-enable dragging
                rollbackPosition();
                const errorMsg = xhr.responseJSON && xhr.responseJSON.message ? xhr.responseJSON.message : "Server error";
                alert(errorMsg);
            }
        });
    }

    // properly undo illegal moves
    function rollbackPosition() {

        if (pendingPromotion) {
            board.position(pendingPromotion.oldPos);
            pendingPromotion = null;
        } else if (lastPosition) {
            board.position(lastPosition);
        }
    }

    function detectPromotion(source, target, piece) {

        // only trigger for pawn
        if (piece[1] !== 'P') {
            return { promotionNeeded: false };
        }

        const isWhite = piece.startsWith('w');
        const finalRank = isWhite ? "8" : "1";

        if (target.endsWith(finalRank)) {
            return { promotionNeeded: true };
        }

        return { promotionNeeded: false };
    }

    function showPromotionDialog(callback) {

        $("#promotion-dialog").remove();

        const html = `
        <div id="promotion-dialog" style="
            position:fixed;
            top:50%;left:50%;
            transform:translate(-50%,-50%);
            background:#fff;
            padding:20px;
            border:2px solid black;
            z-index:9999;">
            <p>Promote pawn to:</p>
            <button class="promote" data-piece="q">Queen</button>
            <button class="promote" data-piece="r">Rook</button>
            <button class="promote" data-piece="b">Bishop</button>
            <button class="promote" data-piece="n">Knight</button>
            <button id="cancel-promotion">Cancel</button>
        </div>`;

        $("body").append(html);

        $(".promote").click(function() {
            const selectedPiece = $(this).data("piece");
            $("#promotion-dialog").remove();
            callback(selectedPiece);
        });

        $("#cancel-promotion").click(function() {
            $("#promotion-dialog").remove();
            board.draggable = true;  // Re-enable dragging on cancel
            rollbackPosition();
        });
    }

    $("#reset-btn").click(function () {
        $.post("/reset", function(response) {
            if (response.status === "ok") {
                pendingPromotion = null;
                lastPosition = null;
                board.start();
                updateStatus('white', false, false, false);
                updateMoveHistory([]);
                updateCaptured({ white: [], black: [] });
            }
        });
    });

    function updateStatus(turn, check, checkmate, stalemate) {
        let status = turn === 'white' ? "White's turn" : "Black's turn";
        if (check) status += " - Check!";
        if (checkmate) status = turn === 'white' ? "Black wins — Checkmate!" : "White wins — Checkmate!";
        if (stalemate) status = "Draw by stalemate";
        $("#game-status").text(status);
    }

    function updateMoveHistory(history) {
        if (!Array.isArray(history)) return;
        $("#move-history").html(history.map(m => `<li>${m}</li>`).join(""));
    }

    function updateCaptured(captured) {
        if (!captured || !captured.white || !captured.black) return;
        $("#white-captured").text(captured.white.join(" "));
        $("#black-captured").text(captured.black.join(" "));
    }

});
