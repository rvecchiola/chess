# Promotion Edge Cases - Test Analysis & Fixes

## Overview
The `test_promotion_edge_cases.py` file contains **7 E2E Playwright tests** that validate important promotion edge cases and bug fixes. All tests use the same DOM selector issues as the other E2E tests.

**Status**: ⚠️ 7 tests failing (DOM selector brittleness, not application bugs)

---

## Test Categories & Coverage

### Category 1: Bug Fix Tests (4 tests)
Tests that validate fixes for illegal promotion dialogs appearing:

1. **test_promotion_popup_blocked_by_opponent_piece** (✅ Logic valid, ⚠️ Selector fails)
   - Purpose: Verify dialog doesn't appear when pawn path is blocked
   - Setup: White pawn on a7, black rook on a8 (blocking)
   - Expected: Drag attempt is illegal, no dialog appears, pawn snaps back
   - Selector Issue: Uses `[data-piece="wP"]` which doesn't exist

2. **test_promotion_popup_invalid_diagonal_no_capture** (✅ Logic valid, ⚠️ Selector fails)
   - Purpose: Verify dialog doesn't appear for diagonal move when no piece to capture
   - Setup: White pawn on a7, b8 is empty
   - Expected: Illegal move, no dialog appears
   - Selector Issue: Uses `.piece-417db` (dynamic class)

3. **test_promotion_popup_only_appears_for_valid_straight_move** (✅ Logic valid, ⚠️ Selector fails)
   - Purpose: Verify dialog DOES appear for legal straight move to 8th rank
   - Setup: White pawn on a7, a8 empty
   - Expected: Dialog appears after legal move
   - Selector Issue: Uses `.piece-417db` (dynamic class)

4. **test_promotion_popup_appears_for_valid_capture** (✅ Logic valid, ⚠️ Selector fails)
   - Purpose: Verify dialog appears when pawn captures diagonally to 8th rank
   - Setup: White pawn on a7, black bishop on b8
   - Expected: Dialog appears after capture and move
   - Selector Issue: Uses `.piece-417db` (dynamic class)

### Category 2: Black Pawn Promotion Tests (2 tests)
Tests for promotion of black pawns (to rank 1):

5. **test_black_pawn_promotion_straight_move** (✅ Logic valid, ⚠️ Selector fails)
   - Purpose: Verify black pawn promotion (mirror of white tests)
   - Setup: Black pawn on b2, b1 empty, black's turn
   - Expected: Dialog appears for legal move to b1
   - Selector Issues: Uses `[data-piece="bp"]` and `.piece-417db`

6. **test_black_pawn_promotion_blocked_no_popup** (PASSED ✅)
   - Purpose: Verify no dialog for blocked black pawn
   - Status: This test passes! (It exists in file but not reported as failing)

### Category 3: Comprehensive Edge Cases (2 tests)
Tests for promotion variants and captured pieces tracking:

7. **test_promotion_all_piece_types** (✅ Logic valid, ⚠️ Selector fails)
   - Purpose: Verify promotion to all 4 piece types (Q, R, B, N)
   - Setup: Same pawn on a7, a8 empty, test all 4 promotion options
   - Expected: Dialog appears, each piece type selectable
   - Selector Issues: Uses `.piece-417db` (dynamic class)

8. **test_promotion_with_capture_updates_captured_pieces** (✅ Logic valid, ⚠️ Selector fails)
   - Purpose: Verify captured piece tracked when promoting with capture
   - Setup: White pawn on a7, black rook on b8
   - Expected: Dialog appears, capture tracked in UI
   - Selector Issue: Uses `.piece-417db` (dynamic class)

---

## Root Cause Analysis

### Problem 1: Non-existent `data-piece` Attribute
```python
# BROKEN: Chessboard.js doesn't create this attribute
a7_pawn = page.locator('[data-square="a7"] .piece-417db[data-piece="wP"]')
```

Chessboard.js renders:
```html
<div data-square="a7">
  <img src="...white-pawn.png" class="piece-417db">
</div>
```

The piece information is in the **image src**, not in a data attribute.

### Problem 2: Dynamic Piece Classes
```python
# BROKEN: The hash "417db" changes every time board initializes
page.locator('[data-square="a7"] .piece-417db')
```

After `setup_board_position()` reloads the page:
- Old class: `.piece-417db` (first load)
- New class: `.piece-a1f2c` (after reload with different pieces)
- The hash is derived from the piece image path, so it changes with board state

### Problem 3: Chessboard.js Initialization
When page is reloaded after `/test/set_position`:
1. DOM is cleared
2. Chessboard.js re-initializes
3. Piece images are re-rendered with NEW class names
4. Tests using old class names fail with "element not found"

---

## Solution Strategy

### Fix 1: Replace Dynamic Class Selectors with Robust Ones

**Pattern: Any piece selector**
```python
# OLD (Broken)
piece = page.locator('[data-square="e2"] .piece-417db[data-piece="wP"]')

# NEW (Robust)
from tests.helper import get_piece_in_square
piece = get_piece_in_square(page, "e2")
```

### Fix 2: Replace Drag Operations

**Pattern: Drag piece to square**
```python
# OLD (Broken)
e2_piece = page.locator('[data-square="e2"] .piece-417db')
e4_square = page.locator('[data-square="e4"]')
e2_piece.drag_to(e4_square)

# NEW (Robust)
from tests.helper import drag_piece
drag_piece(page, "e2", "e4")
```

