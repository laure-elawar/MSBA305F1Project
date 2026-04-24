# DATA SENSITIVITY & PRIVACY DISCLAIMER

## No Sensitive Data or PII Present

This dataset contains **only publicly available Formula 1 racing information**. There are **no sensitive data, personally identifiable information (PII), or privacy concerns** associated with this project.

### Data Classification: **PUBLIC**

All data in this project is classified as **PUBLIC** and can be freely shared, analyzed, and distributed.

### What This Dataset Contains

- **F1 2023 Race Results**: Official race outcomes, finishing positions, points awarded
- **Driver & Team Information**: Names of drivers and constructors (all public figures with public information)
- **Circuit Information**: Track names, locations, basic specifications
- **Statistical Metrics**: Lap times, grid positions, DNF rates, performance statistics derived from public race data

### Why This Data Is Non-Sensitive

1. **Official Publication**: All data sourced from F1 official publications and publicly available APIs
2. **Public Figures**: Drivers and teams are public figures with extensive public information available
3. **No Personal Data**: No addresses, contact information, birth dates, social security numbers, or other personal identifiers beyond names
4. **No Financial Data**: No salaries, contract terms, or confidential business information
5. **No Health/Biometric Data**: No medical records, genetic information, or physical measurements
6. **No Location Tracking**: Geographic information limited to circuit locations (already public)
7. **No Behavioral Profiling**: No tracking of private activities or communications

### Data Sources Validation

-  F1 Official Website (FIA - Fédération Internationale de l'Automobile)
-  Publicly Available APIs
-  Published Race Reports
-  Historical Records (freely accessible)

### Security & Access Implications

**Result**: No security controls, access restrictions, or privacy safeguards required beyond standard academic integrity practices.

---

# Data Governance and Access Control


## 2. ACCESS CONTROL OBJECTIVES

### 2.1 Security Principles

1. **Least Privilege:** Users receive minimum access needed for their role
2. **Separation of Duties:** Critical functions require multiple authorizations
3. **Need-to-Know:** Access based on legitimate business need
4. **Defense in Depth:** Multiple layers of security controls
5. **Accountability:** All access is logged and auditable


---

## 3. ROLE-BASED ACCESS CONTROL (RBAC)

### 3.1 Role Hierarchy

```
┌─────────────────────────┐
│   Data Owner/Admin      │  Full access + policy management
└───────────┬─────────────┘
            │
    ┌───────┴────────┐
    │                │
┌───▼──────┐    ┌───▼──────────┐
│ Developer│    │ Data Analyst │  Read + aggregate
└───┬──────┘    └──────────────┘
    │
┌───▼─────────────┐
│ Public Dashboard│  Read-only (sanitized data)
└─────────────────┘
```

### 3.2 Role Definitions

#### Role 1: DATA OWNER / ADMINISTRATOR
**Purpose:** Overall data governance and system administration

**Permissions:**
-  **Read:** All fields including DOB
-  **Write:** Can modify data (with version control)
-  **Delete:** Can remove records (with audit trail)
-  **Grant:** Can assign roles to other users
-  **Schema:** Can alter database schema
-  **Export:** Can export complete dataset
-  **Admin:** Can access audit logs and system configurations

**Access Level:** UNRESTRICTED

**Assigned To:**
- Project Lead: [Name]
- Technical Lead: [Name]
- Data Governance Officer: [Name]

**Authentication:** Multi-factor authentication (MFA) required

**Access Locations:** Secure VPN only

---

#### Role 2: DATA ANALYST
**Purpose:** Perform statistical analysis and create visualizations

**Permissions:**
-  **Read:** All fields EXCEPT DOB (restricted)
-  **Aggregate:** Can compute statistics (avg, sum, count)
-  **Write:** Cannot modify raw data
-  **Delete:** Cannot delete records
-  **Export:** Can export sanitized datasets (no DOB)
-  **Query:** Can run SQL queries on approved tables/views
-  **Visualize:** Can create dashboards and reports

**Access Level:** READ-ONLY (sanitized)

**Assigned To:**
- Team Members: Aya Masri, Carmen Fhaily, Amira Merheb, Karim Chaar, Laure Awar
- External Analysts (if approved)

**Authentication:** Username/password + email verification

**Access Locations:** On-campus network or approved VPN

---

#### Role 3: DEVELOPER
**Purpose:** Develop and maintain data pipeline and applications

**Permissions:**
-  **Read:** All fields EXCEPT DOB in production
-  **Read:** All fields INCLUDING DOB in development (anonymized data)
-  **Write:** Can modify code and pipeline configurations
-  **Write:** Cannot modify production data
-  **Deploy:** Can deploy new dashboard versions
-  **Debug:** Can access application logs

**Access Level:** READ-ONLY (production), FULL (development)

**Assigned To:**
- Backend Developers
- Dashboard Developers
- DevOps Engineers

**Authentication:** SSH keys + password

**Access Locations:** Development environment (localhost, staging servers)

---

#### Role 4: PUBLIC DASHBOARD USER
**Purpose:** View published analytics and visualizations

**Permissions:**
-  **Read:** Public dashboard only (highly sanitized)
-  **Export:** Cannot download raw data
-  **Query:** Cannot run custom queries
-  **Interact:** Can filter and explore published dashboards

**Access Level:** PUBLIC (anonymous or authenticated)

**Assigned To:**
- F1 fans and general public (if published)
- Course instructors and reviewers
- External stakeholders (sponsor presentations)

**Authentication:** None required (or basic login for tracking)

**Access Locations:** Any internet connection

---


#### SQLite Implementation (Current Project)

```python
# Python-based access control for SQLite

import sqlite3
from functools import wraps
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    DEVELOPER = "developer"
    PUBLIC = "public"

class AccessControl:
    def __init__(self):
        self.current_user = None
        self.current_role = None
    
    def authenticate(self, username, password, role):
        """Authenticate user and set role"""
        # In production, validate against secure credential store
        if self._validate_credentials(username, password):
            self.current_user = username
            self.current_role = role
            return True
        return False
    
    def _validate_credentials(self, username, password):
        """Validate credentials against secure store"""
        # Placeholder - implement proper authentication
        # In production: check against hashed passwords in secure database
        return True
    
    def require_role(self, allowed_roles):
        """Decorator to enforce role-based access"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self.current_role not in allowed_roles:
                    raise PermissionError(f"Access denied. Required roles: {allowed_roles}")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def sanitize_query(self, query):
        """Remove DOB field from queries for non-admin users"""
        if self.current_role != Role.ADMIN:
            # Simple approach: fail if DOB is accessed
            if 'dob' in query.lower():
                raise PermissionError("Access to 'dob' field denied for your role")
        return query

# Usage example
ac = AccessControl()
ac.authenticate("analyst1", "password", Role.ANALYST)

@ac.require_role([Role.ADMIN, Role.ANALYST])
def run_query(query):
    sanitized_query = ac.sanitize_query(query)
    conn = sqlite3.connect('f1_analytics.db')
    return pd.read_sql_query(sanitized_query, conn)
```

