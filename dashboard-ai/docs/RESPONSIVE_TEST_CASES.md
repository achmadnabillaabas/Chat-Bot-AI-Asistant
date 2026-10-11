# Responsive Test Cases

## Manual Testing Checklist

### Desktop (≥ 1280px)

#### Initial State
- [ ] Sidebar is visible (256px width)
- [ ] Header starts at x=256px
- [ ] Main content has left padding
- [ ] All navigation labels visible
- [ ] "AI Assistant" title + subtitle visible
- [ ] "New Chat" button shows icon + text
- [ ] Connection status visible in sidebar footer
- [ ] Connection status visible in header
- [ ] No horizontal scroll

#### Collapse Sidebar
- [ ] Click hamburger in header
- [ ] Sidebar slides left off-screen
- [ ] Header moves to left edge (x=0)
- [ ] Main content expands (padding-left removed)
- [ ] Smooth 300ms transition
- [ ] No layout shift or jank

#### Expand Sidebar
- [ ] Click hamburger again
- [ ] Sidebar slides in from left
- [ ] Header moves right (x=256px)
- [ ] Main content compresses (padding-left added)
- [ ] Smooth 300ms transition

---

### Tablet (768px - 1023px)

#### Initial State
- [ ] Sidebar visible by default
- [ ] Header positioned correctly
- [ ] Main content readable
- [ ] All navigation text visible
- [ ] Buttons usable
- [ ] No text clipping

#### Collapse/Expand
- [ ] Hamburger functions correctly
- [ ] Sidebar collapse works smoothly
- [ ] Content reflows properly
- [ ] No overlapping elements

---

### Mobile (< 768px)

#### Initial State - Drawer Closed
- [ ] Sidebar is hidden (off-screen left)
- [ ] No visible sidebar
- [ ] Hamburger visible in top-left of header
- [ ] Header spans full width
- [ ] Main content uses full width
- [ ] "9Router Active" badge hidden
- [ ] User avatar visible
- [ ] No horizontal scroll
- [ ] No overflow issues

#### Open Drawer
- [ ] Click hamburger button
- [ ] Sidebar slides in from left
- [ ] Sidebar shows at full 256px width (not compressed)
- [ ] Dark overlay appears over main content
- [ ] "AI Assistant" title fully visible (not clipped)
- [ ] "Enterprise Workspace" subtitle visible
- [ ] Close (X) button visible in sidebar header
- [ ] "New Chat" button full width with icon + text
- [ ] "Quick Search" button full width
- [ ] All navigation labels readable
- [ ] Icons aligned properly
- [ ] Footer connection status visible
- [ ] Drawer has proper z-index (above content)
- [ ] Main content still visible behind overlay

#### Close Drawer
**Method 1: Overlay Click**
- [ ] Click dark overlay
- [ ] Drawer slides out to left
- [ ] Overlay fades out
- [ ] Returns to initial state

**Method 2: X Button**
- [ ] Click X button in sidebar header
- [ ] Drawer slides out to left
- [ ] Overlay fades out
- [ ] Returns to initial state

#### Drawer Interactions
- [ ] Can scroll sidebar if content is long
- [ ] Can click navigation items
- [ ] Hover states work on nav items
- [ ] Active nav item highlighted
- [ ] Search button shows keyboard shortcut
- [ ] All text truncates properly (no overflow)

---

### Mobile - Narrow (360px - 390px)

#### Critical Checks
- [ ] No elements off-screen
- [ ] No horizontal scroll
- [ ] Hamburger button accessible (min 44×44px)
- [ ] User avatar visible
- [ ] Drawer opens properly
- [ ] "New Chat" button doesn't become thin vertical bar
- [ ] Text remains readable (not too small)
- [ ] Touch targets adequate (≥ 44px)

#### Typography Check
- [ ] "AI Assistant" doesn't wrap weird
- [ ] "Enterprise Workspace" on second line or truncated
- [ ] Navigation labels single line
- [ ] "Quick Search" readable
- [ ] Connection status text truncates if needed

---

### Resize Testing

#### Desktop → Mobile
1. Start at 1440px
2. Slowly resize to 360px
3. Watch for breakpoints:
   - [ ] At 768px: sidebar becomes drawer
   - [ ] At 768px: header connection badge disappears
   - [ ] At 640px: empty state grid becomes single column
4. [ ] No layout breaks
5. [ ] No text overflow
6. [ ] No horizontal scroll appears

#### Mobile → Desktop
1. Start at 360px
2. Slowly resize to 1440px
3. Watch for breakpoints:
   - [ ] At 768px: drawer becomes fixed sidebar
   - [ ] At 768px: header connection badge appears
   - [ ] At 640px: empty state grid becomes two columns
