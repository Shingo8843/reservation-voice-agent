# 💇‍♀️ Voice-Enabled Salon Reservation System

**Backend:** FastAPI + Supabase (PostgreSQL)

A REST API for voice-based salon booking, supporting reservation creation, lookup, modification, cancellation, and availability checking.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_SERVICE_ROLE_KEY
```

Get these values from your Supabase project settings (Project Settings → API).

### 3. Set Up Database

Run the SQL schema in `schema.sql` in your Supabase SQL Editor to create the necessary tables and indexes.

### 4. Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

## 📚 API Endpoints

### POST `/add`
Create a new reservation.

**Request Body:**
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

### GET `/lookup/{phone_number}`
Get all reservations for a phone number.

**Example:** `GET /lookup/080-1234-5678`

### PATCH `/modify/{reservation_id}`
Update an existing reservation.

**Request Body:**
```json
{
  "reservation_time": "16:00:00",
  "stylist_name": "Sato"
}
```

### PATCH `/cancel/{reservation_id}`
Cancel a reservation.

### GET `/availability`
Check availability for a stylist on a specific date.

**Query Parameters:**
- `reservation_date`: Date in YYYY-MM-DD format
- `stylist`: Stylist name

**Example:** `GET /availability?reservation_date=2025-11-06&stylist=Sato`

## 🔒 Database Constraints

- **No Double Booking:** A unique index prevents overlapping bookings for the same stylist at the same time (only for `status = 'scheduled'`)
- **Automatic Timestamps:** `updated_at` is automatically updated on record modification
- **Default Duration:** All reservations default to 60 minutes

## 📞 Voice AI Integration

The API is designed to work with voice AI assistants:

1. **Booking:** Call `/add` endpoint when customer wants to book
2. **Rescheduling:** Use `/modify/{id}` to change reservation details
3. **Cancellation:** Use `/cancel/{id}` to cancel appointments
4. **Availability Check:** Use `/availability` to check if a time slot is free
5. **Confirmation:** Use `/lookup/{phone_number}` to retrieve customer appointments

## 🚨 Error Handling

- `409 Conflict`: Time slot already booked
- `404 Not Found`: Reservation not found
- `400 Bad Request`: Invalid input data
- `500 Internal Server Error`: Server/database error

## 🚀 Deploy to Render

### Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Create a new Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Set Environment Variables**
   - In your Render service settings, add these environment variables:
     - `SUPABASE_URL`: Your Supabase project URL
     - `SUPABASE_KEY`: Your Supabase service role key
   - Or mark them as "Sync" in the render.yaml to configure in the dashboard

4. **Deploy**
   - Render will automatically build and deploy your service
   - Your API will be available at `https://your-service.onrender.com`

### Option 2: Manual Configuration

1. **Create a new Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build Settings**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4`

3. **Set Environment Variables**
   - Add `SUPABASE_URL` and `SUPABASE_KEY` in the Environment section

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application

### Notes

- Render automatically assigns a `$PORT` environment variable
- The service will sleep after 15 minutes of inactivity (on free tier)
- First request after sleep may take 30-60 seconds to wake up
- Consider upgrading to a paid plan for always-on service

