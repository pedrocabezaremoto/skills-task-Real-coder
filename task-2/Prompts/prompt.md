# Wedding Venue Management System

## Description / Context

We run a mid-size wedding venue that hosts 3 events per weekend across 2 ceremony spaces and a reception hall. Our current spreadsheet system for inquiries, booking, vendor coordination, timeline management, day-of logistics, and billing cannot handle the volume anymore. I need a frontend application with separate views for the sales team handling inquiries, the event coordinator managing logistics, the kitchen for catering coordination, and the owner for financial oversight.

The system must manage the full customer lifecycle from initial inquiry through contracting, handle complex financial calculations including tiered venue pricing and installment payment schedules, coordinate vendors across event dates, manage event timelines with conflict detection, handle catering orders with dietary precision, and enforce floor plan capacity constraints. All data must be bundled locally with a comprehensive sample dataset — no live fetching or external API calls.

## Tech Stack

- React 18.2
- TypeScript 5.4
- Vite 5.2
- Tailwind CSS 3.4
- Lucide React 0.344.0
- React Router 6.22

## Key Requirements

### Data & Business Logic

1. The system MUST manage wedding inquiries capturing: couple names, wedding date, guest count (integer between 20 and 300 inclusive), ceremony type (indoor, outdoor, or both), and budget range (minimum and maximum values).
2. Each inquiry MUST transition through exactly these workflow states in order: Received, Tour Scheduled, Proposal Sent, Contracted, Lost. An inquiry in the Lost state is terminal.
3. The system MUST enforce booking constraints configurable per day of week: Weekdays allow a maximum of 1 event, Saturday allows a maximum of 3 events, Sunday allows a maximum of 2 events.
4. The system MUST calculate venue fees based on the day of the week: Friday $8000, Saturday $12000, Sunday $9000, Weekday $5000.
5. The system MUST generate a payment schedule of 3 installments: 30% of total at signing, 40% at 90 days before the wedding date, 30% at 30 days before the wedding date. All installment amounts MUST be rounded to 2 decimal places.
6. The system MUST flag a payment as overdue when the payment is not received within 7 calendar days after its due date. Overdue payments MUST be visually distinguishable from pending payments.
7. The system MUST manage vendors within these categories: caterer, florist, DJ/band, photographer, officiant, planner. Each vendor MUST have a numerical rating from 1 to 5 inclusive. The system MUST detect and flag any attempt to double-book a vendor at the same venue location on the same date and overlapping time.
8. The system MUST manage timeline events each with a start time, end time, duration, and location assignment. The system MUST detect and flag any two events that overlap in the same location.
9. The system MUST calculate catering order quantities as the guest count plus a 5% buffer, with the result rounded up to the nearest integer. Dietary counts distributed across categories (standard, vegetarian, vegan, gluten-free, kosher) MUST sum exactly to the guest count (not the buffered total).
10. The system MUST enforce that a floor plan seating capacity is greater than or equal to the assigned event guest count. Any assignment violating this constraint MUST be flagged.

### Dashboard Views

11. The Sales Dashboard MUST display: an inquiry pipeline showing each inquiry's current workflow stage, a tour calendar showing scheduled tour dates, and a conversion rate metric calculated as (contracted inquiries divided by total inquiries) multiplied by 100.
12. The Coordinator Dashboard MUST display: event timelines with duration and location for each booking, vendor assignments grouped by event, and payment status showing each installment with its due date, amount, and overdue status.
13. The Kitchen Dashboard MUST display: catering orders for each event with the full dietary breakdown showing counts for standard, vegetarian, vegan, gluten-free, and kosher meals, the total buffered quantity, and a validation indicator showing whether dietary counts sum to the guest count.
14. The Owner Dashboard MUST display: revenue aggregated by month, profit margin percentage, booking pace showing number of confirmed bookings over time, vendor ratings summary across all categories, and year-over-year revenue growth percentage.

### UI Requirements

15. The application MUST provide a persistent navigation mechanism that allows switching between the four dashboard views.
16. The UI MUST meet professional freelance standards: clean layout, readable typography, consistent spacing, functional interactive elements, and proper data presentation using tables, cards, and charts.

## Expected Interface

### Types Module
- Path: src/types/index.ts
- Name: WeddingVenueTypes
- Type: TypeScript module
- Input: N/A
- Output: Exported interfaces: Inquiry, WorkflowState, BookingConstraints, VenueFee, PaymentInstallment, Vendor, VendorCategory, TimelineEvent, CateringOrder, DietaryCounts, FloorPlan, DashboardMetrics
- Description: Defines all TypeScript interfaces and types used across the application. Inquiry includes couple name, wedding date, guest count, ceremony type, budget range, and workflow state. PaymentInstallment includes installment number, due date, amount, and payment status. Vendor includes name, category, rating, and availability schedule.

### Sample Data Module
- Path: src/data/sampleData.ts
- Name: sampleData
- Type: TypeScript module
- Input: N/A
- Output: Object containing sample data arrays populated with at least 5 inquiries in various workflow states, 5 vendors across different categories, 3 timeline events, 3 catering orders with dietary breakdowns, and 2 floor plans with seating capacities
- Description: Exports a comprehensive hardcoded sample dataset that populates all dashboard views. All data MUST be bundled locally within this file. No external data fetching or API calls. Must demonstrate realistic wedding venue scenarios with varied states and values.

