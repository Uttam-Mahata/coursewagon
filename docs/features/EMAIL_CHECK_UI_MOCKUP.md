# Email Check Feature - UI Mockup

## Visual States During Signup

### State 1: Initial / Empty
```
┌────────────────────────────────────────────┐
│  CourseWagon Sign Up                       │
├────────────────────────────────────────────┤
│                                            │
│  First Name                                │
│  ┌────────────────────────────────────┐   │
│  │ John                               │   │
│  └────────────────────────────────────┘   │
│                                            │
│  Last Name                                 │
│  ┌────────────────────────────────────┐   │
│  │ Doe                                │   │
│  └────────────────────────────────────┘   │
│                                            │
│  📧 Email                                  │
│  ┌────────────────────────────────────┐   │
│  │                                    │   │
│  └────────────────────────────────────┘   │
│                                            │
│  🔒 Password                               │
│  ┌────────────────────────────────────┐   │
│  │ ••••••••                           │   │
│  └────────────────────────────────────┘   │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │          Sign Up                   │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

### State 2: Checking Email
```
┌────────────────────────────────────────────┐
│  CourseWagon Sign Up                       │
├────────────────────────────────────────────┤
│                                            │
│  First Name                                │
│  ┌────────────────────────────────────┐   │
│  │ John                               │   │
│  └────────────────────────────────────┘   │
│                                            │
│  Last Name                                 │
│  ┌────────────────────────────────────┐   │
│  │ Doe                                │   │
│  └────────────────────────────────────┘   │
│                                            │
│  📧 Email                                  │
│  ┌────────────────────────────────────┐   │
│  │ john.doe@example.com           ⟳  │   │ ← Spinner
│  └────────────────────────────────────┘   │
│  ℹ️ Checking email availability...         │
│                                            │
│  🔒 Password                               │
│  ┌────────────────────────────────────┐   │
│  │                                    │   │
│  └────────────────────────────────────┘   │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │          Sign Up                   │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

### State 3: Email Available (Success)
```
┌────────────────────────────────────────────┐
│  CourseWagon Sign Up                       │
├────────────────────────────────────────────┤
│                                            │
│  First Name                                │
│  ┌────────────────────────────────────┐   │
│  │ John                               │   │
│  └────────────────────────────────────┘   │
│                                            │
│  Last Name                                 │
│  ┌────────────────────────────────────┐   │
│  │ Doe                                │   │
│  └────────────────────────────────────┘   │
│                                            │
│  📧 Email                                  │
│  ┌────────────────────────────────────┐   │
│  │ john.doe@example.com           ✓  │   │ ← Green checkmark
│  └────────────────────────────────────┘   │
│     ▲ Green border                        │
│  ✅ Email is available!                    │
│                                            │
│  🔒 Password                               │
│  ┌────────────────────────────────────┐   │
│  │ ••••••••                           │   │
│  └────────────────────────────────────┘   │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │          Sign Up                   │   │ ← Button enabled
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

### State 4: Email Already Registered (Error)
```
┌────────────────────────────────────────────┐
│  CourseWagon Sign Up                       │
├────────────────────────────────────────────┤
│                                            │
│  First Name                                │
│  ┌────────────────────────────────────┐   │
│  │ John                               │   │
│  └────────────────────────────────────┘   │
│                                            │
│  Last Name                                 │
│  ┌────────────────────────────────────┐   │
│  │ Doe                                │   │
│  └────────────────────────────────────┘   │
│                                            │
│  📧 Email                                  │
│  ┌────────────────────────────────────┐   │
│  │ existing@example.com           ⚠  │   │ ← Red warning icon
│  └────────────────────────────────────┘   │
│     ▲ Red border                          │
│  ⚠️ This email is already registered.     │
│     Please use a different email or       │
│     [login instead].                      │
│         ▲ Clickable link                  │
│                                            │
│  🔒 Password                               │
│  ┌────────────────────────────────────┐   │
│  │                                    │   │
│  └────────────────────────────────────┘   │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │          Sign Up                   │   │ ← Button disabled
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