4. [ ] Sidebar appears smoothly
5. [ ] Header repositions correctly
6. [ ] Content padding adjusts

---

### Device Simulation

#### iPhone SE (375px × 667px)
- [ ] Hamburger accessible
- [ ] Drawer opens properly
- [ ] All content readable
- [ ] No overflow

#### iPhone 12/13 (390px × 844px)
- [ ] Proper layout
- [ ] Touch targets adequate
- [ ] Drawer full functionality

#### iPad Mini (768px × 1024px)
- [ ] Sidebar behavior correct
- [ ] Layout comfortable
- [ ] Typography appropriate

#### iPad Pro (1024px × 1366px)
- [ ] Desktop-like experience
- [ ] Sidebar collapse works
- [ ] Content well-spaced

---

### Interaction Testing

#### Sidebar Navigation
- [ ] Click "Chat" - navigates correctly
- [ ] Click "Knowledge Base" - navigates
- [ ] Click "Token Usage" - navigates
- [ ] Click "Models & 9Router" - navigates
- [ ] Click "Telegram Bot" - navigates
- [ ] Click "Settings" - navigates
- [ ] Active state updates on current page

#### Hover States (Desktop)
- [ ] Nav items change background on hover
- [ ] Buttons show hover effect
- [ ] Icons remain aligned
- [ ] Transitions smooth (not jarring)

#### Focus States (Keyboard Navigation)
- [ ] Tab through interface
- [ ] Focus ring visible on buttons
- [ ] Focus ring color correct (primary blue)
- [ ] Can navigate entire sidebar
- [ ] Can reach all interactive elements

---

### Accessibility Testing

#### Screen Reader
- [ ] Sidebar has proper ARIA labels
- [ ] Hamburger button has descriptive label
- [ ] Nav items readable
- [ ] Current page announced

#### Keyboard Only
- [ ] Can open/close sidebar with keyboard
- [ ] Tab order logical
- [ ] Can navigate without mouse
- [ ] Focus trap in drawer (mobile) if needed

#### Touch Targets
- [ ] All buttons ≥ 44×44px
- [ ] Adequate spacing between targets
- [ ] No accidental taps

---

### Performance

#### Animation Smoothness
- [ ] Sidebar transitions at 60fps
- [ ] No jank or stuttering
- [ ] Overlay fade smooth
- [ ] Drawer slide smooth

#### Load Time
- [ ] Fonts load without flash
- [ ] Layout stable (no CLS)
- [ ] Interactive quickly

---

### Browser Testing

#### Chrome
- [ ] All features work
- [ ] Responsive correct

#### Firefox
- [ ] All features work
- [ ] Responsive correct

#### Safari (macOS)
- [ ] All features work
- [ ] Responsive correct
- [ ] Backdrop-blur works

#### Safari (iOS)
- [ ] Touch interactions work
- [ ] Drawer slides properly
- [ ] No Safari-specific bugs

#### Edge
- [ ] All features work
- [ ] Responsive correct

---

### Edge Cases

#### Very Narrow (< 360px)
- [ ] Layout degrades gracefully
- [ ] Still functional
- [ ] No critical breaks

#### Very Wide (> 1920px)
- [ ] Max-width constraints work
- [ ] Content centered
- [ ] Not stretched awkwardly

#### Portrait Mobile
- [ ] Vertical space managed
- [ ] Drawer height correct
- [ ] Scrolling works

#### Landscape Mobile
- [ ] Horizontal space used well
- [ ] Not cramped
- [ ] Drawer doesn't cover everything

---

## Automated Testing Commands

```bash
# Run TypeScript check
npm run type-check

# Run linter
npm run lint

# Build production
npm run build

# Start production server
npm start
```

---

## Common Issues to Watch For

### ❌ Bad
- Hamburger overlaps with title
- Sidebar compresses into thin column on mobile
- "New Chat" becomes vertical text
- Horizontal scroll appears
- Text gets clipped
- Buttons too small to tap
- Layout jumps on resize

### ✅ Good
- Clean drawer behavior
- Full-width sidebar on mobile
- Readable text at all sizes
- Smooth transitions
- No layout shifts
- Adequate touch targets
- Responsive without breaking

---

## Sign-off Criteria

Before declaring responsive implementation complete:

- [ ] All viewport sizes tested (360px - 1920px+)
- [ ] No horizontal scroll at any width
- [ ] Drawer works on mobile
- [ ] Sidebar collapse works on desktop
- [ ] All text readable
- [ ] All buttons usable
- [ ] Touch targets adequate
- [ ] Animations smooth
- [ ] No visual bugs
- [ ] Matches design reference screenshots
- [ ] Accessibility basics covered
- [ ] Multiple browsers tested
- [ ] Mobile devices tested (physical or simulator)
