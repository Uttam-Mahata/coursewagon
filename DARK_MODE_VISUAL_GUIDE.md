# Dark Mode Visual Guide

## Overview
This document describes the visual appearance of the dark mode implementation across all components in the CourseWagon Angular application.

## Color System

### Light Mode
- **Primary Background**: White (#FFFFFF)
- **Secondary Background**: Gray-50 (#F9FAFB)
- **Card Background**: White with subtle shadows
- **Primary Text**: Gray-800 (#1F2937)
- **Secondary Text**: Gray-600 (#4B5563)
- **Borders**: Gray-200 (#E5E7EB), Gray-300 (#D1D5DB)
- **Accent Colors**: Blue-600 (#2563EB), Purple-600 (#9333EA)

### Dark Mode
- **Primary Background**: Slate-900 (#0F172A)
- **Secondary Background**: Slate-800 (#1E293B)
- **Card Background**: Slate-800 with darker shadows
- **Primary Text**: White (#FFFFFF)
- **Secondary Text**: Gray-300 (#D1D5DB)
- **Borders**: Slate-700 (#334155), Slate-600 (#475569)
- **Accent Colors**: Blue-400 (#60A5FA), Purple-400 (#C084FC)

## Component Visuals

### 1. Navigation Bar
**Light Mode:**
- White background with subtle shadow
- Blue gradient logo text
- Gray text links with blue hover
- White moon icon button

**Dark Mode:**
- Slate-900 background with darker shadow
- Blue-purple gradient logo (lighter tones)
- Gray-300 text links with blue-400 hover
- Yellow/white sun icon button
- Smooth backdrop blur effect maintained

### 2. Theme Toggle Button
**Appearance:**
- Circular button with icon
- Moon icon (🌙) in light mode
- Sun icon (☀️) in dark mode
- Hover effect: background color change
- Located in top-right navbar (desktop)
- Separate mobile version in mobile menu

### 3. Authentication Pages (Login/Signup)
**Light Mode:**
- White card on blue-gradient background
- Gray labels and placeholders
- White input fields with gray borders
- Blue submit buttons
- Green/red alert messages with light backgrounds

**Dark Mode:**
- Slate-800 card on dark gradient background
- Gray-300 labels, gray-500 placeholders
- Slate-700 input fields with slate-600 borders
- Blue-500 submit buttons with blue-600 hover
- Alert messages: red-900/20 and green-900/20 backgrounds
- White text maintains readability

### 4. Course Creation Page
**Light Mode:**
- White to blue-50 gradient background
- Blue-indigo gradient header
- White card with form inputs
- Gray-50 audio recording section
- Green "Add Subject" buttons

**Dark Mode:**
- Slate-900 to slate-800 gradient background
- Darker blue-indigo gradient header
- Slate-800 card with darker shadows
- Slate-700 audio recording section with slate-600 border
- Green-500 buttons maintain visibility

### 5. Courses List Page
**Light Mode:**
- White background
- White course cards with gray-100 borders
- Gray text on cards
- Blue gradient "Create Course" button
- Gray-200 skeleton loaders

**Dark Mode:**
- Slate-900 background
- Slate-800 course cards with slate-700 borders
- Gray-300 text on cards
- Blue-500 gradient buttons
- Slate-700 skeleton loaders
- Hover effects: cards lift with blue-700 border glow

### 6. Profile Page
**Light Mode:**
- White profile card
- Blue-gradient header bar
- Gray-50 sections
- Green success alerts, red error alerts
- White badge backgrounds

**Dark Mode:**
- Slate-800 profile card
- Darker blue-gradient header
- Slate-700 sections
- Semi-transparent alert backgrounds
- Role badges with appropriate dark colors
- Avatar placeholder with gradient remains vibrant

### 7. Testimonials Section
**Light Mode:**
- White testimonial cards
- Blue-100 avatar backgrounds
- Yellow star ratings
- Gray italic quotes

**Dark Mode:**
- Slate-800 testimonial cards with slate-700 borders
- Blue-900/30 avatar backgrounds
- Yellow-400 star ratings (slightly brighter)
- Gray-300 italic quotes
- Smooth card hover effects

### 8. Admin Dashboard
**Light Mode:**
- White background
- Gray-200 tab borders
- Blue active tab indicators
- White stats cards

**Dark Mode:**
- Slate-900 background
- Slate-700 tab borders
- Blue-400 active tab indicators
- Stats cards maintain gradient backgrounds
- Tab text: gray-400 inactive, blue-400 active

### 9. Learner Dashboard
**Light Mode:**
- Gradient stat cards (blue, orange, green, purple)
- White course cards
- Gray-50 section headers

**Dark Mode:**
- Darker gradient stat cards (maintain vibrant colors)
- Slate-800 course cards
- Slate-700 section headers with slate-600 borders
- Progress bars maintain visibility
- White text on gradient cards for contrast

### 10. Toast Notifications
**Light Mode:**
- Success: Green-50 background, green-800 text, green-500 icon
- Error: Red-50 background, red-800 text, red-500 icon
- Warning: Yellow-50 background, yellow-800 text, yellow-500 icon
- Info: Blue-50 background, blue-800 text, blue-500 icon

**Dark Mode:**
- Success: Green-900/20 background, green-300 text, green-400 icon
- Error: Red-900/20 background, red-300 text, red-400 icon
- Warning: Yellow-900/20 background, yellow-300 text, yellow-400 icon
- Info: Blue-900/20 background, blue-300 text, blue-400 icon
- Slightly darker close button hover

### 11. Footer
**Light Mode:**
- Gray-900 background
- Gray-300 text
- Indigo-500 links and icons

**Dark Mode:**
- Slate-950 background (even darker)
- Gray-400 text
- Indigo-400 links and icons
- Slightly reduced opacity for better hierarchy

### 12. Forms and Inputs
**Light Mode:**
- White backgrounds
- Gray-300 borders
- Gray-700 labels
- Blue-400 focus rings
- Gray-400 icon colors

**Dark Mode:**
- Slate-700 backgrounds
- Slate-600 borders
- Gray-300 labels
- Blue-500 focus rings
- Gray-500 icon colors
- Placeholder text: gray-500

### 13. Buttons
**Primary Buttons:**
- Light: Blue-600 → Blue-700 hover
- Dark: Blue-500 → Blue-600 hover

**Secondary Buttons:**
- Light: Gray-100 → Gray-200 hover
- Dark: Slate-700 → Slate-600 hover

**Success Buttons:**
- Light: Green-600 → Green-700 hover
- Dark: Green-500 → Green-600 hover

**Danger Buttons:**
- Light: Red-600 → Red-700 hover
- Dark: Red-500 → Red-600 hover

### 14. Loading States
**Spinners:**
- Light: Blue-600 border
- Dark: Blue-400 border

**Skeleton Loaders:**
- Light: Gray-200 backgrounds
- Dark: Slate-700 backgrounds
- Pulse animation maintained in both modes

### 15. Breadcrumbs
**Light Mode:**
- Blue-600 links
- Gray-500 separators
- Gray-700 current page

**Dark Mode:**
- Blue-400 links
- Gray-400 separators
- Gray-300 current page

## Transition Effects

All theme switches include smooth transitions:
- Background colors: 0.3s ease
- Border colors: 0.2s ease
- Text colors: 0.2s ease
- No flash of unstyled content

## Accessibility Considerations

### Contrast Ratios
All color combinations meet WCAG AA standards:
- Text on backgrounds: minimum 4.5:1 ratio
- Large text: minimum 3:1 ratio
- Interactive elements: clearly distinguishable states

### Focus Indicators
- Maintained in both themes
- Blue ring in light mode
- Brighter blue ring in dark mode
- 2px outline with 2px offset

## Responsive Behavior

Dark mode styling is consistent across all breakpoints:
- Mobile (< 640px): Full dark mode support
- Tablet (640px - 1024px): Optimized layouts maintained
- Desktop (> 1024px): Full feature set with hover effects

## Browser Compatibility

Tested appearance in:
- Chrome/Edge: Perfect support
- Firefox: Perfect support
- Safari: Perfect support with webkit prefixes
- Mobile browsers: Consistent appearance

## Animation and Motion

All animations work in both themes:
- Card hover lifts: scale(1.02) with shadow changes
- Button hovers: background color transitions
- Toast slide-in: from right edge
- Loading spinners: smooth rotation
- Skeleton pulse: gentle opacity animation

## Special Notes

1. **Gradients**: Many gradient backgrounds work well in both modes by design
2. **Images**: Profile images and course images maintain appearance
3. **Icons**: FontAwesome icons color-adjusted per theme
4. **Shadows**: Shadows are darker and more subtle in dark mode
5. **Backdrop Blur**: Maintained on navbar for frosted glass effect

## User Experience

### Theme Persistence
- User's choice saved in localStorage
- Automatically applied on page load
- No flash between theme loads
- Syncs across browser tabs

### Theme Detection
- System preference detected on first visit
- Manual toggle overrides system preference
- Preference persists across sessions

### Visual Feedback
- Instant theme switch (no delay)
- Icon changes from moon to sun
- All elements update simultaneously
- Smooth color transitions throughout

## Best Practices Followed

1. **Semantic Colors**: Colors have meaning (red = error, green = success)
2. **Consistent Spacing**: Same margins/padding in both themes
3. **Readable Text**: High contrast text in both modes
4. **Clear Hierarchy**: Visual hierarchy maintained
5. **Accessible Forms**: Labels, placeholders, and errors clearly visible
6. **Intuitive Icons**: Icon meanings clear in both themes
7. **Smooth Transitions**: Professional feel with subtle animations

## Testing Checklist

When testing dark mode, verify:
- [ ] All text is readable (no low contrast issues)
- [ ] All buttons are clearly visible and interactive
- [ ] Form inputs have visible borders
- [ ] Hover states work correctly
- [ ] Focus indicators are visible
- [ ] Loading states are clear
- [ ] Error/success messages are distinguishable
- [ ] Navigation is clear
- [ ] Cards and sections have proper separation
- [ ] Icons are appropriately colored
- [ ] Gradients remain appealing
- [ ] Transitions are smooth
- [ ] No visual glitches during theme switch
