import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ComposableMap, Geographies, Geography, Marker } from 'react-simple-maps';
import axios from 'axios';

const GEO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

const LOCATION_COORDS = {
  "Sri Lanka": [80.7718, 7.8731],
  "Russia": [105.3188, 61.5240],
  "China": [104.1954, 35.8617],
  "United States": [-95.7129, 37.0902],
  "India": [78.9629, 20.5937],
  "Unknown": [0, 0],
  "North Korea": [127.5101, 40.3399],
};

function App() {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({ total:0, safe:0, high_risk:0, blocked:0, otp:0 });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('events');
  const [alerts, setAlerts] = useState([]);

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
      const newEvents = eventsRes.data;
      setEvents(newEvents);
      setStats(statsRes.data);
      const highRiskEvents = newEvents.filter(e =>
        e.risk_score > 60 || e.action_taken === 'blocked'
      );
      setAlerts(highRiskEvents.slice(-3).reverse());
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

  const mapMarkers = events.map(e => {
    const country = e.location ? e.location.split(', ').pop() : 'Unknown';
    const coords = LOCATION_COORDS[country] || [0, 0];
    return {
      coords,
      username: e.username,
      action: e.action_taken,
      risk: e.risk_score,
      location: e.location
    };
  }).filter(m => m.coords[0] !== 0);

  return (
    <div style={{ background:'#0D1B3E', minHeight:'100vh', color:'white', fontFamily:'Arial, sans-serif' }}>

      <div style={{ background:'#1560BD', padding:'14px 24px', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div>
          <h1 style={{ margin:0, fontSize:'18px', color:'#02C39A' }}>ISP Security Monitor</h1>
          <p style={{ margin:0, fontSize:'11px', color:'#aaa' }}>AI-Based Network Security — Zero Trust Architecture</p>
        </div>
        <div style={{ fontSize:'11px', color:'#aaa' }}>Live — refreshes every 5 seconds</div>
      </div>

      <div style={{ padding:'16px' }}>

        {alerts.length > 0 && (
          <div style={{ marginBottom:'16px' }}>
            {alerts.map((alert, i) => (
              <div key={i} style={{
                background:'#7B0D1E',
                border:'1px solid #EF4444',
                borderRadius:'8px',
                padding:'10px 16px',
                marginBottom:'6px',
                display:'flex',
                alignItems:'center',
                gap:'10px'
              }}>
                <span style={{ fontSize:'18px' }}>ALERT</span>
                <div>
                  <div style={{ fontSize:'12px', fontWeight:'bold', color:'#EF4444' }}>
                    SECURITY ALERT — {alert.action_taken.toUpperCase()}
                  </div>
                  <div style={{ fontSize:'11px', color:'#ffaaaa' }}>
                    User: {alert.username} | Location: {alert.location} | Risk: {alert.risk_score}/100 | {new Date(alert.login_time).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:'10px', marginBottom:'16px' }}>
          {[
            { label:'Total', value:stats.total, color:'#1560BD', icon:'U' },
            { label:'Safe', value:stats.safe, color:'#02C39A', icon:'S' },
            { label:'OTP Sent', value:stats.otp||0, color:'#F59E0B', icon:'O' },
            { label:'High Risk', value:stats.high_risk, color:'#F97316', icon:'!' },
            { label:'Blocked', value:stats.blocked, color:'#EF4444', icon:'X' },
          ].map((card, i) => (
            <div key={i} style={{ background:'#1F3864', borderRadius:'8px', padding:'12px', borderTop:`3px solid ${card.color}` }}>
              <div style={{ fontSize:'18px', marginBottom:'2px', color:card.color }}>{card.icon}</div>
              <div style={{ fontSize:'10px', color:'#8FA3BF', marginBottom:'2px' }}>{card.label}</div>
              <div style={{ fontSize:'24px', fontWeight:'bold', color:card.color }}>{card.value}</div>
            </div>
          ))}
        </div>

        <div style={{ display:'flex', gap:'8px', marginBottom:'16px' }}>
          {['events', 'chart', 'map'].map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              style={{ padding:'7px 16px', borderRadius:'8px', border:'none', cursor:'pointer', fontSize:'12px', fontWeight:'500',
                background: activeTab===tab ? '#1560BD' : '#1F3864',
                color: activeTab===tab ? 'white' : '#8FA3BF' }}>
              {tab === 'events' ? 'Live Events' : tab === 'chart' ? 'Risk Chart' : 'Login Map'}
            </button>
          ))}
        </div>

        {activeTab === 'events' && (
          <div style={{ background:'#1F3864', borderRadius:'10px', padding:'16px' }}>
            <h3 style={{ margin:'0 0 12px', color:'#02C39A', fontSize:'13px' }}>Live Login Events</h3>
            {loading ? <p style={{ color:'#8FA3BF' }}>Loading...</p> :
             events.length === 0 ? <p style={{ color:'#8FA3BF', fontSize:'13px' }}>No events yet</p> : (
              <div style={{ overflowX:'auto' }}>
                <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'11px' }}>
                  <thead>
                    <tr style={{ color:'#8FA3BF', borderBottom:'1px solid #2E5596' }}>
                      {['User','Time','Location','IP','Risk','Action','AI Explanation'].map(h => (
                        <th key={h} style={{ padding:'8px', textAlign:'left' }}>{h}</th>
                      ))}
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
                          <span style={{ color:getRiskColor(event.risk_score), fontWeight:'bold' }}>{event.risk_score}/100</span>
                        </td>
                        <td style={{ padding:'8px' }}>
                          <span style={{ background:getActionColor(event.action_taken), color:'white', padding:'2px 8px', borderRadius:'20px', fontSize:'10px', fontWeight:'bold' }}>
                            {event.action_taken.toUpperCase()}
                          </span>
                        </td>
                        <td style={{ padding:'8px', color:'#8FA3BF', fontSize:'10px', maxWidth:'250px' }}>{event.explanation||'-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'chart' && (
          <div style={{ background:'#1F3864', borderRadius:'10px', padding:'16px' }}>
            <h3 style={{ margin:'0 0 12px', color:'#02C39A', fontSize:'13px' }}>Risk Score per Login</h3>
            {events.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2E5596" />
                  <XAxis dataKey="name" stroke="#8FA3BF" fontSize={11} />
                  <YAxis domain={[0,100]} stroke="#8FA3BF" fontSize={11} />
                  <Tooltip contentStyle={{ background:'#1F3864', border:'none', color:'white' }} />
                  <Bar dataKey="risk" fill="#1560BD" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <p style={{ color:'#8FA3BF' }}>No data yet</p>}
          </div>
        )}

        {activeTab === 'map' && (
          <div style={{ background:'#1F3864', borderRadius:'10px', padding:'16px' }}>
            <h3 style={{ margin:'0 0 12px', color:'#02C39A', fontSize:'13px' }}>Login Location Map</h3>
            <ComposableMap style={{ background:'#0D1B3E', borderRadius:'8px' }}>
              <Geographies geography={GEO_URL}>
                {({ geographies }) =>
                  geographies.map(geo => (
                    <Geography key={geo.rsmKey} geography={geo}
                      fill="#1F3864" stroke="#2E5596" strokeWidth={0.5} />
                  ))
                }
              </Geographies>
              {mapMarkers.map((marker, i) => (
                <Marker key={i} coordinates={marker.coords}>
                  <circle r={6} fill={getActionColor(marker.action)}
                    stroke="white" strokeWidth={1} opacity={0.8} />
                  <text textAnchor="middle" y={-10} style={{ fontSize:'8px', fill:'white' }}>
                    {marker.username}
                  </text>
                </Marker>
              ))}
            </ComposableMap>
            <div style={{ display:'flex', gap:'16px', marginTop:'12px', fontSize:'11px' }}>
              {[['#02C39A','Safe'],['#F59E0B','OTP'],['#F97316','Restricted'],['#EF4444','Blocked']].map(([color,label]) => (
                <div key={label} style={{ display:'flex', alignItems:'center', gap:'4px' }}>
                  <div style={{ width:'10px', height:'10px', borderRadius:'50%', background:color }}></div>
                  <span style={{ color:'#8FA3BF' }}>{label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;