# Project: Wedding Venue Management System (Real Coder Task 2)

## Project Goal
Generate high-quality, verified software solutions for freelance-style tasks starting from a blank slate. Transform a raw task description into a structured prompt intended for an agent to solve the task, develop a complete 'from-scratch' functional solution (Golden Patch), and provide a dual-layer verification suite consisting of automated test cases and a multi-dimensional expert rubric.

## Task Workflow
1. **Re-write a prompt based on the task description**: A structured entry point that guides an AI agent to build the solution from scratch.
2. **F2P Verification**: A test suite that reliably fails on an empty codebase.
3. **Expert Rubric**: A qualitative scoring guide for dimensions that automated tests can't catch (e.g., code readability, instruction following).
4. **Create the solution (Golden Patch)**: A high-quality implementation that solves the task & passing every unit test you write & rubrics you build.
5. **F2P Verification**: A test suite that passes once the Golden Patch is applied.

## Task Type
Frontend Development

## Task Description
We run a mid-size wedding venue that hosts 3 events per weekend across 2 ceremony spaces and a reception hall, and our current spreadsheet system for inquiries, booking, vendor coordination, timeline management, day-of logistics, and billing can not handle the volume anymore. I need a frontend application with separate views for the sales team handling inquiries, the event coordinator managing logistics, the kitchen for catering coordination, and the owner for financial oversight. 

### Key Features & Business Logic:
- **Inquiry Management**: Capture couple names, date, guest count (20 to 300), ceremony type (indoor, outdoor, or both), and budget range.
- **Workflow States**: Received, Tour Scheduled, Proposal Sent, Contracted, and Lost.
- **Booking Constraints**: Configurable per day of week (Weekdays max 1, Saturday max 3, Sunday max 2).
- **Financials**:
    - Venue Fee: Friday $8000, Saturday $12000, Sunday $9000, Weekday $5000.
    - Payment Schedule: 3 installments (30% at signing, 40% 90 days before, 30% 30 days before). Rounded to 2 decimal places.
    - Automatic flagging for payments not received within 7 days of due date.
- **Vendor Management**: Categories (caterer, florist, DJ/band, photographer, officiant, planner). Includes rating (1-5 scale). Prevent double-booking vendors at the same venue/date/time.
- **Timeline Management**: Events with duration and location. Flag overlaps in the same location.
- **Catering Coordination**: Orders must match guest count + 5% buffer (rounded up). Dietary counts (standard, vegetarian, vegan, gluten-free, kosher) must sum to guest count.
- **Floor Plan**: Seating capacity must be >= guest count.
- **Dashboard Views**:
    - **Sales**: Inquiry pipeline, tour calendar, conversion rate.
    - **Coordinator**: Timelines, vendor assignments, payment status.
    - **Kitchen**: Catering orders with dietary breakdown.
    - **Owner**: Revenue by month, profit margins, booking pace, vendor ratings, year-over-year growth.

## Guidelines
- **UI Design**: Must meet professional freelance standards. Even if not explicitly mentioned, it must look good and be functional.
- **Data**: Live fetching or sample dataset (included in codebase).
- **Rubric**: Must cover UI design if it's in the top 30 most important things.
- **Tech Stack**: Choose a specific tech stack (not "Any").
- **Constraints**: Do NOT include unit test & rubric instructions in the prompt.
