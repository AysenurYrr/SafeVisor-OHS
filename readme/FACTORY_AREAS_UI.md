# Factory Areas Feature - Visual Guide

## User Interface Components

### 1. Navigation Menu
The Factory Areas feature is accessible from the main sidebar navigation:

```
┌─────────────────────────────────────┐
│ SafeVisor                           │
├─────────────────────────────────────┤
│ Main                                │
│  📊 Dashboard                       │
│  👥 Employees                       │
│  📹 Cameras                         │
│  🏢 Factory Areas          ← NEW!  │
│                                     │
│ Safety Events                       │
│  ⚠️  PPE Violations                 │
│  🕐 Pose Alerts                     │
│                                     │
│ Administration                      │
│  ⚙️  User Management                │
└─────────────────────────────────────┘
```

### 2. Factory Areas List Page

When you navigate to `/factory-areas`, you see:

```
┌──────────────────────────────────────────────────────────────────────┐
│ Factory Areas                           [+ Add Factory Area] Button   │
│ Manage factory areas with cameras and safety rules                   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│ 🔍 [Search areas...]                                                 │
│                                                                       │
├──────────────────────────────────────────────────────────────────────┤
│ Area Name       │ Cameras  │ Safety Rules              │ Status │ Actions │
├─────────────────┼──────────┼───────────────────────────┼────────┼─────────┤
│ Factory Area-1  │ 3 camera(s) │ helmet gloves vest +2  │ Active │ ✏️ 🗑️  │
│ Main Gate       │ 1 camera(s) │ helmet glasses         │ Active │ ✏️ 🗑️  │
│ Assembly Line   │ 2 camera(s) │ helmet vest gloves     │ Active │ ✏️ 🗑️  │
└──────────────────────────────────────────────────────────────────────┘
```

### 3. Create/Edit Factory Area Form

Click "Add Factory Area" or edit icon to see:

```
┌──────────────────────────────────────────────────────────────────────┐
│ Add New Factory Area                                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│ Area Name *                    Status                                │
│ [Factory Area-1        ]       [Active ▼]                           │
│                                                                       │
│ Description                                                           │
│ [Main production floor with assembly lines...                    ]   │
│ [                                                                 ]   │
│                                                                       │
│ Safety Rules                                                          │
│ ☑ glasses      ☑ face-mask    ☐ ear-muffs    ☐ hands    ☑ gloves  │
│ ☑ safety-vest  ☐ tools         ☑ helmet       ☐ medical-suit       │
│ ☐ safety-suit                                                        │
│                                                                       │
│ Cameras                                                               │
│ ┌───────────────────────────────────────────────────────┐           │
│ │ ☑ Camera-1                                      Active │           │
│ │   Main Gate                                            │           │
│ │ ☑ Camera-2                                      Active │           │
│ │   Production Floor                                     │           │
│ │ ☐ Camera-3                                    Inactive │           │
│ │   Warehouse Entrance                                   │           │
│ └───────────────────────────────────────────────────────┘           │
│                                                                       │
│                                    [Cancel]  [Create Area]           │
└──────────────────────────────────────────────────────────────────────┘
```

## Feature Highlights

### ✅ Key Features Implemented

1. **Full CRUD Operations**
   - ✓ Create new factory areas
   - ✓ View list of all areas
   - ✓ Edit existing areas
   - ✓ Delete areas (soft delete)
   - ✓ Search functionality

2. **Camera Management**
   - ✓ Assign multiple cameras to each area
   - ✓ View camera details (name, location, status)
   - ✓ One camera can belong to multiple areas

3. **Safety Rules**
   - ✓ 10 predefined safety rules
   - ✓ Select multiple rules per area
   - ✓ Visual checkbox interface
   - ✓ Server-side validation

4. **Access Control**
   - ✓ All users can view areas
   - ✓ Manager/Admin can create/edit
   - ✓ Admin only can delete

5. **User Experience**
   - ✓ Clean, modern UI
   - ✓ Responsive design
   - ✓ Loading states
   - ✓ Error handling
   - ✓ Confirmation dialogs

## Data Model

### Factory Area Structure

```json
{
  "id": 1,
  "name": "Factory Area-1",
  "description": "Main production floor",
  "is_active": true,
  "cameras": [
    {
      "id": 1,
      "name": "Camera-1",
      "location": "Main Gate",
      "stream_url": "rtsp://example.com/stream1",
      "is_active": true
    }
  ],
  "safety_rules": [
    "helmet",
    "safety-vest",
    "gloves"
  ],
  "created_by": 1,
  "created_at": "2025-01-07T10:00:00Z",
  "updated_at": null
}
```

## API Endpoints Summary

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | /api/v1/factory-areas/safety-rules | Get valid safety rules | All |
| GET | /api/v1/factory-areas/ | List all areas | All |
| GET | /api/v1/factory-areas/{id} | Get specific area | All |
| POST | /api/v1/factory-areas/ | Create new area | Manager/Admin |
| PUT | /api/v1/factory-areas/{id} | Update area | Manager/Admin |
| DELETE | /api/v1/factory-areas/{id} | Delete area | Admin |
| GET | /api/v1/factory-areas/active/list | Get active areas | All |

## Safety Rules Reference

Available safety equipment types:

1. **glasses** - Safety glasses/goggles
2. **face-mask** - Face masks/respirators
3. **ear-muffs** - Hearing protection
4. **hands** - Hand visibility/positioning
5. **gloves** - Safety gloves
6. **safety-vest** - High-visibility vest
7. **tools** - Proper tool usage
8. **helmet** - Hard hat/helmet
9. **medical-suit** - Medical protective suit
10. **safety-suit** - Industrial safety suit

## Workflow Example

### Creating a New Factory Area

1. **Navigate** to Factory Areas from the sidebar
2. **Click** "Add Factory Area" button
3. **Enter** area details:
   - Name: "Assembly Line A"
   - Description: "Main assembly line with robotic arms"
4. **Select** safety rules:
   - ✓ helmet
   - ✓ safety-vest
   - ✓ gloves
   - ✓ glasses
5. **Choose** cameras:
   - ✓ Camera-2 (Production Floor)
   - ✓ Camera-4 (Assembly Station)
6. **Click** "Create Area"
7. **View** the new area in the list

### Editing an Existing Area

1. **Find** the area in the list
2. **Click** the edit icon (✏️)
3. **Modify** any fields:
   - Add/remove cameras
   - Add/remove safety rules
   - Change description
4. **Click** "Update Area"
5. **Changes** are saved and reflected in the list

## Integration Points

### With Existing Features

- **Cameras**: Factory areas can be assigned multiple cameras
- **Users**: Areas track who created them (created_by)
- **Authentication**: All endpoints require valid JWT token
- **Authorization**: Role-based access control integrated

### Future Enhancements (Not in Scope)

- Associate violations with specific areas
- Area-specific detection rules
- Real-time monitoring per area
- Area-based reporting and analytics

## Technical Details

### Frontend Stack
- React 18 with Hooks
- React Router for navigation
- Tailwind CSS for styling
- Heroicons for icons
- Axios for API calls

### Backend Stack
- FastAPI with Pydantic
- SQLAlchemy ORM
- PostgreSQL database
- Alembic migrations
- JWT authentication

### Security
- JWT token required for all endpoints
- Role-based authorization
- Input validation and sanitization
- SQL injection prevention via ORM
- XSS protection

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Responsive Design

The interface is fully responsive:
- **Desktop**: Full layout with sidebar
- **Tablet**: Collapsible sidebar
- **Mobile**: Hamburger menu, stacked layout
