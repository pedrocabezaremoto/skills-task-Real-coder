# Wedding Venue Management System

## Description / Context

We run a mid-size wedding venue that hosts 3 events per weekend across 2 ceremony spaces and a reception hall. Our current spreadsheet system for inquiries, booking, vendor coordination, timeline management, day-of logistics, and billing cannot handle the volume anymore. I need a frontend application with separate views for the sales team handling inquiries, the event coordinator managing logistics, the kitchen for catering coordination, and the owner for financial oversight.

The system must manage the full customer lifecycle from initial inquiry through contracting, handle complex financial calculations including tiered venue pricing, additional services, operating costs, and installment payment schedules, coordinate vendors across event dates, manage event timelines with conflict detection, handle catering orders with dietary precision, and enforce floor plan capacity constraints. All data must be bundled locally with a comprehensive sample dataset — no live fetching or external API calls. Overdue payment detection MUST occur dynamically when the application loads by comparing the current date against payment due dates plus a 7-day grace period.

## Tech Stack

- React 18.2
- TypeScript 5.4
- Vite 5.2
- Tailwind CSS 3.4
- Lucide React 0.344.0
- React Router 6.22

## Key Requirements

### Data & Business Logic

1. The system MUST manage wedding inquiries capturing: couple names, wedding date, guest count (integer between 20 and 300 inclusive), ceremony type (indoor, outdoor, both), package type (ceremony, reception, all-inclusive), and budget range with minimum and maximum values.
2. Each inquiry MUST transition through exactly these workflow states in order: Received, Tour Scheduled, Proposal Sent, Contracted, Lost. An inquiry in the Lost state is terminal.
3. The system MUST enforce booking constraints configurable per day of week: Weekdays allow a maximum of 1 event, Saturday allows a maximum of 3 events, Sunday allows a maximum of 2 events.
4. The system MUST calculate venue fees based on the day of the week: Friday 8000, Saturday 12000, Sunday 9000, Weekday 5000.
5. The system MUST generate a payment schedule of 3 installments: 30 percent of total at signing, 40 percent at 90 days before the wedding date, 30 percent at 30 days before the wedding date. All installment amounts MUST be rounded to 2 decimal places.
6. The system MUST flag a payment as overdue when the payment is not received within 7 calendar days after its due date. The overdue status MUST be calculated dynamically on each application load by comparing the current date against the due date plus 7 days. Overdue payments MUST be visually distinguishable from pending payments using a red warning indicator.
7. The system MUST manage vendors within these categories: caterer, florist, DJ/band, photographer, officiant, planner. Each vendor MUST have a numerical rating from 1 to 5 inclusive and a contactInfo field containing phone number and email. The system MUST detect and flag any attempt to double-book a vendor at the same venue location on the same date and overlapping time.
8. The system MUST manage timeline events each with an event type (ceremony, cocktail hour, dinner, first dance, cake cutting), start time, end time, duration, and location assignment. The system MUST detect and flag any two events that overlap in the same location.
9. The system MUST calculate revenue as the sum of the venue fee plus additional services revenue. The system MUST calculate profit margin as (revenue minus operating costs) divided by revenue multiplied by 100, expressed as a percentage. The profit margin MUST be rounded to exactly 1 decimal place.
10. The system MUST calculate catering order quantities as the guest count plus a 5 percent buffer, with the result rounded up to the nearest integer. Dietary counts distributed across categories (standard, vegetarian, vegan, gluten-free, kosher) MUST sum exactly to the guest count, not the buffered total.
11. The system MUST enforce that a floor plan seating capacity is greater than or equal to the assigned event guest count. Any assignment violating this constraint MUST be flagged.

### Dashboard Views

12. The Sales Dashboard MUST display: an inquiry pipeline using a Kanban board with columns for each workflow state showing the inquiry count and list, a tour calendar showing scheduled tour dates with dates, and a conversion rate calculated as contracted inquiries divided by total inquiries multiplied by 100 and rounded to exactly 1 decimal place.
13. The Coordinator Dashboard MUST display: event timelines with event type, start time, end time, duration, and location for each booking with timeline conflicts highlighted using a warning indicator, vendor assignments grouped by event showing vendor name, category, rating, and contactInfo, and payment status showing each installment with due date, amount, and overdue status with a red warning indicator for overdue payments.
14. The Kitchen Dashboard MUST display: catering orders for each event showing the buffered total quantity as guest count plus 5 percent rounded up, a full dietary breakdown table showing counts for standard, vegetarian, vegan, gluten-free, and kosher meals, and a validation indicator showing whether the sum of dietary counts equals the guest count.
15. The Owner Dashboard MUST display: revenue aggregated by month displayed as a Bar chart, profit margin percentage rounded to 1 decimal place calculated using (venue fee plus additional services minus operating costs) divided by (venue fee plus additional services) multiplied by 100, booking pace showing the number of confirmed bookings over time, vendor ratings summary with average rating per vendor category rounded to 1 decimal place, and year-over-year revenue growth percentage rounded to 1 decimal place.

