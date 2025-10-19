# Personnel Management - UI Preview

## Navigation Structure

```
Dashboard (Sidebar)
└── Personnel Management ← NEW!
    ├── Employees Tab
    ├── Departments Tab
    └── Positions Tab
```

## UI Components Overview

### 1. Personnel Management Main Page (`/personnel`)

**Header:**
- Title: "Personnel Management" with employee icon
- Subtitle: "Manage employees, departments, and positions"

**Tabs:**
- Three horizontal tabs: Employees | Departments | Positions
- Active tab highlighted with primary color (ISG blue)
- Icons for each tab (employees, building, tag)

### 2. Employees Tab

**Features:**
- Search bar with icon (search by name, email, department, position)
- "Add Employee" button (Admin only, primary color)
- Filter buttons (Filter by Department, More Filters)

**Table Columns:**
1. Employee (with photo thumbnail, name, email)
2. Department (with building icon)
3. Position (as badge)
4. Status (active/inactive badge)
5. Last Activity (with clock icon)
6. Actions (View, Edit, Delete icons)

**Photo Display:**
- 40x40px rounded avatar
- Fallback to placeholder if image fails
- Uses `photo_front_path` from backend

**Modal for Add/Edit:**
- Form fields: First Name, Last Name, Email, Phone
- Department and Position dropdowns
- Hire Date picker
- Emergency Contact fields
- Notes textarea
- Three photo upload slots (Front, Left, Right) with previews
- Save and Cancel buttons

### 3. Departments Tab

**Features:**
- Search bar (search by name or description)
- "Add Department" button (Admin only)

**Table Columns:**
1. Department (with building icon, name in bold)
2. Description
3. Employees (count as primary badge)
4. Positions (count as secondary badge)
5. Status (Active/Inactive badge)
6. Actions (Edit, Delete icons)

**Modal for Add/Edit:**
- Department Name (required)
- Description (optional textarea)
- Active checkbox
- Save and Cancel buttons

**Delete Behavior:**
- If department has employees: Soft delete (marks as inactive)
- If department has no employees: Hard delete
- Confirmation dialog shows employee count warning

### 4. Positions Tab

**Features:**
- Search bar (search by name, description, or department)
- "Add Position" button (Admin only)

**Table Columns:**
1. Position (with tag icon, name in bold)
2. Department (name or "No department")
3. Description
4. Employees (count as primary badge)
5. Status (Active/Inactive badge)
6. Actions (Edit, Delete icons)

**Modal for Add/Edit:**
- Position Name (required)
- Department (dropdown, optional)
- Description (optional textarea)
- Active checkbox
- Save and Cancel buttons

**Delete Behavior:**
- If position has employees: Soft delete (marks as inactive)
- If position has no employees: Hard delete
- Confirmation dialog shows employee count warning

## Design System (ISG Theme)

### Colors:
- **Primary**: Blue (#3B82F6 / primary-600)
- **Success**: Green (for active status)
- **Danger**: Red (for inactive/delete)
- **Neutral**: Gray shades for text and backgrounds

### Components:
- **Cards**: White background, subtle shadow, rounded corners
- **Buttons**: 
  - Primary: Blue background, white text
  - Secondary: Gray background, dark text
  - Icon buttons: Transparent with hover effects
- **Badges**:
  - Primary: Blue background (for counts)
  - Secondary: Light gray (for counts)
  - Success: Green (for active)
  - Danger: Red (for inactive)
- **Table**: 
  - Striped rows
  - Hover effects
  - Responsive design

### Icons Used:
- `employees`: User group icon
- `building`: Building/department icon
- `tag`: Tag/label icon
- `search`: Magnifying glass
- `add`: Plus sign
- `edit`: Pencil
- `delete`: Trash bin
- `close`: X mark
- `check`: Checkmark
- `clock`: Clock/time
- `dashboard`: Dashboard grid
- `cameras`: Camera icon
- `violations`: Warning triangle
- `settings`: Gear/cog

## Responsive Design

- **Desktop**: Full table view with all columns
- **Tablet**: Optimized column widths, horizontal scroll if needed
- **Mobile**: Stacked cards instead of table (responsive Table component)

## Accessibility Features

- Semantic HTML elements
- ARIA labels for icon buttons
- Keyboard navigation support
- Focus indicators
- Color contrast compliance
- Screen reader friendly

## State Management

**Loading States:**
- Skeleton table with animated placeholders
- Loading spinners for async operations

**Error States:**
- Red error card with icon and message
- Retry options where applicable

**Empty States:**
- Friendly messages like "No departments found. Add your first department to get started."
- Search-specific empty states

**Success Feedback:**
- Immediate UI update on successful operations
- Modal closes automatically
- Updated counts and relationships

## User Permissions

**Admin Role:**
- Full CRUD access (Create, Read, Update, Delete)
- All buttons and actions visible

**Other Roles:**
- Read-only access
- No Add/Edit/Delete buttons shown
- View details only
