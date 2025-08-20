# Capital Planning Application – V1 Feature Set

This document defines the core features for version 1 of a capital planning software focused on **physical assets** (e.g., buildings, vehicles, equipment). These features represent table-stakes functionality necessary for organizations such as schools, municipalities, manufacturers, and farms.

---

## 1. Asset Inventory & Lifecycle Tracking ✅ COMPLETED
- ✅ Maintain a centralized register of all assets (buildings, vehicles, equipment).
- ✅ Store key attributes:
  - Asset name, type, category
  - Location
  - Installation/commissioning date
  - Expected useful life
  - Replacement cost
- ✅ Ability to update asset condition (e.g., Good, Fair, Poor).
- ✅ Calculate estimated replacement date based on useful life.

### Implementation Status:
- ✅ Backend models: AssetLifecycle model with all required fields
- ✅ Frontend UI: AssetLifecycleList.vue with full CRUD operations
- ✅ API endpoints: /api/cap-planning/v1/asset-lifecycle/
- ✅ Condition updates: POST /update_condition/ endpoint
- ✅ Replacement schedule: GET /replacement_schedule/ endpoint
- ✅ Maintenance analysis: GET /maintenance_analysis/ endpoint
- ✅ Additional features: Lifecycle percentage visualization, maintenance cost ratio

---

## 2. Capital Project Planning ✅ COMPLETED
- ✅ Create and manage a list of **capital projects** (e.g., equipment replacement, renovations).
- ✅ Capture project details:
  - Title, description
  - Associated asset(s)
  - Priority level
  - Scheduled year
  - Estimated cost
- ✅ Support for categorizing projects (building, fleet, equipment).

### Implementation Status:
- ✅ Backend models: CapitalProject model with all required fields
- ✅ Frontend UI: ProjectsList.vue with full CRUD operations
- ✅ Project-Asset linkage: ProjectAssetLink model with relationship types
- ✅ API endpoints: /api/cap-planning/v1/projects/
- ✅ Project approval: POST /approve/ endpoint
- ✅ Asset linking: POST /link_assets/ endpoint
- ✅ Priority matrix: GET /priority_matrix/ endpoint
- ✅ Yearly summary: GET /yearly_summary/ endpoint
- ✅ Additional features: Budget variance tracking, approval workflow

---

## 3. Budgeting & Forecasting 🔄 PLANNED
- Multi-year capital forecast (e.g., 5–10 years).
- Yearly aggregation of planned expenditures.
- Compare planned spending against available budget.
- Highlight budget gaps or surpluses.

---

## 4. Cost Estimation 🔄 PLANNED
- Simple cost entry for each asset/project (replacement or upgrade).
- Option to enter unit cost and quantity for transparency.
- Automatic roll-up of total costs by year and category.

---

## 5. Prioritization & Ranking 🔄 PLANNED
- Basic priority scoring or ranking mechanism.
- Ability to sort/filter projects by:
  - Urgency
  - Condition
  - Year
  - Category
- Support for manual adjustment of project priority.

---

## 6. Funding Management 🔄 PLANNED
- Input annual capital funding/budget.
- Allocate available funding to planned projects.
- View funded vs. unfunded projects.
- Highlight shortfalls when total projects exceed available funds.

---

## 7. Reporting & Dashboards 🔄 PLANNED
- Standard reports:
  - List of capital projects with status and cost
  - Annual forecast of expenditures
  - Summary by category (e.g., buildings vs. vehicles)
- Visual dashboards:
  - Yearly spending bar chart
  - Asset replacement timeline
  - Budget vs. forecast comparison

---

## 8. Document & Data Attachments 🔄 PLANNED
- Ability to attach files (photos, manuals, condition reports) to assets and projects.
- Support for notes and comments on each asset/project.

---

## 9. Basic Maintenance Data Linkage 🔄 PLANNED
- Display lifetime maintenance cost for assets (manual entry or calculated).
- Compare recent maintenance cost vs. replacement cost.
- Flag assets with disproportionate maintenance cost for potential replacement.

---

## Technical Implementation Details

### Database Schema Extensions

#### Asset Inventory Extensions (Feature 1)
- Extend existing Asset model with lifecycle tracking fields
- Add condition assessment tracking
- Add replacement cost calculations

#### Capital Projects (Feature 2)
- New CapitalProject model
- Project-Asset relationship table
- Project categories and priorities

### API Endpoints

#### Asset Lifecycle (Feature 1)
- `GET/PUT /api/cap-planning/v1/asset-lifecycle/`
- `POST /api/cap-planning/v1/asset-lifecycle/{id}/condition/`
- `GET /api/cap-planning/v1/asset-lifecycle/replacement-schedule/`

#### Capital Projects (Feature 2)
- `GET/POST /api/cap-planning/v1/projects/`
- `GET/PUT/DELETE /api/cap-planning/v1/projects/{id}/`
- `POST /api/cap-planning/v1/projects/{id}/link-assets/`

### Frontend Components

#### Asset Lifecycle Management
- AssetLifecycleList.vue
- AssetConditionForm.vue
- ReplacementSchedule.vue

#### Capital Projects
- ProjectsList.vue
- ProjectForm.vue
- ProjectDetail.vue
- AssetLinkage.vue

---

## Development Timeline

### Phase 1 (Completed - December 2024)
- ✅ Basic Capital Planning infrastructure
- ✅ Asset Inventory & Lifecycle Tracking (Feature 1)
- ✅ Capital Project Planning (Feature 2)
- ✅ 30 backend tests passing
- ✅ 19 frontend tests passing
- ✅ UX testing completed with EXCELLENT rating

### Phase 2 (Next Sprint)
- Budgeting & Forecasting (Feature 3)
- Cost Estimation (Feature 4)
- Prioritization & Ranking (Feature 5)

### Phase 3 (Future)
- Funding Management (Feature 6)
- Reporting & Dashboards (Feature 7)
- Document Attachments (Feature 8)
- Maintenance Data Linkage (Feature 9)