### UI Requirements

16. The application MUST provide a persistent sidebar navigation with labeled links using Lucide React icons that allows switching between the four dashboard views. The navigation MUST be visible on all dashboard pages.
17. The UI MUST meet professional freelance standards: clean layout, readable typography, consistent spacing, and functional interactive elements with proper data presentation using tables and charts.

## Expected Interface

### Types Module
- Path: src/types/index.ts
- Name: WeddingVenueTypes
- Type: TypeScript module
- Input: N/A
- Output: Exported interfaces: Inquiry, WorkflowState, BookingConstraints, PaymentInstallment, Vendor, VendorCategory, TimelineEvent, CateringOrder, DietaryCounts, FloorPlan, DashboardMetrics, EventType, PackageType
- Description: Defines all TypeScript interfaces and types used across the application. Inquiry includes couple name, wedding date, guest count, ceremony type (indoor, outdoor, both), package type (ceremony, reception, all-inclusive), budget range, and workflow state. PaymentInstallment includes installment number, due date, amount, and payment status (pending, paid, overdue). Vendor includes name, category, rating from 1 to 5, contactInfo with phone and email fields, and availability schedule. TimelineEvent includes eventType (ceremony, cocktail hour, dinner, first dance, cake cutting), startTime, endTime, duration, and location. DashboardMetrics includes totalRevenue, operatingCosts, additionalServices, profitMargin, and yearOverYearGrowth fields.

### Sample Data Module
- Path: src/data/sampleData.ts
- Name: sampleData
- Type: TypeScript module
- Input: N/A
- Output: Object containing sample data arrays populated with exactly 5 inquiries in various workflow states, exactly 5 vendors across different categories each with contactInfo, exactly 3 timeline events with event types, exactly 3 catering orders with dietary breakdowns, and exactly 2 floor plans with seating capacities
- Description: Exports a comprehensive hardcoded sample dataset that populates all dashboard views. Each booking in the sample data MUST include operatingCosts and additionalServices numeric fields to enable profit margin calculation. All data MUST be bundled locally within this file. No external data fetching or API calls. Must demonstrate realistic wedding venue scenarios with varied states and values.

### Utility Functions Module
- Path: src/utils/calculations.ts
- Name: calculateVenueFee
- Type: function
- Input: dayOfWeek: string with values friday, saturday, sunday, weekday
- Output: number
- Description: Returns the venue fee for the given day of week. Friday returns 8000, Saturday returns 12000, Sunday returns 9000, weekday returns 5000.

- Path: src/utils/calculations.ts
- Name: calculateRevenue
- Type: function
- Input: venueFee: number, additionalServices: number
- Output: number
- Description: Returns total revenue as the sum of venueFee plus additionalServices.

- Path: src/utils/calculations.ts
- Name: calculateProfitMargin
- Type: function
- Input: revenue: number, operatingCosts: number
- Output: number
- Description: Calculates profit margin as (revenue minus operatingCosts) divided by revenue multiplied by 100. Returns result rounded to exactly 1 decimal place. Returns 0 when revenue is 0 to avoid division by zero.

- Path: src/utils/calculations.ts
- Name: generatePaymentSchedule
- Type: function
- Input: totalAmount: number, weddingDate: string in ISO 8601 date format, currentDate: string in ISO 8601 date format
- Output: PaymentInstallment[]
- Description: Generates an array of 3 payment installments. Installment 1 is 30 percent of totalAmount due at signing using currentDate. Installment 2 is 40 percent due 90 days before weddingDate. Installment 3 is 30 percent due 30 days before weddingDate. Each amount is rounded to 2 decimal places. Each installment status is computed dynamically: status is overdue when currentDate is greater than dueDate plus 7 days and status is not paid. Status is pending when currentDate is less than or equal to dueDate plus 7 days and status is not paid.

- Path: src/utils/calculations.ts
- Name: calculateCateringBufferedTotal
- Type: function
- Input: guestCount: number
- Output: number
- Description: Returns guest count plus 5 percent buffer rounded up using Math.ceil. For 100 guests returns 105. For 200 guests returns 210.

