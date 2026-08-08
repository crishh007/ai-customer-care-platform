"use client";
import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/store';
import { useRouter } from 'next/navigation';

export default function Tickets() {
  const { isAuthenticated, token } = useAuthStore();
  const router = useRouter();
  const [tickets, setTickets] = useState([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newTicket, setNewTicket] = useState({ title: '', description: '', priority: 'Medium' });

  const fetchTickets = async () => {
    try {
      const user_id = useAuthStore.getState().user?.email || "anonymous";
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/tickets/list/${user_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        const formattedTickets = data.map(t => ({
          id: t.ticket_id,
          title: t.subject,
          status: t.status,
          priority: t.priority,
          customer_name: t.user_id
        }));
        setTickets(formattedTickets);
      }
    } catch (error) {
      console.error("Failed to fetch tickets", error);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchTickets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, router]);

  const handleCreateTicket = async (e) => {
    e.preventDefault();
    try {
      const user_id = useAuthStore.getState().user?.email || "anonymous";
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/tickets/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: user_id,
          subject: newTicket.title,
          description: newTicket.description,
          priority: newTicket.priority
        })
      });
      
      if (res.ok) {
        setNewTicket({ title: '', description: '', priority: 'Medium' });
        setIsCreateModalOpen(false);
        fetchTickets();
      }
    } catch (error) {
      console.error("Failed to create ticket", error);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto mt-8">
      <div className="flex justify-between items-end border-b border-white/10 pb-6">
        <div>
          <h2 className="text-[#ff4500] font-mono text-[10px] uppercase tracking-[0.2em] mb-2">Escalation Queue</h2>
          <h1 className="text-4xl font-bold tracking-tight">Active Tickets</h1>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn-primary"
        >
          [+] Initialize Ticket
        </button>
      </div>

      <div className="tech-card p-0">
        <div className="overflow-x-auto">
          <table className="tech-table">
            <thead>
              <tr>
                <th className="w-24">ID</th>
                <th>Title</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Customer Name</th>
              </tr>
            </thead>
            <tbody>
              {tickets.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center py-8 text-gray-500 font-mono">
                    {">"} NO_ACTIVE_TICKETS_FOUND
                  </td>
                </tr>
              ) : (
                tickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td className="font-mono text-gray-500">#{ticket.id?.toString().substring(0,6) || "---"}</td>
                    <td className="font-medium text-white">{ticket.title}</td>
                    <td>
                      <span className={`px-2 py-1 text-[10px] uppercase tracking-wider font-bold ${
                        ticket.status === 'Open' ? 'text-[#ff4500]' : 
                        ticket.status === 'Resolved' ? 'text-green-500' : 'text-yellow-500'
                      }`}>
                        {ticket.status}
                      </span>
                    </td>
                    <td>
                      <span className={`px-2 py-1 text-[10px] uppercase tracking-wider font-bold ${
                        ticket.priority === 'High' ? 'text-red-500' : 
                        ticket.priority === 'Medium' ? 'text-yellow-500' : 'text-gray-400'
                      }`}>
                        {ticket.priority}
                      </span>
                    </td>
                    <td className="text-gray-400">{ticket.customer_name}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-[#0a0a0a]/90 flex items-center justify-center z-50 p-4">
          <div className="tech-card w-full max-w-md p-8 animate-fade-in border-[#ff4500]">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold font-mono text-white">
                <span className="text-[#ff4500]">λ</span> INITIALIZE_TICKET
              </h2>
              <button 
                onClick={() => setIsCreateModalOpen(false)}
                className="text-gray-500 hover:text-[#ff4500] font-mono text-xl"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleCreateTicket} className="space-y-4">
              <div>
                <label className="block text-[10px] font-mono text-[#ff4500] mb-2 uppercase tracking-widest">Title</label>
                <input
                  type="text"
                  required
                  value={newTicket.title}
                  onChange={(e) => setNewTicket({...newTicket, title: e.target.value})}
                  className="input-field"
                  placeholder="Error log..."
                />
              </div>
              
              <div>
                <label className="block text-[10px] font-mono text-[#ff4500] mb-2 uppercase tracking-widest">Description</label>
                <textarea
                  required
                  value={newTicket.description}
                  onChange={(e) => setNewTicket({...newTicket, description: e.target.value})}
                  className="input-field h-32 resize-none"
                  placeholder="Detailed output..."
                />
              </div>

              <div>
                <label className="block text-[10px] font-mono text-[#ff4500] mb-2 uppercase tracking-widest">Priority</label>
                <select
                  value={newTicket.priority}
                  onChange={(e) => setNewTicket({...newTicket, priority: e.target.value})}
                  className="input-field appearance-none cursor-pointer"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>

              <div className="pt-4 flex gap-4">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="flex-1 btn-outline"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 btn-primary"
                >
                  Execute
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
