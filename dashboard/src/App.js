import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import axios from 'axios';

function App() {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({ total:0, safe:0, high_risk:0, blocked:0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [eventsRes, statsRes] = await Promise.all([
        axios.get('http://127.0.0.1:8000/login-events'),
        axios.get('http://127.0.0.1:8000/stats')
      ]);
      setEvents(eventsRes.data);
      setStats(statsRes.data);
      setLoading(false);
    } catch (err) {
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

  const chartData = events.map((e) => ({
    name: e.username,
    risk: e.risk_score
  }));

  return (
    <div style={{ background:'#0D1B3E', minHeight:'100vh', color:'white', fontFamily:'Arial, sans-serif' }}>

      {/* Header */}
      <div style={{ background:'#1560BD', padding:'16px 30px', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div>
          <h1 style={{ margin:0, fontSize:'20px', color:'#02C39A' }}>🛡️ ISP Security Monitor</h1>
          <p style={{ margin:0, fontSize:'12px', color:'#aaa' }}>AI-Based Network Security — Zero Trust Dashboard</p>
        </div>
        <div style={{ fontSize:'12px', color:'#aaa' }}>🔄 Auto-refresh every 5 seconds</div>
      </div>

      <div style={{ padding:'20px' }}>

        {/* Stats */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:'12px', marginBottom:'20px' }}>
          {[
  { label:'Total Logins', value:stats.total, color:'#1560BD', icon:'👤' },
  { label:'Safe Logins', value:stats.safe, color:'#02C39A', icon:'✅' },
  { label:'OTP Required', value:stats.otp || 0, color:'#F59E0B', icon:'🔐' },
  { label:'Blocked', value:stats.blocked, color:'#EF4444', icon:'🚫' },
].map((card, i) => (
  <div key={i} style={{ background:'#1F3864', borderRadius:'10px', padding:'16px', borderTop:`3px solid ${card.color}` }}>
    <div style={{ fontSize:'20px', marginBottom:'4px' }}>{card.icon}</div>
    <div style={{ fontSize:'11px', color:'#8FA3BF', marginBottom:'4px' }}>{card.label}</div>
    <div style={{ fontSize:'28px', fontWeight:'bold', color:card.color }}>{card.value}</div>
  </div>
))}
        </div>

        {/* Chart */}
        <div style={{ background:'#1F3864', borderRadius:'10px', padding:'16px', marginBottom:'20px' }}>
          <h3 style={{ margin:'0 0 12px', color:'#02C39A', fontSize:'14px' }}>📊 Risk Score per Login</h3>
          {events.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2E5596" />
                <XAxis dataKey="name" stroke="#8FA3BF" fontSize={11} />
                <YAxis domain={[0,100]} stroke="#8FA3BF" fontSize={11} />
                <Tooltip contentStyle={{ background:'#1F3864', border:'none', color:'white' }} />
                <Bar dataKey="risk" fill="#1560BD" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color:'#8FA3BF', fontSize:'13px' }}>No login data yet</p>
          )}
        </div>

        {/* Events Table */}
        <div style={{ background:'#1F3864', borderRadius:'10px', padding:'16px' }}>
          <h3 style={{ margin:'0 0 12px', color:'#02C39A', fontSize:'14px' }}>🔴 Live Login Events</h3>
          {loading ? (
            <p style={{ color:'#8FA3BF' }}>Loading...</p>
          ) : events.length === 0 ? (
            <p style={{ color:'#8FA3BF', fontSize:'13px' }}>No login events yet</p>
          ) : (
            <div style={{ overflowX:'auto' }}>
              <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'12px' }}>
                <thead>
                  <tr style={{ color:'#8FA3BF', borderBottom:'1px solid #2E5596' }}>
                    <th style={{ padding:'8px', textAlign:'left' }}>User</th>
                    <th style={{ padding:'8px', textAlign:'left' }}>Time</th>
                    <th style={{ padding:'8px', textAlign:'left' }}>Location</th>
                    <th style={{ padding:'8px', textAlign:'left' }}>IP</th>
                    <th style={{ padding:'8px', textAlign:'left' }}>Risk</th>
                    <th style={{ padding:'8px', textAlign:'left' }}>Action</th>
                    <th style={{ padding:'8px', textAlign:'left' }}>AI Explanation</th>
                  </tr>
                </thead>
                <tbody>
                  {events.slice().reverse().map((event, i) => (
                    <tr key={i} style={{ borderBottom:'1px solid #162844' }}>
                      <td style={{ padding:'8px', color:'white', fontWeight:'500' }}>{event.username}</td>
                      <td style={{ padding:'8px', color:'#8FA3BF' }}>{new Date(event.login_time).toLocaleString()}</td>
                      <td style={{ padding:'8px', color:'#8FA3BF' }}>{event.location}</td>
                      <td style={{ padding:'8px', color:'#8FA3BF' }}>{event.ip_address}</td>
                      <td style={{ padding:'8px' }}>
                        <span style={{ color:getRiskColor(event.risk_score), fontWeight:'bold' }}>
                          {event.risk_score}/100
                        </span>
                      </td>
                      <td style={{ padding:'8px' }}>
                        <span style={{ background:getActionColor(event.action_taken), color:'white', padding:'2px 8px', borderRadius:'20px', fontSize:'11px', fontWeight:'bold' }}>
                          {event.action_taken.toUpperCase()}
                        </span>
                      </td>
                      <td style={{ padding:'8px', color:'#8FA3BF', fontSize:'11px', maxWidth:'300px' }}>
                        {event.explanation || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default App;