### Fix 3: Update FEN Positions (Optional but Recommended)

Some FEN positions could be simplified similar to castling tests:
```python
# CURRENT (Complex with many pieces)
fen = "rnbqkbnr/pppppppp/8/8/8/8/1p6/RNBQKBNR b KQkq - 0 1"

# SIMPLER (Only necessary pieces, clearer intent)
fen = "8/8/8/8/8/8/1p6/8 b - - 0 1"
# But be careful: this might affect board rendering in tests
```

---

## Implementation Plan

### Step 1: Add Imports
Add to top of `test_promotion_edge_cases.py`:
```python
from tests.helper import get_piece_in_square, drag_piece
```

### Step 2: Fix Each Test

#### test_promotion_popup_blocked_by_opponent_piece (Line ~20)
**Changes needed: 1**
- Replace drag operation with `drag_piece()`

```python
# Before
page.locator('[data-square="a7"] .piece-417db').drag_to(
    page.locator('[data-square="a8"]')
)

# After
drag_piece(page, "a7", "a8")
```

#### test_promotion_popup_invalid_diagonal_no_capture (Line ~53)
**Changes needed: 1**
- Replace drag operation with `drag_piece()`

```python
# Before
page.locator('[data-square="a7"] .piece-417db').drag_to(
    page.locator('[data-square="b8"]')
)

# After
drag_piece(page, "a7", "b8")
```

#### test_promotion_popup_only_appears_for_valid_straight_move (Line ~112)
**Changes needed: 1**
- Replace drag operation with `drag_piece()`

```python
# Before
page.locator('[data-square="a7"] .piece-417db').drag_to(
    page.locator('[data-square="a8"]')
)

# After
drag_piece(page, "a7", "a8")
```

#### test_promotion_popup_appears_for_valid_capture (Line ~148)
**Changes needed: 1**
- Replace drag operation with `drag_piece()`

```python
# Before
page.locator('[data-square="a7"] .piece-417db').drag_to(
    page.locator('[data-square="b8"]')
)

# After
drag_piece(page, "a7", "b8")
```

#### test_black_pawn_promotion_straight_move (Line ~217)
**Changes needed: 2**
- Replace `[data-piece="bp"]` selector with `get_piece_in_square()`
- Replace drag operation with `drag_piece()`

```python
# Before
page.locator('[data-square="b2"] .piece-417db[data-piece="bp"]').drag_to(
    page.locator('[data-square="b1"]')
)

# After
drag_piece(page, "b2", "b1")
```

#### test_promotion_all_piece_types (Line ~281)
**Changes needed: 1**
- Replace drag operation with `drag_piece()`

```python
# Before
page.locator('[data-square="a7"] .piece-417db').drag_to(
    page.locator('[data-square="a8"]')
)

# After
drag_piece(page, "a7", "a8")
```

#### test_promotion_with_capture_updates_captured_pieces (Line ~321)
**Changes needed: 1**
- Replace drag operation with `drag_piece()`

```python
# Before
page.locator('[data-square="a7"] .piece-417db').drag_to(
    page.locator('[data-square="b8"]')
)

# After
drag_piece(page, "a7", "b8")
```

---

## Summary of Changes

| Test | Selector Issues | Required Fixes |
|------|-----------------|-----------------|
| test_promotion_popup_blocked_by_opponent_piece | `.piece-417db` | Replace drag with `drag_piece()` |
| test_promotion_popup_invalid_diagonal_no_capture | `.piece-417db` | Replace drag with `drag_piece()` |
| test_promotion_popup_only_appears_for_valid_straight_move | `.piece-417db` | Replace drag with `drag_piece()` |
| test_promotion_popup_appears_for_valid_capture | `.piece-417db` | Replace drag with `drag_piece()` |
| test_black_pawn_promotion_straight_move | `[data-piece="bp"]`, `.piece-417db` | Replace selector & drag |
| test_promotion_all_piece_types | `.piece-417db` | Replace drag with `drag_piece()` |
| test_promotion_with_capture_updates_captured_pieces | `.piece-417db` | Replace drag with `drag_piece()` |

**Total replacements needed: 8**

---

## Expected Results After Fix
```bash
pytest tests/test_promotion_edge_cases.py -v
# Expected: 8 passed ✅
```

All tests verify critical promotion functionality:
- ✅ Illegal promotion dialogs are blocked
- ✅ Valid promotions trigger dialog
- ✅ Black pawn promotion works
- ✅ All promotion piece types work
- ✅ Captures with promotion tracked correctly

---

## Notes

1. **No Application Code Changes Needed** - The chess application works correctly. Only test infrastructure needs updating.

2. **Test Logic is Solid** - These tests verify important edge cases that prevent bugs in the promotion system.

3. **Helper Module Available** - Use `tests/helper.py` functions instead of hard-coded selectors.

4. **FEN Positions** - Current FEN positions are complex but valid. They test promotion in realistic game scenarios. Simplification is optional.

5. **Related Tests Passing** - Promotion-related unit tests in `test_routes_api.py` all pass (test_promotion, test_promotion_to_queen, etc.), confirming the application logic is correct.
