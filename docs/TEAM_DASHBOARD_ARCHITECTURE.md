# Team Dashboard Architecture

## Overview

The Team Dashboard transforms LLM Session Manager from an individual CLI tool into a collaborative team platform with real-time visibility, shared insights, and team analytics.

## Architecture Design

### Tech Stack

**Backend:**
- **FastAPI** - Modern, fast Python web framework with async support
- **WebSockets** - Real-time updates for live dashboard
- **SQLAlchemy** - Already in use, extend for team features
- **JWT** - Authentication tokens
- **Uvicorn** - ASGI server

**Frontend:**
- **React** - Component-based UI (or Vue.js alternative)
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS
- **Chart.js / Recharts** - Data visualization
- **SWR / React Query** - Data fetching
- **WebSocket** - Real-time updates

**Deployment:**
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy (optional)

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Web Browser                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Dashboard  │  │  Analytics  │  │   Settings  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                    HTTP/WebSocket
                          │
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  REST API   │  │  WebSocket  │  │    Auth     │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                          │
┌─────────────────────────────────────────────────────────┐
│              Existing Core Components                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Database │  │  Memory  │  │  Health  │             │
│  │ (SQLite) │  │ Manager  │  │ Monitor  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                          │
                          │
┌─────────────────────────────────────────────────────────┐
│                CLI Session Agents                        │
│  (Running on developer machines)                         │
│  - Discover sessions                                     │
│  - Report metrics to API                                 │
│  - Receive commands from dashboard                       │
└─────────────────────────────────────────────────────────┘
```

## Data Model Extensions

### New Tables

#### `teams`
```sql
CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    settings JSON  -- Team-wide settings
);
```

#### `users`
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    team_id TEXT,
    role TEXT,  -- 'admin', 'member', 'viewer'
    created_at TIMESTAMP,
    last_login TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams (id)
);
```

