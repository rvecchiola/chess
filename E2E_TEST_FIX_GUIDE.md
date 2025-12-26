# E2E Test Refactoring Guide

## Problem
Playwright E2E tests fail because they use brittle DOM selectors that don't match Chessboard.js's actual structure:

**What tests expect**: `[data-square="e2"] .piece-417db[data-piece="wP"]`
**What Chessboard.js creates**: `<div data-square="e2"><img src="..."></div>`

The hash in `.piece-417db` changes every time the board reinitializes.

## Solution
Use robust selectors that work with Chessboard.js's actual DOM structure.

## Helper Functions Available
Location: `tests/helper.py`

### 1. `get_piece_in_square(page, square)`
Get the img element for a piece in a specific square.

```python
from tests.helper import get_piece_in_square

# Instead of:
piece = page.locator('[data-square="e2"] .piece-417db[data-piece="wP"]')

# Use:
piece = get_piece_in_square(page, "e2")
expect(piece).to_have_count(1)  # Piece exists
```

### 2. `drag_piece(page, from_square, to_square)`
Drag a piece from one square to another using robust selectors.

```python
from tests.helper import drag_piece

# Instead of:
e2_piece = page.locator('[data-square="e2"] .piece-417db')
e4_square = page.locator('[data-square="e4"]')
e2_piece.drag_to(e4_square)

# Use:
drag_piece(page, "e2", "e4")
```

## Selector Replacement Strategy

### Pattern 1: Check if piece exists in square
```python
# Old (brittle - uses non-existent data-piece attribute)
piece = page.locator('[data-square="e2"] .piece-417db[data-piece="wP"]')
expect(piece).to_have_count(1)

# New (robust)
piece = get_piece_in_square(page, "e2")
expect(piece).to_have_count(1)
```

### Pattern 2: Drag piece to square
```python
# Old (brittle - uses dynamic class name)
e2_piece = page.locator('[data-square="e2"] .piece-417db')
e4_square = page.locator('[data-square="e4"]')
e2_piece.drag_to(e4_square)

# New (robust)
drag_piece(page, "e2", "e4")
```

### Pattern 3: Check square is empty
```python
# Old (brittle)
empty = page.locator('[data-square="e5"] .piece-417db')
expect(empty).to_have_count(0)

# New (robust)
empty = get_piece_in_square(page, "e5")
expect(empty).to_have_count(0)
```

## Test Files to Fix

### test_e2e_playwright.py (8 tests)
1. `test_pawn_promotion_modal_appears_with_setup` (lines ~375-405)
2. `test_pawn_promotion_queen_selection_with_setup` (lines ~408-440)
3. `test_pawn_promotion_cancel_button_with_setup` (lines ~443-475)
4. `test_check_status_displays_with_setup` (lines ~560-600)
5. `test_en_passant_capture_ui_with_exact_setup` (lines ~730-770)
6. `test_castling_kingside_with_exact_setup` (lines ~590-630)
7. `test_checkmate_fool_mate_with_setup` (lines ~760-805)

### test_promotion_edge_cases.py (7 tests)
1. `test_promotion_popup_blocked_by_opponent_piece`
2. `test_promotion_popup_invalid_diagonal_no_capture`
3. `test_promotion_popup_only_appears_for_valid_straight_move`
4. `test_promotion_popup_appears_for_valid_capture`
5. `test_black_pawn_promotion_straight_move`
6. `test_promotion_all_piece_types`
7. `test_promotion_with_capture_updates_captured_pieces`

## Implementation Checklist

- [ ] Add import: `from tests.helper import get_piece_in_square, drag_piece`
- [ ] Replace all `[data-square="X"] .piece-417db[data-piece="Y"]` with `get_piece_in_square(page, "X")`
- [ ] Replace all `[data-square="X"] .piece-417db` with `get_piece_in_square(page, "X")`
- [ ] Replace all piece drag operations with `drag_piece(page, from_sq, to_sq)`
- [ ] Verify `setup_board_position()` helper is called before tests using position setup
- [ ] Add `page.wait_for_timeout(500)` after board operations to ensure DOM updates
- [ ] Run tests: `pytest tests/test_e2e_playwright.py tests/test_promotion_edge_cases.py -v`

## Key Points

1. **Chessboard.js creates `<img>` elements**, not divs with data attributes
2. **The `.piece-XXXXX` class has a dynamic suffix** that changes on each board initialization
3. **After page reload**, all piece class names change - selectors must be more generic
4. **Use the helper functions** to abstract away Chessboard.js implementation details

## Example Fix: test_pawn_promotion_modal_appears_with_setup

```python
# BEFORE (Broken)
def test_pawn_promotion_modal_appears_with_setup(page: Page, live_server):
    page.goto(live_server)
    promotion_fen = "r1bqkbnr/Ppppppp1/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1"
    setup_board_position(page, promotion_fen, ...)
    
    # BROKEN: [data-piece="wP"] doesn't exist in DOM
    a7_pawn = page.locator('[data-square="a7"] .piece-417db[data-piece="wP"]')
    expect(a7_pawn).to_have_count(1)
    
    # BROKEN: .piece-417db class changed after page reload
    page.locator('[data-square="a7"] .piece-417db').drag_to(
        page.locator('[data-square="a8"]')
    )

# AFTER (Fixed)
def test_pawn_promotion_modal_appears_with_setup(page: Page, live_server):
    from tests.helper import get_piece_in_square, drag_piece
    
    page.goto(live_server)
    promotion_fen = "r1bqkbnr/Ppppppp1/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1"
    setup_board_position(page, promotion_fen, ...)
    
    # FIXED: Use robust selector helper
    a7_pawn = get_piece_in_square(page, "a7")
    expect(a7_pawn).to_have_count(1)
    
    # FIXED: Use drag_piece helper
    drag_piece(page, "a7", "a8")
    page.wait_for_timeout(1000)
    
    promotion_dialog = page.locator("#promotion-dialog")
    expect(promotion_dialog).to_be_visible()
```

## Testing the Fix
```bash
# Run all tests to verify
pytest tests/test_e2e_playwright.py tests/test_promotion_edge_cases.py -v

# Or just run a specific test
pytest tests/test_e2e_playwright.py::test_pawn_promotion_modal_appears_with_setup -v
```
