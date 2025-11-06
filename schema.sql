-- Voice-Enabled Salon Reservation System
-- Supabase PostgreSQL Schema

-- Create enum type for reservation status
CREATE TYPE reservation_status AS ENUM ('scheduled', 'completed', 'cancelled');

-- Create the salon_reservations table
CREATE TABLE salon_reservations (
    reservation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    stylist_name TEXT NOT NULL,
    service_menu TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    status reservation_status NOT NULL DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index to prevent double-booking
-- Only applies to 'scheduled' status reservations
-- This ensures cancelled/completed appointments don't block the slot
CREATE UNIQUE INDEX idx_unique_stylist_slot 
ON salon_reservations (stylist_name, reservation_date, reservation_time)
WHERE status = 'scheduled';

-- Create indexes for fast lookups
CREATE INDEX idx_phone_number ON salon_reservations (phone_number);
CREATE INDEX idx_reservation_date ON salon_reservations (reservation_date);
CREATE INDEX idx_stylist_date ON salon_reservations (stylist_name, reservation_date);
CREATE INDEX idx_status ON salon_reservations (status);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on record modification
CREATE TRIGGER update_salon_reservations_updated_at
    BEFORE UPDATE ON salon_reservations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE salon_reservations IS 'Stores all salon reservations with one-hour time slots';
COMMENT ON COLUMN salon_reservations.reservation_id IS 'Primary key, UUID generated automatically';
COMMENT ON COLUMN salon_reservations.phone_number IS 'Used for caller identification in voice system';
COMMENT ON COLUMN salon_reservations.status IS 'scheduled: active booking, completed: finished appointment, cancelled: freed slot';
COMMENT ON INDEX idx_unique_stylist_slot IS 'Prevents double-booking: unique constraint on (stylist, date, time) for scheduled status only';
