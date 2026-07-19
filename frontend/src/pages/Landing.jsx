import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { Hexagon, ArrowRight, Menu, X } from "lucide-react";

export default function Landing() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const videoRef = useRef(null);
  const btnRef = useRef(null);

  // Nav shrink on scroll
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Mouse parallax on video
  useEffect(() => {
    const onMove = (e) => {
      if (!videoRef.current) return;
      const x = (e.clientX / window.innerWidth - 0.5) * 20;
      const y = (e.clientY / window.innerHeight - 0.5) * 20;
      videoRef.current.style.transform = `scale(1.08) translate(${-x}px, ${-y}px)`;
    };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  // Magnetic button
  const onBtnMove = (e) => {
    if (!btnRef.current) return;
    const rect = btnRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    btnRef.current.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
  };
  const onBtnLeave = () => {
    if (btnRef.current) btnRef.current.style.transform = "translate(0,0)";
  };

  const words = ["Your", "placement", "prep,"];

  return (
    <section className="relative min-h-screen overflow-hidden bg-[#0a0a1a]">
      {/* Background video with parallax */}
      <video
        ref={videoRef}
        className="absolute inset-0 w-full h-full object-cover z-0 transition-transform duration-300 ease-out"
        style={{ transform: "scale(1.08)" }}
        autoPlay muted loop playsInline
      >
        <source src="/hero-bg.mp4" type="video/mp4" />
        <source src="/hero-bg.webm" type="video/webm" />
      </video>

      {/* Overlays */}
      <div className="absolute inset-0 bg-black/25 z-10 pointer-events-none" />
      <div className="absolute bottom-0 left-0 right-0 h-40 z-10 pointer-events-none"
           style={{ background: "linear-gradient(to top, #0a0a1a, transparent)" }} />

      {/* Content */}
      <div className="relative z-20 flex flex-col min-h-screen">
        {/* Nav */}
        <nav className={`liquid-glass rounded-full max-w-5xl w-[92%] mx-auto mt-6 px-6 py-3 flex items-center justify-between transition-all duration-300 ${scrolled ? "nav-scrolled" : ""}`}>
          <div className="flex items-center gap-2">
            <Hexagon size={22} className="text-white" strokeWidth={1.5} />
            <span className="text-white font-semibold text-lg">PrepPath</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a className="text-white/70 hover:text-white text-sm transition cursor-pointer">Features</a>
            <a className="text-white/70 hover:text-white text-sm transition cursor-pointer">How it works</a>
            <a className="text-white/70 hover:text-white text-sm transition cursor-pointer">Companies</a>
            <a className="text-white/70 hover:text-white text-sm transition cursor-pointer">For Colleges</a>
          </div>
          <div className="hidden md:flex items-center gap-3">
            <Link to="/login" className="text-white/70 hover:text-white text-sm transition">Login</Link>
            <Link to="/register" className="liquid-glass rounded-full px-6 py-2 text-white text-sm hover:scale-95 transition">Get Started</Link>
          </div>
          <button className="md:hidden text-white" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </nav>

        {menuOpen && (
          <div className="md:hidden liquid-glass rounded-2xl max-w-5xl w-[92%] mx-auto mt-2 p-4 flex flex-col gap-3">
            <a className="text-white/70 text-sm">Features</a>
            <a className="text-white/70 text-sm">How it works</a>
            <a className="text-white/70 text-sm">Companies</a>
            <a className="text-white/70 text-sm">For Colleges</a>
            <Link to="/login" className="text-white/70 text-sm">Login</Link>
            <Link to="/register" className="text-white text-sm font-medium">Get Started →</Link>
          </div>
        )}

        {/* Hero */}
        <div className="flex-1 flex flex-col items-center justify-center text-center px-6">
          <p className="fade-up text-xs tracking-[0.3em] text-white/50 uppercase mb-6">
            AI Career Intelligence
          </p>

          <h1 className="font-serif-display text-5xl md:text-6xl lg:text-7xl text-white tracking-tight mb-8 max-w-4xl leading-[1.05]">
            {words.map((w, i) => (
              <span key={i} className="word-mask mr-[0.25em]">
                <span className="word-rise" style={{ animationDelay: `${0.1 + i * 0.12}s` }}>{w}</span>
              </span>
            ))}
            <br />
            <span className="word-mask">
              <span className="word-rise italic gradient-text" style={{ animationDelay: "0.5s" }}>elevated</span>
            </span>
            <span className="word-mask ml-[0.25em]">
              <span className="word-rise" style={{ animationDelay: "0.62s" }}>by</span>
            </span>
            <span className="word-mask ml-[0.25em]">
              <span className="word-rise" style={{ animationDelay: "0.74s" }}>intelligence.</span>
            </span>
          </h1>

          <p className="fade-up delay-3 text-white/70 text-sm md:text-base max-w-xl mx-auto leading-relaxed mb-8">
            One platform that connects your resume gaps to a personalized AI roadmap — powered by a Career Digital Twin that knows exactly where you stand.
          </p>

          <Link
            ref={btnRef}
            to="/register"
            onMouseMove={onBtnMove}
            onMouseLeave={onBtnLeave}
            className="fade-up delay-4 magnetic liquid-glass rounded-full px-8 py-3 text-white text-sm font-medium flex items-center gap-2"
          >
            Get Started free <ArrowRight size={16} />
          </Link>

          <p className="fade-up delay-4 text-white/50 text-xs mt-8">
            2,400+ students &nbsp;·&nbsp; 34% avg readiness lift &nbsp;·&nbsp; 48 companies mapped
          </p>
        </div>

        {/* Scroll indicator */}
        <div className="pb-8 flex justify-center">
          <div className="relative w-16 h-16 flex items-center justify-center">
            <svg className="spin-slow absolute inset-0" viewBox="0 0 100 100">
              <defs>
                <path id="circle" d="M 50,50 m -35,0 a 35,35 0 1,1 70,0 a 35,35 0 1,1 -70,0" />
              </defs>
              <text className="fill-white/50" style={{ fontSize: "9px", letterSpacing: "2px" }}>
                <textPath href="#circle">SCROLL DOWN · SCROLL DOWN · </textPath>
              </text>
            </svg>
            <ArrowRight size={16} className="text-white/60 rotate-90" />
          </div>
        </div>
      </div>
    </section>
  );
}