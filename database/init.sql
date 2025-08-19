-- C4ISR Database Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'operator',
    rank VARCHAR(50),
    unit VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Military devices table
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_type VARCHAR(100) NOT NULL,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    location GEOMETRY(POINT, 4326),
    altitude DECIMAL(10,2),
    heading DECIMAL(5,2),
    speed DECIMAL(8,2),
    battery_level INTEGER,
    signal_strength INTEGER,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Intelligence reports table
CREATE TABLE intelligence_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    threat_level VARCHAR(50) NOT NULL,
    location GEOMETRY(POINT, 4326),
    source VARCHAR(100),
    confidence_level INTEGER CHECK (confidence_level >= 1 AND confidence_level <= 10),
    status VARCHAR(50) DEFAULT 'new',
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Communications table
CREATE TABLE communications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sender_id UUID REFERENCES users(id),
    recipient_id UUID REFERENCES users(id),
    message_type VARCHAR(50) NOT NULL,
    subject VARCHAR(255),
    content TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    status VARCHAR(50) DEFAULT 'sent',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Air support requests table
CREATE TABLE air_support_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requester_id UUID REFERENCES users(id),
    request_type VARCHAR(100) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    location GEOMETRY(POINT, 4326),
    target_description TEXT,
    coordinates VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    assigned_aircraft VARCHAR(100),
    eta TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Battlefield situations table
CREATE TABLE battlefield_situations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location GEOMETRY(POINT, 4326),
    situation_type VARCHAR(100) NOT NULL,
    description TEXT,
    threat_level VARCHAR(50),
    friendly_forces TEXT,
    enemy_forces TEXT,
    civilian_presence BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'active',
    reported_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Device telemetry table
CREATE TABLE device_telemetry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES devices(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    location GEOMETRY(POINT, 4326),
    altitude DECIMAL(10,2),
    heading DECIMAL(5,2),
    speed DECIMAL(8,2),
    battery_level INTEGER,
    signal_strength INTEGER,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    additional_data JSONB
);

-- Create indexes for better performance
CREATE INDEX idx_devices_location ON devices USING GIST (location);
CREATE INDEX idx_devices_device_type ON devices (device_type);
CREATE INDEX idx_devices_status ON devices (status);
CREATE INDEX idx_devices_last_seen ON devices (last_seen);

CREATE INDEX idx_intelligence_reports_location ON intelligence_reports USING GIST (location);
CREATE INDEX idx_intelligence_reports_threat_level ON intelligence_reports (threat_level);
CREATE INDEX idx_intelligence_reports_status ON intelligence_reports (status);

CREATE INDEX idx_air_support_requests_location ON air_support_requests USING GIST (location);
CREATE INDEX idx_air_support_requests_status ON air_support_requests (status);
CREATE INDEX idx_air_support_requests_priority ON air_support_requests (priority);

CREATE INDEX idx_battlefield_situations_location ON battlefield_situations USING GIST (location);
CREATE INDEX idx_battlefield_situations_status ON battlefield_situations (status);

CREATE INDEX idx_device_telemetry_device_id ON device_telemetry (device_id);
CREATE INDEX idx_device_telemetry_timestamp ON device_telemetry (timestamp);
CREATE INDEX idx_device_telemetry_location ON device_telemetry USING GIST (location);

-- Insert sample data
INSERT INTO users (username, email, password_hash, role, rank, unit) VALUES
('admin', 'admin@c4isr.mil', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Gi', 'admin', 'General', 'Command Center'),
('operator1', 'operator1@c4isr.mil', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Gi', 'operator', 'Captain', 'Alpha Company'),
('intel1', 'intel1@c4isr.mil', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Gi', 'intelligence', 'Major', 'Intelligence Unit');

-- Insert sample devices
INSERT INTO devices (device_type, device_id, name, status, location, altitude, heading, speed, battery_level, signal_strength) VALUES
('drone', 'DRONE-001', 'Reconnaissance Drone Alpha', 'active', ST_GeomFromText('POINT(-74.0060 40.7128)', 4326), 150.0, 45.0, 25.0, 85, 95),
('sensor', 'SENSOR-001', 'Ground Sensor Bravo', 'active', ST_GeomFromText('POINT(-74.0065 40.7130)', 4326), 0.0, 0.0, 0.0, 90, 88),
('radar', 'RADAR-001', 'Mobile Radar Charlie', 'active', ST_GeomFromText('POINT(-74.0055 40.7125)', 4326), 10.0, 180.0, 0.0, 75, 92);

-- Insert sample intelligence reports
INSERT INTO intelligence_reports (title, description, threat_level, location, source, confidence_level, status, assigned_to) VALUES
('Enemy Movement Detected', 'Multiple vehicles observed moving north along Route 15', 'high', ST_GeomFromText('POINT(-74.0060 40.7128)', 4326), 'DRONE-001', 8, 'new', (SELECT id FROM users WHERE username = 'intel1')),
('Suspicious Activity', 'Unusual radio traffic detected in sector Bravo', 'medium', ST_GeomFromText('POINT(-74.0065 40.7130)', 4326), 'SENSOR-001', 6, 'investigating', (SELECT id FROM users WHERE username = 'intel1'));

-- Insert sample battlefield situations
INSERT INTO battlefield_situations (location, situation_type, description, threat_level, friendly_forces, enemy_forces, civilian_presence, reported_by) VALUES
(ST_GeomFromText('POINT(-74.0060 40.7128)', 4326), 'engagement', 'Active firefight in progress', 'high', 'Alpha Company, 2nd Platoon', 'Unknown enemy forces', FALSE, (SELECT id FROM users WHERE username = 'operator1')),
(ST_GeomFromText('POINT(-74.0065 40.7130)', 4326), 'observation', 'Enemy forces setting up defensive positions', 'medium', 'Bravo Company', 'Estimated 2-3 squads', TRUE, (SELECT id FROM users WHERE username = 'operator1'));

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_intelligence_reports_updated_at BEFORE UPDATE ON intelligence_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_air_support_requests_updated_at BEFORE UPDATE ON air_support_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_battlefield_situations_updated_at BEFORE UPDATE ON battlefield_situations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
