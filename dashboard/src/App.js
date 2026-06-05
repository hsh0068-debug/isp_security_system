import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

function App() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvents();
    // Refresh every 5 seconds
    const interval = setInterval(fetchEvents, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchEvents = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/login-events');
      setEvents(res.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching events');
      setLoading(false);
    }
  };

  const getActionColor = (action) => {
    if (action === 'allow') return '#02C39A';
    if (action === 'otp') return '#F59E0B';
    if (action === 'restrict') return '#F97316';
    if (action === 'block' || action === 'blocked') return '#EF4444';
    return '#888';
  };

  const getRiskColor = (score) => {
    if (score <= 30) return '#02C39A';
    if (score <= 60) return '#F59E0B';
    if (score <= 80) return '#F97316';
    return '#EF4444';
  };

  const chartData = events.map((e, i) => ({
    name: e.username,
    risk: e.risk_score
  }));

  const totalLogins = events.length;
  const blockedLogins = events.filter(e => e.action_taken === 'block' || e.action_taken === 'blocked').length;
  const safeLogins = events.filter(e => e.action_taken === 'allow').length;
  const highRisk = events.filter(e => e.risk_score > 60).length;

  return (
    <div style={{ background:'#0D1B3E', minHeight:'100vh', color:'white', fontFamily:'Arial, sans-serif' }}>
      
      {/* Header */}
      <div style={{ background:'#1560BD', padding:'20px 30px', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div>
          <h1 style={{ margin:0, fontSize:'22px', color:'#02C39A' }}>🛡️ ISP Security Monitor</h1>
          <p style={{ margin:0, fontSize:'13px', color:'#aaa' }}>AI-Based Network Security System — Live Dashboard</p>
        </div>
        <div style={{ fontSize:'13px', color:'#aaa' }}>
          Auto-refresh: every 5 seconds
        </div>
      </div>

      <div style={{ padding:'24px' }}>

        {/* Stats Cards */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:'16px', marginBottom:'24px' }}>
          {[
            { label:'Total Logins', value:totalLogins, color:'#1560BD' },
            { label:'Safe Logins', value:safeLogins, color:'#02C39A' },
            { label:'High Risk', value:highRisk, color:'#F97316' },
            { label:'Blocked', value:blockedLogins, color:'#EF4444' },
          ].map((card, i) => (
            <div key={i} style={{ background:'#1F3864', borderRadius:'12px', padding:'20px', borderTop:`4px solid ${card.color}` }}>
              <div style={{ fontSize:'13px', color:'#8FA3BF', marginBottom:'8px' }}>{card.label}</div>
              <div style={{ fontSize:'32px', fontWeight:'bold', color:card.color }}>{card.value}</div>
            </div>
          ))}
        </div>

        {/* Chart */}
        <div style={{ background:'#1F3864', borderRadius:'12px', padding:'20px', marginBottom:'24px' }}>
          <h3 style={{ margin:'0 0 16px', color:'#02C39A' }}>Risk Score per Login</h3>
          {events.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2E5596" />
                <XAxis dataKey="name" stroke="#8FA3BF" />
                <YAxis domain={[0,100]} stroke="#8FA3BF" />
                <Tooltip />
                <Bar dataKey="risk" fill="#1560BD" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color:'#8FA3BF' }}>No login data yet</p>
          )}
        </div>

        {/* Login Events Table */}
        <div style={{ background:'#1F3864', borderRadius:'12px', padding:'20px' }}>
          <h3 style={{ margin:'0 0 16px', color:'#02C39A' }}>Live Login Events</h3>
          {loading ? (
            <p style={{ color:'#8FA3BF' }}>Loading...</p>
          ) : events.length === 0 ? (
            <p style={{ color:'#8FA3BF' }}>No login events yet</p>
          ) : (
            <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'13px' }}>
              <thead>
                <tr style={{ color:'#8FA3BF', borderBottom:'1px solid #2E5596' }}>
                  <th style={{ padding:'10px', textAlign:'left' }}>Username</th>
                  <th style={{ padding:'10px', textAlign:'left' }}>Time</th>
                  <th style={{ padding:'10px', textAlign:'left' }}>Location</th>
                  <th style={{ padding:'10px', textAlign:'left' }}>IP Address</th>
                  <th style={{ padding:'10px', textAlign:'left' }}>Risk Score</th>
                  <th style={{ padding:'10px', textAlign:'left' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event, i) => (
                  <tr key={i} style={{ borderBottom:'1px solid #1F3864' }}>
                    <td style={{ padding:'10px', color:'white' }}>{event.username}</td>
                    <td style={{ padding:'10px', color:'#8FA3BF' }}>{new Date(event.login_time).toLocaleString()}</td>
                    <td style={{ padding:'10px', color:'#8FA3BF' }}>{event.location}</td>
                    <td style={{ padding:'10px', color:'#8FA3BF' }}>{event.ip_address}</td>
                    <td style={{ padding:'10px' }}>
                      <span style={{ color:getRiskColor(event.risk_score), fontWeight:'bold' }}>
                        {event.risk_score}/100
                      </span>
                    </td>
                    <td style={{ padding:'10px' }}>
                      <span style={{ background:getActionColor(event.action_taken), color:'white', padding:'3px 10px', borderRadius:'20px', fontSize:'12px', fontWeight:'bold' }}>
                        {event.action_taken.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

      </div>
    </div>
  );
}

export default App;