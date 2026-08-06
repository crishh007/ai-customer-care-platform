"use client";
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { fetchApi } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Users, TicketCheck, Zap } from 'lucide-react';

export default function Dashboard() {
  const { isAuthenticated, user } = useAuthStore();
  const router = useRouter();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [churnData, setChurnData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const loadData = async () => {
      try {
        const [dash, sent, churn] = await Promise.all([
          fetchApi('/analytics/dashboard'),
          fetchApi('/analytics/sentiment'),
          fetchApi('/analytics/churn')
        ]);
        setDashboardData(dash);
        setSentimentData(sent);
        setChurnData(churn);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isAuthenticated, router]);

  if (loading) {
    return <div className="flex justify-center items-center h-[calc(100vh-8rem)]">Loading...</div>;
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto">
      <div className="flex justify-between items-end border-b border-white/10 pb-6">
        <div>
          <h2 className="text-[#ff4500] font-mono text-[10px] uppercase tracking-[0.2em] mb-2">Telemetry Module</h2>
          <h1 className="text-4xl font-bold tracking-tight">System Overview</h1>
        </div>
      </div>

      {/* KPI Cards - Rig Bento Style */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/10 border border-white/10">
        
        <div className="tech-card border-none bg-[#0a0a0a]">
          <div className="flex justify-between items-start">
            <span className="tech-label">Live Channels</span>
            <span className="font-mono text-[10px] text-gray-600">001</span>
          </div>
          <h3 className="text-2xl font-bold mt-2">Active Conversations</h3>
          <p className="text-gray-400 text-sm mt-4 leading-relaxed h-12">
            Real-time tracking of active socket connections and ongoing AI threads without external dependency.
          </p>
          <div className="mt-8 font-mono text-5xl text-[#ff4500] font-bold">
            {dashboardData?.active_conversations || 0}
          </div>
        </div>
        
        <div className="tech-card border-none bg-[#0a0a0a]">
          <div className="flex justify-between items-start">
            <span className="tech-label">Satisfaction</span>
            <span className="font-mono text-[10px] text-gray-600">002</span>
          </div>
          <h3 className="text-2xl font-bold mt-2">CSAT Metrics</h3>
          <p className="text-gray-400 text-sm mt-4 leading-relaxed h-12">
            Automated polling of user satisfaction on resolved threads. Computed locally, zero telemetry.
          </p>
          <div className="mt-8 font-mono text-5xl text-white font-bold">
            {dashboardData?.csat_score || 0}%
          </div>
        </div>

        <div className="tech-card border-none bg-[#0a0a0a]">
          <div className="flex justify-between items-start">
            <span className="tech-label">Workload</span>
            <span className="font-mono text-[10px] text-gray-600">003</span>
          </div>
          <h3 className="text-2xl font-bold mt-2">Total Tickets</h3>
          <p className="text-gray-400 text-sm mt-4 leading-relaxed h-12">
            Cumulative volume of support tickets processed by the local SLM cluster.
          </p>
          <div className="mt-8 font-mono text-5xl text-white font-bold">
            {dashboardData?.ticket_count || 0}
          </div>
        </div>

        <div className="tech-card border-none bg-[#0a0a0a]">
          <div className="flex justify-between items-start">
            <span className="tech-label">Efficiency</span>
            <span className="font-mono text-[10px] text-gray-600">004</span>
          </div>
          <h3 className="text-2xl font-bold mt-2">Automation Rate</h3>
          <p className="text-gray-400 text-sm mt-4 leading-relaxed h-12">
            Percentage of tickets resolved entirely by AI agents without human escalation.
          </p>
          <div className="mt-8 font-mono text-5xl text-white font-bold">
            {dashboardData?.automation_rate || 0}%
          </div>
        </div>
      </div>

      {/* Charts & Analytics - Technical Style */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Predictive Churn Box */}
        <div className="lg:col-span-1 tech-card flex flex-col border-[#ff4500]/50 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#ff4500] to-transparent"></div>
          <div className="flex justify-between border-b border-white/10 pb-4 mb-6">
            <h3 className="font-mono text-xs uppercase tracking-widest text-[#ff4500]">Predictive Churn</h3>
            <span className="text-gray-500 font-mono text-xs">AI_MODEL: LLaMA3</span>
          </div>
          
          <div className="flex-1 flex flex-col items-center justify-center py-4">
            <div className="relative flex items-center justify-center">
              <svg className="w-32 h-32 transform -rotate-90">
                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-[#222]" />
                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="transparent" 
                  strokeDasharray="351.8" 
                  strokeDashoffset={351.8 - (351.8 * (churnData?.risk_score || 0)) / 100}
                  className="text-[#ff4500] transition-all duration-1000 ease-out" 
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="text-3xl font-bold font-mono">{churnData?.risk_score || 0}%</span>
              </div>
            </div>
          </div>
          
          <div className="mt-4 bg-[#111] p-4 border border-white/5">
            <p className="font-mono text-xs text-gray-400">
              <span className="text-[#ff4500]">{"{ reason: "}</span>
              &quot;{churnData?.reason || 'Awaiting telemetry...'}&quot;
              <span className="text-[#ff4500]">{" }"}</span>
            </p>
          </div>
        </div>

        <div className="lg:col-span-2 tech-card min-h-[400px]">
          <div className="flex justify-between border-b border-white/10 pb-4 mb-6">
            <h3 className="font-mono text-xs uppercase tracking-widest text-gray-400">Sentiment Timeseries</h3>
            <span className="text-[#ff4500] font-mono text-xs flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#ff4500] animate-pulse"></span>
              LIVE
            </span>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sentimentData?.trend || []} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                <XAxis dataKey="date" stroke="#666" tick={{fontFamily: 'monospace', fontSize: 10}} axisLine={false} tickLine={false} />
                <YAxis stroke="#666" domain={[0, 1]} tick={{fontFamily: 'monospace', fontSize: 10}} axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0a0a0a', border: '1px solid #333', borderRadius: '0', fontFamily: 'monospace', fontSize: '12px' }}
                  itemStyle={{ color: '#ff4500' }}
                />
                <Line type="step" dataKey="score" stroke="#ff4500" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: '#ff4500' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="tech-card flex flex-col">
          <h3 className="font-mono text-xs uppercase tracking-widest text-gray-400 border-b border-white/10 pb-4 mb-6">Distribution</h3>
          <div className="flex-1 flex flex-col justify-center space-y-8 font-mono">
            <div>
              <div className="flex justify-between mb-2 text-xs">
                <span className="text-gray-400">POS_SENT</span>
                <span className="text-white">{sentimentData?.positive || 0}%</span>
              </div>
              <div className="w-full bg-[#222] h-1">
                <div className="bg-white h-1" style={{ width: `${sentimentData?.positive || 0}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2 text-xs">
                <span className="text-gray-400">NEU_SENT</span>
                <span className="text-white">{sentimentData?.neutral || 0}%</span>
              </div>
              <div className="w-full bg-[#222] h-1">
                <div className="bg-gray-500 h-1" style={{ width: `${sentimentData?.neutral || 0}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2 text-xs">
                <span className="text-[#ff4500]">NEG_SENT</span>
                <span className="text-[#ff4500]">{sentimentData?.negative || 0}%</span>
              </div>
              <div className="w-full bg-[#222] h-1">
                <div className="bg-[#ff4500] h-1" style={{ width: `${sentimentData?.negative || 0}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