#### `session_owners`
```sql
CREATE TABLE session_owners (
    session_id TEXT,
    user_id TEXT,
    PRIMARY KEY (session_id, user_id),
    FOREIGN KEY (session_id) REFERENCES sessions (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

#### `team_metrics`
```sql
CREATE TABLE team_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id TEXT,
    metric_type TEXT,  -- 'token_usage', 'session_count', etc.
    value REAL,
    timestamp TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (team_id) REFERENCES teams (id)
);
```

#### `shared_insights`
```sql
CREATE TABLE shared_insights (
    id TEXT PRIMARY KEY,
    team_id TEXT,
    session_id TEXT,
    insight_type TEXT,  -- 'learning', 'pattern', 'recommendation'
    content TEXT,
    shared_by TEXT,
    created_at TIMESTAMP,
    upvotes INTEGER DEFAULT 0,
    FOREIGN KEY (team_id) REFERENCES teams (id),
    FOREIGN KEY (session_id) REFERENCES sessions (id),
    FOREIGN KEY (shared_by) REFERENCES users (id)
);
```

### Extended Tables

#### `sessions` (add columns)
```sql
ALTER TABLE sessions ADD COLUMN team_id TEXT;
ALTER TABLE sessions ADD COLUMN visibility TEXT DEFAULT 'private';  -- 'private', 'team', 'public'
ALTER TABLE sessions ADD COLUMN shared_at TIMESTAMP;
```

## API Endpoints

### Authentication

```
POST   /api/auth/register          - Register new user
POST   /api/auth/login             - Login (returns JWT)
POST   /api/auth/logout            - Logout
GET    /api/auth/me                - Get current user
PUT    /api/auth/me                - Update current user
```

### Teams

```
GET    /api/teams                  - List teams
POST   /api/teams                  - Create team
GET    /api/teams/:id              - Get team details
PUT    /api/teams/:id              - Update team
DELETE /api/teams/:id              - Delete team
GET    /api/teams/:id/members      - List team members
POST   /api/teams/:id/members      - Add member
DELETE /api/teams/:id/members/:uid - Remove member
```

### Sessions

```
GET    /api/sessions               - List all sessions (filtered by user/team)
GET    /api/sessions/:id           - Get session details
PUT    /api/sessions/:id           - Update session
DELETE /api/sessions/:id           - Delete session
POST   /api/sessions/:id/share     - Share session with team
GET    /api/sessions/:id/health    - Get health metrics
GET    /api/sessions/:id/history   - Get session history
```

### Analytics

```
GET    /api/analytics/team         - Team-wide analytics
GET    /api/analytics/user/:id     - User-specific analytics
GET    /api/analytics/sessions     - Session-level analytics
GET    /api/analytics/trends       - Time-series trends
GET    /api/analytics/export       - Export analytics data
```

### Insights

```
GET    /api/insights               - List shared insights
POST   /api/insights               - Create insight
GET    /api/insights/:id           - Get insight details
PUT    /api/insights/:id           - Update insight
DELETE /api/insights/:id           - Delete insight
POST   /api/insights/:id/upvote    - Upvote insight
```

### Real-time (WebSocket)

```
WS     /ws/sessions                - Real-time session updates
WS     /ws/team                    - Team activity stream
WS     /ws/notifications           - User notifications
```

## Frontend Pages

### 1. Dashboard (/)
**Purpose:** Real-time overview of all team sessions

**Features:**
- Live session grid/list
- Active/idle/error status indicators
- Token usage bars
- Health score colors
- Quick filters (by user, tag, status)
- Real-time updates via WebSocket

**Components:**
- `SessionCard` - Individual session display
- `SessionList` - Grid/list view
- `FilterBar` - Quick filters
- `StatusBadge` - Status indicators
- `LiveIndicator` - Real-time pulse

### 2. Analytics (/analytics)
**Purpose:** Team-wide insights and trends

**Features:**
- Token usage over time (line chart)
- Session distribution (pie chart)
- Health score trends (area chart)
- Top users by activity (bar chart)
- Tag cloud
- Export reports

**Components:**
- `TokenUsageChart` - Line chart
- `SessionDistribution` - Pie/donut chart
- `HealthTrends` - Area chart
- `UserActivityChart` - Bar chart
- `MetricCard` - KPI display
- `DateRangePicker` - Filter by date

### 3. Session Details (/sessions/:id)
**Purpose:** Deep dive into individual session

**Features:**
- Full session metadata
- Health breakdown
- Token usage graph
- Activity timeline
- Memories from session
- Git commits (if available)
- File changes

**Components:**
- `SessionHeader` - Title, status, actions
- `HealthBreakdown` - Pie chart of health factors
- `ActivityTimeline` - Event timeline
- `MemoryList` - Session memories
- `GitCommitList` - Git integration
- `FileChangeList` - Modified files

### 4. Team Settings (/settings)
**Purpose:** Configure team and users

**Features:**
- Team profile
- Member management (add/remove)
- Role assignments
- Token limits
- Health thresholds
- Notification preferences

**Components:**
- `TeamProfile` - Edit team info
- `MemberList` - Manage members
- `RoleSelector` - Assign roles
- `SettingsForm` - Configuration
- `InviteForm` - Invite new members

### 5. Shared Insights (/insights)
**Purpose:** Team knowledge sharing

**Features:**
- Feed of shared learnings
- Upvote/comment
- Filter by tag/user
- Create new insight
- Link to sessions

**Components:**
- `InsightFeed` - List of insights
- `InsightCard` - Individual insight
- `CreateInsightForm` - New insight
- `UpvoteButton` - Vote on insights
- `CommentThread` - Discussions

## Real-time Features

### WebSocket Events

**Client → Server:**
```json
{
  "type": "subscribe",
  "channel": "team:abc123",
  "filters": {
    "status": ["active", "error"],
    "users": ["user-1", "user-2"]
  }
}
```

**Server → Client:**
```json
{
  "type": "session_update",
  "data": {
    "session_id": "xyz789",
    "health_score": 75.0,
    "token_count": 150000,
    "status": "active"
  }
}
```

### Update Types

- `session_update` - Session metrics changed
- `session_created` - New session discovered
- `session_ended` - Session closed
- `health_alert` - Health drops below threshold
- `token_warning` - Token usage > 90%
- `insight_shared` - New insight posted
- `member_joined` - Team member added

## Security

### Authentication Flow

1. User submits email/password
2. Backend validates credentials
3. JWT token generated with claims:
   ```json
   {
     "user_id": "abc123",
     "team_id": "team-xyz",
     "role": "member",
     "exp": 1234567890
   }
   ```
4. Token sent to client
5. Client includes token in `Authorization: Bearer <token>` header

### Authorization

**Roles:**
- **Admin** - Full access, can manage team settings
- **Member** - View all team sessions, edit own sessions, share insights
- **Viewer** - Read-only access to team dashboard

**Permission Matrix:**

| Action | Admin | Member | Viewer |
|--------|-------|--------|--------|
| View team sessions | ✅ | ✅ | ✅ |
| View team analytics | ✅ | ✅ | ✅ |
| Edit own sessions | ✅ | ✅ | ❌ |
| Edit others' sessions | ✅ | ❌ | ❌ |
| Share insights | ✅ | ✅ | ❌ |
| Manage members | ✅ | ❌ | ❌ |
| Change settings | ✅ | ❌ | ❌ |

### Data Isolation

- Users can only access sessions from their team
- Private sessions not shared unless explicitly shared
- API enforces team_id filtering on all queries
- WebSocket channels scoped to team

## Deployment Architecture

### Development

```yaml
# docker-compose.dev.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=sqlite:///data/sessions.db
      - JWT_SECRET=dev-secret
    command: uvicorn main:app --reload --host 0.0.0.0

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev
```

### Production

```yaml
# docker-compose.prod.yml
services:
  backend:
    image: ghcr.io/iamgagan/llm-session-manager-api:latest
    environment:
      - DATABASE_URL=postgresql://...
      - JWT_SECRET=${JWT_SECRET}
      - CORS_ORIGINS=${FRONTEND_URL}
    restart: unless-stopped

  frontend:
    image: ghcr.io/iamgagan/llm-session-manager-web:latest
    environment:
      - VITE_API_URL=https://api.example.com
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
```

## Implementation Phases

### Week 1: Backend Foundation
- [x] Set up FastAPI project structure
- [ ] Create extended database schema
- [ ] Implement authentication (JWT)
- [ ] Build REST API endpoints (sessions, users, teams)
- [ ] Add WebSocket support
- [ ] Write API tests

### Week 2: Frontend Core
- [ ] Set up React + Vite project
- [ ] Create component library (cards, charts, forms)
- [ ] Build Dashboard page (session list)
- [ ] Implement authentication flow
- [ ] Add WebSocket client
- [ ] Create session details page

### Week 3: Analytics & Polish
- [ ] Build Analytics page (charts, trends)
- [ ] Create Shared Insights page
- [ ] Add Team Settings page
- [ ] Implement export/reporting
- [ ] Write documentation
- [ ] Create deployment guide
- [ ] Performance optimization

## Key Metrics to Track

### Team Metrics
- Total sessions across team
- Total token usage
- Average health score
- Active sessions count
- Sessions per developer
- Token efficiency (output/tokens)

### Individual Metrics
- Sessions created
- Token usage
- Average session duration
- Health score distribution
- Most used tags
- Insights shared

### Trends
- Token usage over time
- Session count over time
- Health score trends
- Peak activity hours
- Common error patterns

## Integration with CLI

### Agent Mode

CLI can run in "agent mode" to report to dashboard:

```bash
# Start agent that reports to dashboard
python -m llm_session_manager.cli agent \
  --dashboard-url https://dashboard.example.com \
  --token <api-token>
