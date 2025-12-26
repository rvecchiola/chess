# Promotion Edge Cases - Detailed Fix Guide

## Analysis of Current Failures

After applying the Chessboard.js selector fixes, 6 of 7 tests are still failing due to **FEN position complexity**, not selector issues.

### Root Cause: Complex FEN Positions with Many Pieces

The promotion tests use realistic starting positions with many pieces, which after `setup_board_position()` page reload, may not render correctly or pieces may not be where tests expect them.

**Example Problem**:
```python
# Current FEN in test
fen = "r1bqkbnr/P1pppppp/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1"
# This has 29 pieces! After page reload, Chessboard.js reinitializes all pieces
# The pawn on a7 might render but DOM might not be fully updated when test tries to drag
```

### Solution: Simplify FEN Positions Like Castling Tests Did

Just as we simplified castling tests with minimal FEN positions (e.g., `'5r2/8/8/8/8/8/8/4K2R'`), we should simplify promotion tests.

---

## Recommended FEN Simplifications

### Test 1: test_promotion_popup_blocked_by_opponent_piece
**Purpose**: Verify illegal move (pawn blocked) - no dialog

**Current FEN**:
```
r1bqkbnr/P1pppppp/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1
```
(29 pieces - too complex)

**Proposed FEN**:
```
r7/P7/8/8/8/8/8/8 w - - 0 1
```
(2 pieces - white pawn on a7, black rook on a8)
- Clear intent: pawn can't move straight (blocked)
- No other pieces to interfere
- Minimal rendering complexity after reload

### Test 2: test_promotion_popup_invalid_diagonal_no_capture
**Purpose**: Verify invalid diagonal move - no dialog

**Current FEN**:
```
rn1qkbnr/Ppppppp1/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1
```

**Proposed FEN**:
```
8/P7/8/8/8/8/8/8 w - - 0 1
```
(1 piece - white pawn on a7 only)
- Clear: no pieces to capture on diagonals
- No blocking pieces
- Test illegal diagonal move to b8

### Test 3: test_promotion_popup_only_appears_for_valid_straight_move
**Purpose**: Verify legal straight move triggers dialog

**Current FEN**:
```
1nbqkbnr/Ppppppp1/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1
```

**Proposed FEN**:
```
8/P7/8/8/8/8/8/8 w - - 0 1
```
(1 piece - white pawn on a7)
- Clear: legal move to a8
- Dialog SHOULD appear
- Promote to queen

### Test 4: test_promotion_popup_appears_for_valid_capture
**Purpose**: Verify diagonal capture triggers dialog

**Current FEN**:
```
rb1qkbnr/Ppppppp1/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1
```

**Proposed FEN**:
```
r7/P7/8/8/8/8/8/8 w - - 0 1
```
(2 pieces - white pawn on a7, black rook on b8)
- Clear: pawn can capture rook
- Dialog SHOULD appear
- Promote to queen, rook tracked as captured

### Test 5: test_black_pawn_promotion_straight_move
**Purpose**: Black pawn promotion (rank 1 instead of rank 8)

**Current FEN**:
```
rnbqkbnr/pppppppp/8/8/8/8/1p6/RNBQKBNR b KQkq - 0 1
```

**Proposed FEN**:
```
8/8/8/8/8/8/1p6/8 b - - 0 1
```
(1 piece - black pawn on b2)
- Clear: legal move to b1
- Dialog SHOULD appear
- It's black's turn

### Test 6: test_promotion_all_piece_types
**Purpose**: Promote to each of 4 piece types

**Current FEN**:
```
1nbqkbnr/Ppppppp1/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1
```

**Proposed FEN**:
```
8/P7/8/8/8/8/8/8 w - - 0 1
```
(Same as Test 3 - white pawn on a7, test all 4 promotion options)

### Test 7: test_promotion_with_capture_updates_captured_pieces
**Purpose**: Verify capture tracked with promotion

**Current FEN**:
```
rb1qkbnr/Ppppppp1/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1
```

**Proposed FEN**:
```
r7/P7/8/8/8/8/8/8 w - - 0 1
```
(Same as Test 4 - white pawn on a7, black rook on b8)

---

## Implementation Steps

1. **Update each test's FEN** to use simplified version
2. **Simplify move_history** - most can be empty `[]`
3. **Keep assertions** - they're testing the right things
4. **Re-run tests** - should all pass now

---

## Example Fix Pattern

```python
# BEFORE: Complex FEN with 29 pieces
def test_promotion_popup_appears_for_valid_capture(page: Page, live_server):
    page.goto(live_server)
    
    fen = "rb1qkbnr/Ppppppp1/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    setup_board_position(
        page,
        fen,
        move_history=["a4", "h6", "a5", "h5", "a6"],
        captured_pieces={"white": [], "black": []},
        special_moves=[]
    )
    
    # Test pawn capture and promotion
    drag_piece(page, "a7", "b8")
    # ...

# AFTER: Minimal FEN with 2 pieces
def test_promotion_popup_appears_for_valid_capture(page: Page, live_server):
    page.goto(live_server)
    
    fen = "r7/P7/8/8/8/8/8/8 w - - 0 1"
    
    setup_board_position(
        page,
        fen,
        move_history=[],  # Much simpler
        captured_pieces={"white": [], "black": []},
        special_moves=[]
    )
    
    # Test pawn capture and promotion  
    drag_piece(page, "a7", "b8")
    # ...
```

---

## Benefits of FEN Simplification

1. **Faster rendering** - Fewer pieces to render after reload
2. **Clearer intent** - Test name matches FEN position
3. **Reduced complexity** - Fewer potential DOM issues
4. **Matches castling pattern** - Consistent with other edge case tests
5. **Faster tests** - Less to process in Playwright

---

## Validation Checklist

After applying FEN simplifications:

- [ ] Update all 7 test FENs
- [ ] Update move_history to be minimal
- [ ] Run tests: `pytest tests/test_promotion_edge_cases.py -v`
- [ ] Expected: All 8 tests pass ✅
- [ ] Verify promotion dialog appears/doesn't appear correctly
- [ ] Verify captured pieces tracked
- [ ] Verify error messages on illegal moves
