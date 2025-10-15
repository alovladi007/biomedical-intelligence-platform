export default function Home() {
  return (
    <div style={{ padding: '40px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#2563eb', marginBottom: '20px' }}>🤰 MYNX NatalCare</h1>
      <p style={{ fontSize: '18px', marginBottom: '30px' }}>
        Maternal Health Monitoring Platform
      </p>

      <div style={{ background: '#f3f4f6', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2 style={{ marginBottom: '15px' }}>Features</h2>
        <ul style={{ lineHeight: '1.8' }}>
          <li>Prenatal Care Tracking</li>
          <li>Appointment Scheduling & Management</li>
          <li>Vital Signs Monitoring</li>
          <li>Risk Assessment & Alerts</li>
          <li>Patient Records Management</li>
        </ul>
      </div>

      <div style={{ background: '#dbeafe', padding: '20px', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '10px' }}>Backend API</h3>
        <p>Backend service running on port 5006</p>
        <p>API Base: <code>http://localhost:5006/api/v1</code></p>
      </div>
    </div>
  );
}