```

**Agent responsibilities:**
- Discover local sessions
- Report metrics to API every 60s
- Listen for commands from dashboard
- Execute actions (close session, export, etc.)

### API Communication

```python
# Agent pseudo-code
while True:
    sessions = discover_sessions()

    for session in sessions:
        metrics = calculate_metrics(session)
        api.post("/api/sessions/sync", {
            "session_id": session.id,
            "metrics": metrics,
            "hostname": socket.gethostname(),
            "user_id": current_user_id
        })

    sleep(60)
```

## Future Enhancements

### Phase 2 Features
- **Slack/Teams integration** - Notifications in team chat
- **GitHub integration** - Link sessions to PRs
- **VSCode extension** - Dashboard in IDE
- **Mobile app** - iOS/Android dashboard
- **AI insights** - Automated pattern detection
- **Session collaboration** - Multiple devs in one session
- **Video recordings** - Screen recording of sessions
- **Cost tracking** - Map to API costs

### Advanced Analytics
- Predictive token usage
- Anomaly detection
- Recommendation engine improvements
- A/B testing framework
- Custom dashboards

## Technical Considerations

### Performance
- **Caching**: Redis for session data (optional)
- **Pagination**: Limit 50 sessions per page
- **Debouncing**: WebSocket updates max 1/sec
- **Lazy loading**: Charts load on demand

### Scalability
- **Horizontal scaling**: Stateless API servers
- **Database**: Migrate to PostgreSQL for > 1000 sessions
- **CDN**: Static assets on CDN
- **WebSocket**: Separate WS server if needed

### Monitoring
- **APM**: Application performance monitoring
- **Logging**: Structured logs (JSON)
- **Metrics**: Prometheus/Grafana
- **Alerts**: Health alerts, error tracking

## Success Metrics

### Adoption
- 80%+ team members using dashboard weekly
- 50%+ sessions shared with team
- 100+ insights created in first month

### Performance
- < 2s page load time
- < 100ms API response time
- 99.9% uptime

### Value
- 30% reduction in context switching
- 50% faster knowledge discovery
- 20% improvement in token efficiency

---

**Next Steps:** Begin implementation with Week 1 backend foundation.