## Color Scheme

### Border Colors
- **Default/Checking**: `border-gray-300` (#D1D5DB)
- **Available**: `border-green-500` (#10B981)
- **Taken**: `border-red-500` (#EF4444)

### Focus Ring Colors
- **Default**: `ring-blue-400` (#60A5FA)
- **Available**: `ring-green-400` (#34D399)
- **Taken**: `ring-red-400` (#F87171)

### Icon Colors
- **Spinner**: `text-gray-400` (#9CA3AF)
- **Success**: `text-green-500` (#10B981)
- **Error**: `text-red-500` (#EF4444)

### Message Colors
- **Info**: `text-gray-500` (#6B7280)
- **Success**: `text-green-600` (#059669)
- **Error**: `text-red-600` (#DC2626)

## Interaction Flow

```
User Types Email
       ↓
   Debounce 500ms
       ↓
    Show Spinner
       ↓
  Call API: /auth/check-email
       ↓
   Get Response
       ↓
    ┌─────┴─────┐
    ↓           ↓
Available    Taken
    ↓           ↓
Show ✓      Show ⚠
Green       Red
Enable      Disable
Submit      Submit
```

## Responsive Behavior

### Desktop (≥768px)
- Full width form with side padding
- Icons clearly visible
- Messages display inline

### Mobile (<768px)
- Full width form
- Slightly smaller icons
- Messages stack below input
- Touch-friendly click targets

## Accessibility Features

1. **ARIA Labels**
   - `aria-label="Email availability status"`
   - `aria-live="polite"` for status messages

2. **Screen Reader Announcements**
   - "Checking email availability"
   - "Email is available"
   - "Email is already registered"

3. **Keyboard Navigation**
   - Tab to email field
   - Type email
   - Status updates announced
   - Tab to next field or login link

4. **Color Independence**
   - Icons complement colors
   - Text messages provide context
   - Not relying solely on color

## Animation Timing

- **Debounce**: 500ms
- **Spinner**: Continuous rotation
- **Border Transition**: 300ms ease
- **Message Fade In**: 200ms ease
- **Icon Appearance**: 150ms ease

## Example HTML Structure

```html
<div class="email-field">
  <label for="email">Email</label>
  <div class="input-wrapper">
    <input 
      type="email"
      id="email"
      [ngClass]="{
        'border-green-500': available,
        'border-red-500': taken
      }"
    />
    <span class="icon">
      <!-- Spinner or Icon -->
    </span>
  </div>
  <p class="message" *ngIf="status">
    {{ statusMessage }}
  </p>
</div>
```

## User Flow Example

1. **User arrives at signup page**
   - Sees empty form with gray borders

2. **User fills first name and last name**
   - Fields turn green when valid

3. **User clicks email field**
   - Field gains focus with blue ring

4. **User types "john"**
   - No action yet (debouncing)

5. **User continues typing "john.doe@example.com"**
   - Still debouncing

6. **User pauses typing (500ms passes)**
   - Spinner appears
   - "Checking..." message shows

7. **API responds (email available)**
   - Spinner disappears
   - Green checkmark appears
   - Border turns green
   - "Email is available!" message shows

8. **User moves to password field**
   - Can now complete signup

**Alternative Flow (Email Taken)**:

7. **API responds (email taken)**
   - Spinner disappears
   - Red warning icon appears
   - Border turns red
   - Error message with login link shows
   - Submit button becomes disabled

8. **User clicks "login instead"**
   - Form switches to login mode
   - Email field pre-filled

## Performance Metrics

- **Time to First Check**: ~500ms after typing stops
- **API Response Time**: <200ms (target)
- **Total User Wait**: <700ms
- **Perceived Performance**: Instant (due to visual feedback)

## Error States

### Network Error
- Fail open (allow signup)
- No visual error to user
- Logged in console
- User can proceed normally

### Invalid Email Format
- Caught by standard validators
- Shows before async check
- Red border with format error
- No API call made

### API Timeout
- 10 second timeout
- Fail open after timeout
- User can proceed
- Logged for monitoring
