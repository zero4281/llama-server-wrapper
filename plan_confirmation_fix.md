# Plan to Fix Confirmation Prompt Issues in render_confirmation()

## Summary
The `render_confirmation()` method in `ui_manager.py` has multiple text alignment and border rendering issues that deviate from the Requirements.md specification (Section 8.4). The current implementation is a Yes/No menu with navigation, but should be a simple confirmation dialog showing a status line and a prompt line.

## Issues Identified

1. **Wrong Window Dimensions**: Fixed height of 8 rows but only uses 6 rows
2. **Inconsistent Column Alignment**: Multiple conflicting padding values (2, 3, 1 spaces)
3. **Incorrect Content Width Calculations**: Inconsistent width usage (msg_width - 4, msg_width - 6)
4. **Inconsistent Button Positioning**: Hardcoded button width (12) vs actual text length (9)
5. **Wrong UI Pattern**: Shows Yes/No menu with arrow key navigation instead of simple confirmation
6. **Missing Prompt Line**: Should show "Proceed? [Y/n]:" prompt
7. **Title Bar Issue**: "Confirm" title rendered twice

## Solution Plan

### 1. Fix Window Creation
- Use appropriate height (6 rows for content + 2 for border = 8 total)
- Calculate width based on content, not fixed percentage
- Use consistent internal padding (2 spaces)

### 2. Implement Correct Layout
Layout (6 content rows + 2 border rows = 8 total):
```
Row 0: ┌─────────────────────────────────────────────┐ (border + title)
Row 1: │  ────────────────────────────────────────   │ (separator)
Row 2: │  Status line (resolved selection)            │ (content)
Row 3: │  Proceed? [Y/n]:                             │ (prompt)
Row 4: │  ────────────────────────────────────────   │ (separator - optional)
Row 5: └─────────────────────────────────────────────┘ (border)
```

### 3. Simplify Rendering
- Remove Yes/No menu navigation
- Remove arrow key instructions
- Show only status line and prompt
- Center text within content area

### 4. Fix Alignment
- Use fixed 2-space internal padding
- Calculate content width once and reuse
- Center text using `.center(width - padding * 2)`

### 5. Add Direct Input Handling
- Enter = confirm (default yes)
- y/Y = confirm
- n/N = cancel
- Esc/RESIZE/BACKSPACE = cancel
- No timeout (wait for input)

## Implementation Steps
1. **Step 1**: Read current render_confirmation() code (already read)
2. **Step 2**: Rewrite render_confirmation() with correct layout
3. **Step 3**: Test with various message lengths
4. **Step 4**: Verify alignment is consistent
5. **Step 5**: Ensure it matches Requirements.md specification

## Verification
- Test with short message: "Proceed? [Y/n]:"
- Test with long message: "Selected: v1.2.0 (llama-server-wrapper-v1.2.0.zip)"
- Verify centered text alignment
- Confirm border is properly rendered
- Test all input keys (Enter, y, n, Esc)

## Expected Outcome
After fixing, the confirmation dialog should look like:
```
┌─────────────────────────────────────────────────────┐
│ Selected: v1.2.0 (llama-server-wrapper-v1.2.0.zip) │
│ Proceed? [Y/n]:                                     │
└─────────────────────────────────────────────────────┘
```

## Files to Modify
- `ui_manager.py`: Rewrite `render_confirmation()` method (lines 1048-1218)

## Dependencies
- None (uses existing UIManager infrastructure)

## Timeline
- Estimated time: 30 minutes
- Priority: High (blocks proper UI for confirmations)