### Utility Functions Module
- Path: src/utils/calculations.ts
- Name: calculateVenueFee
- Type: function
- Input: dayOfWeek: string (values: 'friday', 'saturday', 'sunday', 'weekday')
- Output: number
- Description: Returns the venue fee for the given day of week. Friday returns 8000, Saturday returns 12000, Sunday returns 9000, weekday returns 5000.

- Path: src/utils/calculations.ts
- Name: generatePaymentSchedule
- Type: function
- Input: totalAmount: number, weddingDate: string (ISO 8601 date format)
- Output: PaymentInstallment[]
- Description: Generates an array of 3 payment installments. Installment 1 is 30% of totalAmount due at signing (current date). Installment 2 is 40% due 90 days before weddingDate. Installment 3 is 30% due 30 days before weddingDate. Each amount is rounded to 2 decimal places. Each installment includes a status field set to 'pending', 'paid', or 'overdue'. Status is 'overdue' when the due date is in the past and status is not 'paid'.

- Path: src/utils/calculations.ts
- Name: calculateCateringBufferedTotal
- Type: function
- Input: guestCount: number
- Output: number
- Description: Returns the guest count plus 5% buffer, rounded up using Math.ceil. For 100 guests returns 105. For 200 guests returns 210.

- Path: src/utils/calculations.ts
- Name: detectTimelineConflicts
- Type: function
- Input: events: { id: string, startTime: string, endTime: string, location: string }[]
- Output: { eventA: string, eventB: string, location: string }[]
- Description: Detects all pairs of events that overlap in time at the same location. An overlap occurs when event A's time range intersects event B's time range at the same location. Returns an array of conflict objects, each identifying the two conflicting event IDs and the shared location. Returns an empty array when no conflicts exist.

- Path: src/utils/calculations.ts
- Name: checkBookingAllowed
- Type: function
- Input: date: string (ISO date), existingBookings: { date: string }[], maxPerDay: { weekday: number, saturday: number, sunday: number }
- Output: { allowed: boolean, reason: string }
- Description: Checks whether a new booking is permitted on the given date. Weekday dates allow up to maxPerDay.weekday bookings, Saturday allows up to maxPerDay.saturday, Sunday allows up to maxPerDay.sunday. Returns allowed=true with empty reason when the limit is not reached. Returns allowed=false with a descriptive reason when the limit is exceeded.

- Path: src/utils/calculations.ts
- Name: calculateConversionRate
- Type: function
- Input: inquiries: { status: string }[]
- Output: number
- Description: Calculates the conversion rate as a percentage. Counts inquiries with status 'Contracted', divides by total inquiries, multiplies by 100. Returns a number between 0 and 100. Returns 0 when inquiries array is empty.

- Path: src/utils/calculations.ts
- Name: aggregateRevenueByMonth
- Type: function
- Input: bookings: { date: string, totalAmount: number }[]
- Output: { month: string, revenue: number }[]
- Description: Aggregates booking revenue by calendar month. Each entry contains the month label (format 'YYYY-MM') and the sum of totalAmount for all bookings in that month. Returns entries sorted chronologically. Returns empty array when bookings is empty.

- Path: src/utils/calculations.ts
- Name: calculateYearOverYearGrowth
- Type: function
- Input: revenueByMonth: { month: string, revenue: number }[]
- Output: number
- Description: Calculates year-over-year revenue growth percentage. Compares total revenue from the most recent 12 months against the preceding 12 months. Returns the growth as a percentage. Returns 0 when insufficient data exists for comparison.

### React Components

- Path: src/App.tsx
- Name: App
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Root application component. Sets up React Router with four routes: /sales, /coordinator, /kitchen, /owner. Renders a persistent sidebar navigation with labeled navigation links using Lucide React icons. Each navigation link navigates to its corresponding dashboard route.

- Path: src/components/SalesDashboard.tsx
- Name: SalesDashboard
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Renders the sales team dashboard. Displays an inquiry pipeline table or kanban with columns for each workflow state (Received, Tour Scheduled, Proposal Sent, Contracted, Lost) showing the count and list of inquiries in each. Shows a tour calendar section listing upcoming scheduled tours with dates. Displays the conversion rate percentage calculated from sample data.

- Path: src/components/CoordinatorDashboard.tsx
- Name: CoordinatorDashboard
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Renders the event coordinator dashboard. Displays event timelines showing each booking's events with start time, end time, duration, and location. Highlights any timeline conflicts detected by detectTimelineConflicts using a warning indicator. Shows vendor assignments grouped by event. Displays payment status table showing each installment with due date, amount, and overdue status with visual indicators for overdue payments.

- Path: src/components/KitchenDashboard.tsx
- Name: KitchenDashboard
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Renders the kitchen dashboard. Displays catering orders for each event showing the buffered total quantity using calculateCateringBufferedTotal. Shows full dietary breakdown table (standard, vegetarian, vegan, gluten-free, kosher) with counts. Includes a validation indicator showing whether the sum of all dietary counts equals the guest count.

- Path: src/components/OwnerDashboard.tsx
- Name: OwnerDashboard
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Renders the owner financial dashboard. Displays monthly revenue bar or table using aggregateRevenueByMonth. Shows profit margin percentage. Displays booking pace with number of confirmed bookings over time. Shows vendor ratings summary with average rating per vendor category. Displays year-over-year growth percentage using calculateYearOverYearGrowth.

## Current State

Empty repository with test files only.