- Path: src/utils/calculations.ts
- Name: detectTimelineConflicts
- Type: function
- Input: events: array of objects with fields id, startTime, endTime, location
- Output: array of objects with fields eventA, eventB, location
- Description: Detects all pairs of events that overlap in time at the same location. An overlap occurs when event A time range intersects event B time range at the same location. Returns array of conflict objects each identifying the two conflicting event IDs and the shared location. Returns empty array when no conflicts exist.

- Path: src/utils/calculations.ts
- Name: checkBookingAllowed
- Type: function
- Input: date: string in ISO date format, existingBookings: array of objects with field date, maxPerDay: object with fields weekday, saturday, sunday
- Output: object with fields allowed (boolean) and reason (string)
- Description: Checks whether a new booking is permitted on the given date. Weekday dates allow up to maxPerDay.weekday bookings, Saturday allows up to maxPerDay.saturday, Sunday allows up to maxPerDay.sunday. Returns allowed true with empty string reason when the limit is not reached. Returns allowed false with a descriptive reason when the limit is exceeded.

- Path: src/utils/calculations.ts
- Name: calculateConversionRate
- Type: function
- Input: inquiries: array of objects with field status (string)
- Output: number
- Description: Calculates conversion rate as a percentage. Counts inquiries with status Contracted, divides by total inquiries, multiplies by 100, and rounds to exactly 1 decimal place. Returns a number between 0 and 100. Returns 0 when inquiries array is empty.

- Path: src/utils/calculations.ts
- Name: aggregateRevenueByMonth
- Type: function
- Input: bookings: array of objects with fields date (string), totalAmount (number)
- Output: array of objects with fields month (string in YYYY-MM format) and revenue (number)
- Description: Aggregates booking revenue by calendar month. Each entry contains the month label in YYYY-MM format and the sum of totalAmount for all bookings in that month. Returns entries sorted chronologically. Returns empty array when bookings is empty.

- Path: src/utils/calculations.ts
- Name: calculateYearOverYearGrowth
- Type: function
- Input: revenueByMonth: array of objects with fields month (string), revenue (number)
- Output: number
- Description: Calculates year-over-year revenue growth percentage. Compares total revenue from the most recent 12 months against the preceding 12 months. Returns growth as a percentage rounded to exactly 1 decimal place. Returns 0 when insufficient data exists for comparison.

- Path: src/utils/calculations.ts
- Name: calculateAverageVendorRating
- Type: function
- Input: vendors: array of objects with fields category (string), rating (number)
- Output: array of objects with fields category (string), averageRating (number)
- Description: Calculates average rating per vendor category. Each entry contains the category name and the average rating rounded to exactly 1 decimal place. Returns empty array when vendors is empty.

### React Components

- Path: src/App.tsx
- Name: App
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Root application component. Sets up React Router with four routes: sales, coordinator, kitchen, owner. Renders a persistent sidebar navigation with labeled navigation links using Lucide React icons. Each navigation link navigates to its corresponding dashboard route.

- Path: src/components/SalesDashboard.tsx
- Name: SalesDashboard
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Renders the sales team dashboard. Displays an inquiry pipeline using a Kanban board with columns for each workflow state showing the inquiry count and list. Shows a tour calendar section listing upcoming scheduled tours with dates. Displays the conversion rate percentage rounded to 1 decimal place calculated from sample data.

- Path: src/components/CoordinatorDashboard.tsx
- Name: CoordinatorDashboard
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Renders the event coordinator dashboard. Displays event timelines showing each booking events with event type, start time, end time, duration, and location. Highlights timeline conflicts detected by detectTimelineConflicts using a warning indicator. Shows vendor assignments grouped by event with vendor name, category, rating, and contactInfo. Displays payment status table showing each installment with due date, amount, and overdue status using a red warning indicator for overdue payments.

- Path: src/components/KitchenDashboard.tsx
- Name: KitchenDashboard
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Renders the kitchen dashboard. Displays catering orders for each event showing the buffered total quantity using calculateCateringBufferedTotal. Shows full dietary breakdown table with counts for standard, vegetarian, vegan, gluten-free, and kosher meals. Includes a validation indicator showing whether the sum of dietary counts equals the guest count.

- Path: src/components/OwnerDashboard.tsx
- Name: OwnerDashboard
- Type: React Component
- Input: N/A
- Output: JSX element
- Description: Renders the owner financial dashboard. Displays monthly revenue using aggregateRevenueByMonth shown as a Bar chart. Shows profit margin percentage rounded to 1 decimal place using calculateProfitMargin. Displays booking pace with number of confirmed bookings over time using a line chart. Shows vendor ratings summary with average rating per vendor category rounded to 1 decimal place using calculateAverageVendorRating. Displays year-over-year growth percentage rounded to 1 decimal place using calculateYearOverYearGrowth.

## Current State

Empty repository with test files only.
