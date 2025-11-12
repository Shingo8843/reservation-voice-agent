# 💇‍♀️ Voice-Enabled Salon Reservation System — Full Scope
🎥 **Demo Video**  
🎬 [Watch the Demo on YouTube](https://youtu.be/vbU8FWOfAuo)

## 1. Overview

This project delivers a **voice AI-powered salon reservation system** for **ABC Salon**, transforming traditional phone-based scheduling into an intelligent, automated experience. The system captures booking details, validates availability through a FastAPI backend, and records confirmed reservations in Supabase.

Developed as part of a proof-of-concept by a **Forward Deployed Engineer**, this solution integrates conversational AI with a structured scheduling API, supporting both English and Japanese clients.

---

## 2. Project Context

### 2.1 Background

From the discovery sessions, ABC Salon faces missed bookings because calls often arrive during active services. The clientele consists mostly of senior regulars who prefer simplicity and clarity.

### 2.2 Objectives

Based on the Scope of Work:

* Automate inbound booking, modification, confirmation, and cancellation calls.
* Maintain natural and polite tone across voice interactions.
* Ensure booking accuracy and structured API integration.

### 2.3 Target Outcomes

* Reduce missed bookings by at least 80%.
* Achieve ≥90% accuracy for date, time, and service capture.
* Reach ≥90% completion rate for inbound calls routed to the assistant.

---

## 3. System Architecture

### 3.1 Components

| Layer                     | Description                                                                                      |
| ------------------------- | ------------------------------------------------------------------------------------------------ |
| **Voice Assistant**       | Handles natural-language interaction and intent detection (book, modify, confirm, cancel).       |
| **FastAPI Backend**       | REST API that manages reservation data, ensures availability, and handles Supabase transactions. |
| **Supabase (PostgreSQL)** | Persistent storage for customer reservations with built-in validation and timestamps.            |

### 3.2 Interaction Flow

1. **Inbound Call Trigger** → Voice agent identifies intent (book, modify, confirm, cancel).
2. **Field Capture** → Customer provides name, phone, date, time, stylist, and service.
3. **API Transaction** → FastAPI endpoint processes request and validates availability.
4. **Confirmation** → Assistant reads back booking details and confirms before committing.
5. **Database Write** → Data persisted to Supabase via `add_reservation`.
6. **Response Output** → Assistant ends with confirmation message.

---

## 4. FastAPI Backend

### 4.1 Key Features

* **Endpoints**:

  * `POST /add` — create reservation
  * `GET /lookup/{phone_number}` — list bookings for customer
  * `PUT /modify/{reservation_id}` — update booking details
  * `DELETE /cancel/{reservation_id}` — cancel a reservation
  * `GET /availability` — check available time slots

* **Conflict Prevention**: Prevents double booking for the same stylist and time.

* **Validation**: Ensures duration > 0 and normalizes time input.

* **Header-based Input**: Designed for voice agent API calls with prefixed headers like `X-Customer-Name` and `X-Reservation-Time`.

### 4.2 Data Models

Defined in `models.py`:

```python
class Reservation(BaseModel):
    customer_name: str
    phone_number: str
    reservation_date: date
    reservation_time: time
    stylist_name: str
    service_menu: str
    duration_minutes: Optional[int] = 60
    status: Optional[str] = "scheduled"
```

### 4.3 Example Payload

```json
{
  "customer_name": "Haruka Tanaka",
  "phone_number": "080-1234-5678",
  "reservation_date": "2025-11-06",
  "reservation_time": "15:00:00",
  "stylist_name": "Sato",
  "service_menu": "Cut and Color",
  "notes": "Prefers afternoon slot"
}
```

---

## 5. Voice Agent Logic

### 5.1 Intents

The agent supports four primary intents:

1. **New Reservation**
2. **Modify Reservation**
3. **Confirm Reservation**
4. **Cancel Reservation**

### 5.2 Call Handling Rules

* Speak warmly and clearly using short, natural phrases.
* Always repeat and confirm all reservation details.
* Transfer to human representative for out-of-scope requests (e.g., kimono dressing, special photo bookings).
* If system error occurs, politely ask caller to retry later.

### 5.3 Example Dialogue (New Booking)

> **Agent:** “Thank you for calling ABC Salon, how can I assist you?”
> **Caller:** “I want to book a haircut tomorrow afternoon.”
> **Agent:** “Sure, may I have your name and phone number please?”
> **Caller:** “It is Haruka Tanaka, 080-1234-5678.”
> **Agent:** “We have 1 p.m. and 3 p.m. available with Sato, which works for you?”
> **Caller:** “3 p.m. please.”
> **Agent:** “Got it. Haircut for Haruka Tanaka on November 6 at 3 p.m. with Sato, correct?”
> **Caller:** “Yes.”
> **Agent:** “Perfect, you are all set. See you then.”

---

## 6. Success Metrics

| Metric                  | Definition                                | Target             |
| ----------------------- | ----------------------------------------- | ------------------ |
| **Connection Rate**     | % of calls reaching the assistant         | ≥95%               |
| **Completion Rate**     | % of calls completing required fields     | ≥90%               |
| **Data Accuracy**       | % of correctly parsed reservation details | ≥90%               |
| **Average Handle Time** | Duration per completed call               | Track and optimize |
| **Human Transfer Rate** | % of calls escalated to staff             | ≤15%               |

---

## 7. Risks and Mitigation

| Risk                                   | Mitigation                                          |
| -------------------------------------- | --------------------------------------------------- |
| Older callers struggle with automation | Use natural phrasing and minimal options.           |
| Ambiguous time phrases (“around noon”) | Agent repeats back explicit times for confirmation. |
| API latency delays                     | Cache short-term availability results.              |
| Schedule change variability            | Allow dynamic calendar updates in Supabase.         |

---

## 8. Deployment

### Render Deployment Workflow

1. **Push to GitHub**

   ```bash
   git add .
   git commit -m "Voice API ready"
   git push origin main
   ```
2. **Create Render Web Service**

   * Link GitHub repository.
   * Set environment variables:

     * `SUPABASE_URL`
     * `SUPABASE_KEY`
3. **Start Command**

   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4
   ```
4. **Access**

   * `https://your-service.onrender.com/docs`

---

## 9. Future Enhancements

* Add LINE chat integration for text-based booking.
* Sync directly with Google Calendar or salon management software.
* Add notification support via SMS or LINE Messaging API.
* Introduce multilingual support (Japanese and English).
* Integrate voice analytics to optimize tone and response flow.

---

## 10. References

* Discovery: **ABC Salon Voice Booking Insights** [Discovery Document](./docs/Discovery.pdf)
* Scope of Work: **Voice Assistant Functional Requirements** [Scope of Work](./docs/Scope_of_Work.pdf)
* Specification: **Conversation and API Prompts** [Project Specification](./docs/Project_Specification.pdf)
* Backend Implementation: **FastAPI Reservation API** [Backend Code (main.py)](./main.py), [Data Models (models.py)](./models.py)

---



