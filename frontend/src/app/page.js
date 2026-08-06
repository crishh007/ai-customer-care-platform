import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-8rem)]">
      
      {/* Hero Section - Matching the Rig.ai screenshot */}
      <div className="flex-1 bg-[#ff4500] text-[#111] flex flex-col justify-center px-4 sm:px-6 lg:px-8 py-20 relative overflow-hidden -mx-4 sm:-mx-6 lg:-mx-8 -mt-8">
        
        {/* Subtle grid background pattern */}
        <div className="absolute inset-0 opacity-[0.05]" style={{ backgroundImage: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
        
        <main className="flex-1 max-w-6xl mx-auto w-full flex flex-col justify-center px-4 relative z-10 min-h-[calc(100vh-6rem)]">
          <h1 className="text-[#111] text-[120px] leading-[0.85] font-black tracking-tighter mix-blend-color-burn mb-8 uppercase max-w-4xl">
            Autonomous AI<br />
            Support.<br />
            Zero Limits.
          </h1>
          
          <p className="text-[#222] text-xl md:text-2xl max-w-2xl font-medium mb-12 mix-blend-color-burn leading-snug">
            An intelligent multi-agent platform that routes tickets, analyzes sentiment, and predicts churn in real-time. Full CRM integration. Zero human bottlenecks.
          </p>
          
          <div className="flex flex-wrap gap-4">
            <Link href="/register" className="bg-[#111] text-white hover:bg-black px-8 py-4 font-bold transition-colors uppercase tracking-wider text-sm flex items-center gap-3">
              Join Waitlist
            </Link>
            <Link href="/about" className="border-2 border-[#111] text-[#111] hover:bg-[#111] hover:text-white px-8 py-4 font-bold transition-all uppercase tracking-wider text-sm">
              Our Approach
            </Link>
          </div>
        </main>
      </div>

      {/* Scrolling Ticker Banner */}
      <div className="bg-[#ff4500] border-t border-[#111]/10 py-3 overflow-hidden whitespace-nowrap -mx-4 sm:-mx-6 lg:-mx-8">
        <div className="animate-[scroll_20s_linear_infinite] inline-block font-mono text-[10px] uppercase tracking-widest text-[#111] font-bold">
          <span className="mx-8">• YOUR HARDWARE, YOUR RULES</span>
          <span className="mx-8">• NO TOKENS, NO LIMITS</span>
          <span className="mx-8">• SPECIALIZED SLM</span>
          <span className="mx-8">• UNBOUNDED CONTEXT</span>
          <span className="mx-8">• ZERO TELEMETRY</span>
          <span className="mx-8">• YOUR HARDWARE, YOUR RULES</span>
          <span className="mx-8">• NO TOKENS, NO LIMITS</span>
          <span className="mx-8">• SPECIALIZED SLM</span>
          <span className="mx-8">• UNBOUNDED CONTEXT</span>
          <span className="mx-8">• ZERO TELEMETRY</span>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
      `}} />
    </div>
  );
}
