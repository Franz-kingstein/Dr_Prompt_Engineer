import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import './index.css';

// --- Constants ---
const BACKEND_URL = "/generate";

// --- Components ---

const NotFoundView = ({ onBack }) => (
  <div className="relative h-screen w-full flex flex-col items-center justify-center p-6 select-none bg-background text-on-surface font-body overflow-hidden">
    {/* Top Navigation Anchor */}
    <header className="fixed top-0 w-full z-50 flex justify-between items-center px-6 py-4 bg-surface-dim">
      <div className="text-xl font-black tracking-tighter text-on-surface uppercase font-headline">
        True <span className="text-primary">Obsidian</span>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-on-surface-variant text-xs uppercase tracking-widest font-semibold">System Status: Offline</span>
      </div>
    </header>

    {/* Background Atmospheric Elements */}
    <div className="absolute inset-0 z-0 opacity-20 overflow-hidden pointer-events-none">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary rounded-full blur-[160px]"></div>
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-tertiary rounded-full blur-[140px]"></div>
    </div>

    {/* 404 Canvas Content */}
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="z-10 flex flex-col items-center text-center max-w-2xl"
    >
      {/* Thematic Icon: Broken Satellite */}
      <div className="relative mb-12 floating-entity flex items-center justify-center">
        <div className="relative w-48 h-48 bg-surface-container-high rounded-full flex items-center justify-center shadow-[inset_4px_4px_10px_#000,inset_-2px_-2px_10px_#2c2c2c]">
          <span className="material-symbols-outlined text-[120px] text-primary" style={{ fontVariationSettings: "'FILL' 0" }}>satellite_alt</span>
        </div>
        <div className="absolute -top-4 -right-4 w-12 h-12 bg-surface-container-highest rounded-lg flex items-center justify-center shadow-lg transform rotate-12">
          <span className="material-symbols-outlined text-on-surface-variant text-2xl">hardware</span>
        </div>
        <div className="absolute bottom-2 -left-8 w-14 h-14 bg-surface-container rounded-full flex items-center justify-center shadow-md transform -rotate-12">
          <span className="material-symbols-outlined text-primary-dim text-2xl">warning</span>
        </div>
      </div>

      <div className="space-y-4 mb-10">
        <h1 className="text-on-surface-variant font-headline text-sm font-bold uppercase tracking-[0.4em]">Error Code: 404</h1>
        <h2 className="text-on-surface font-headline text-5xl md:text-7xl font-black tracking-tighter leading-none">
          Lost in <span className="text-primary">Space</span>
        </h2>
        <p className="text-on-surface-variant text-base md:text-lg max-w-md mx-auto leading-relaxed">
          The prompt you're looking for has drifted beyond the event horizon. We've reached The Dead End of our current coordinates.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-6">
        <button onClick={onBack} className="neumorphic-convex group relative px-8 py-4 rounded-xl flex items-center gap-3 transition-all duration-300 nm-button-active">
          <span className="material-symbols-outlined text-on-primary-container group-hover:rotate-12 transition-transform" style={{ fontVariationSettings: "'FILL' 1" }}>rocket_launch</span>
          <span className="font-headline font-extrabold uppercase tracking-wider text-on-primary-container text-sm">Recall to Base</span>
        </button>
        <button onClick={onBack} className="px-6 py-4 rounded-xl text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all text-sm font-semibold uppercase tracking-widest flex items-center gap-2">
          <span className="material-symbols-outlined text-lg">support_agent</span>
          Contact Mission Control
        </button>
      </div>
    </motion.div>

    {/* Data Stream Grids */}
    <div className="absolute bottom-12 left-12 hidden lg:block opacity-40">
      <div className="obsidian-glass p-4 rounded-xl space-y-2 w-48 shadow-2xl">
        <div className="flex justify-between items-center">
          <span className="text-[0.6rem] text-on-surface-variant uppercase font-bold">Signal</span>
          <span className="text-[0.6rem] text-error font-bold">LOST</span>
        </div>
        <div className="h-1 w-full bg-surface-container-lowest rounded-full overflow-hidden">
          <div className="h-full bg-error w-1/12"></div>
        </div>
        <div className="text-[0.5rem] text-on-surface-variant font-mono">COORD: 0.00.404.NULL</div>
      </div>
    </div>

    <div className="absolute top-24 right-12 hidden lg:block opacity-40">
      <div className="obsidian-glass p-4 rounded-xl space-y-2 w-48 shadow-2xl">
        <div className="flex justify-between items-center">
          <span className="text-[0.6rem] text-on-surface-variant uppercase font-bold">Atmosphere</span>
          <span className="text-[0.6rem] text-primary font-bold">OBSIDIAN</span>
        </div>
        <div className="h-1 w-full bg-surface-container-lowest rounded-full overflow-hidden">
          <div className="h-full bg-primary w-full opacity-50"></div>
        </div>
        <div className="text-[0.5rem] text-on-surface-variant font-mono">SECTOR: DARK_VOID</div>
      </div>
    </div>

    {/* Side Decoration */}
    <aside className="fixed left-0 top-0 h-full w-20 flex flex-col items-center py-8 z-40 bg-surface-container-low hidden md:flex">
      <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center mb-12 shadow-[inset_2px_2px_4px_#000]">
        <span className="material-symbols-outlined text-on-surface-variant text-xl">radar</span>
      </div>
      <div className="flex-1 flex flex-col gap-8 opacity-20">
        <span className="material-symbols-outlined">code</span>
        <span className="material-symbols-outlined">image</span>
        <span className="material-symbols-outlined">description</span>
      </div>
      <div className="w-10 h-10 rounded-full bg-surface-container-high flex items-center justify-center mt-auto shadow-lg">
        <span className="material-symbols-outlined text-primary text-xl">help_center</span>
      </div>
    </aside>
  </div>
);

const ConstructionModal = ({ onClose }) => (
  <div className="fixed inset-0 z-[120] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm transition-all duration-300">
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.8, opacity: 0 }}
      className="bg-surface-container-high neumorphic-extruded border border-primary/30 rounded-3xl p-8 max-w-xs w-full text-center relative"
    >
      <div className="mb-6 flex justify-center">
        <div className="w-16 h-16 bg-surface-container-highest rounded-full flex items-center justify-center shadow-lg border border-primary/20">
          <span className="material-symbols-outlined text-primary text-3xl animate-bounce">construction</span>
        </div>
      </div>
      <h3 className="text-xl font-black text-on-surface uppercase tracking-tighter mb-2">Feature Locked</h3>
      <p className="text-on-surface-variant text-xs mb-8 leading-relaxed font-medium uppercase tracking-widest opacity-70">
        This module is currently under deep neural construction.
      </p>
      <button
        onClick={onClose}
        className="w-full py-3 bg-surface-container-lowest text-primary font-black uppercase tracking-widest text-[10px] rounded-xl hover:bg-surface-container-low transition-all active:scale-95 nm-inset"
      >
        Acknowledged
      </button>
    </motion.div>
  </div>
);

const LoadingScreen = () => (
  <main className="fixed inset-0 z-[100] bg-surface flex flex-col items-center justify-center p-6 transition-opacity duration-500">
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary-container opacity-[0.03] blur-[120px] rounded-full"></div>
    </div>

    <div className="relative flex items-center justify-center w-64 h-64 mb-16">
      <div className="absolute inset-0 rounded-full bg-surface-container-low neumorphic-extruded border border-white/[0.02]"></div>
      <div className="absolute inset-4 rounded-full border-t-2 border-l-2 border-primary-fixed-dim/40 animate-spin-slow"></div>
      <div className="absolute inset-8 rounded-full border-b-2 border-r-2 border-primary-fixed-dim/20 animate-spin-reverse"></div>
      <div className="relative w-32 h-32 rounded-full bg-surface-container-high neumorphic-inset flex items-center justify-center glow-orange overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-tr from-primary-fixed-dim/10 to-transparent animate-pulse-ring"></div>
        <span className="material-symbols-outlined text-primary text-5xl z-10" style={{ fontVariationSettings: "'FILL' 1" }}>memory</span>
      </div>
      <div className="absolute inset-0 animate-spin-slow">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-primary rounded-full glow-orange"></div>
      </div>
    </div>

    <div className="text-center space-y-4 max-w-md z-10">
      <h1 className="text-xl font-black tracking-tighter text-primary uppercase font-headline">
        Dr. Prompt
      </h1>
      <div className="flex flex-col items-center gap-2">
        <div className="flex items-center gap-3">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
          <p className="text-on-surface-variant font-medium tracking-wide text-sm leading-relaxed">
            Syncing Neural Layers
          </p>
        </div>
        <div className="w-48 h-1 bg-surface-container-lowest rounded-full mt-4 overflow-hidden neumorphic-inset relative">
          <div className="h-full bg-gradient-to-r from-primary-fixed-dim to-primary rounded-full glow-orange animate-progress-scan"></div>
        </div>
      </div>
    </div>

    <div className="absolute bottom-12 left-0 w-full flex flex-col items-center gap-2 px-8">
      <div className="flex items-center gap-4 text-[0.6875rem] font-medium uppercase tracking-[0.2em] text-on-surface-variant/40">
        <span>V1.0-Obsidian</span>
        <span className="w-1 h-1 bg-white/10 rounded-full"></span>
        <span>Secure Tunnel Active</span>
      </div>
      <div className="mt-8 flex gap-6">
        <div className="px-4 py-2 rounded-xl bg-surface-container-low neumorphic-extruded flex items-center gap-2">
          <span className="material-symbols-outlined text-on-surface-variant text-sm">terminal</span>
          <span className="text-[0.625rem] text-on-surface-variant font-bold">Verifying Guardrails...</span>
        </div>
      </div>
    </div>
  </main>
);

const ConnectionErrorPopup = ({ onRetry, onSupport }) => (
  <div className="fixed inset-0 z-[110] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm transition-all duration-300">
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="bg-surface-container-low neumorphic-extruded border border-primary/20 rounded-[2.5rem] p-10 max-w-md w-full text-center relative overflow-hidden"
    >
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/50 to-transparent"></div>

      <div className="mb-8 flex justify-center">
        <div className="w-20 h-20 bg-surface-container-high rounded-full flex items-center justify-center shadow-xl border border-white/5 relative">
          <span className="material-symbols-outlined text-error text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>warning</span>
          <div className="absolute inset-0 rounded-full border border-error/20 animate-pulse"></div>
        </div>
      </div>

      <h2 className="text-3xl font-black text-on-surface uppercase tracking-tighter mb-4 italic">
        Connection Severed
      </h2>

      <p className="text-on-surface-variant text-sm mb-8 leading-relaxed">
        The engine is currently offline. <span className="text-primary font-bold">Retrying in 5 seconds...</span>
      </p>

      <div className="space-y-4">
        <button
          onClick={onRetry}
          className="w-full py-4 bg-primary text-on-primary font-black uppercase tracking-widest text-sm rounded-2xl glow-orange hover:bg-primary-dim transition-all active:scale-95 nm-convex"
        >
          Retry Connection
        </button>
        <button
          onClick={onSupport}
          className="w-full py-4 bg-surface-container-high text-on-surface-variant font-bold uppercase tracking-widest text-xs rounded-2xl hover:text-on-surface transition-all active:scale-95 nm-inset"
        >
          Contact Support
        </button>
      </div>

      <div className="mt-8 text-[10px] text-on-surface-variant/30 font-mono tracking-widest">
        ERR_CODE: PULSE_TIMEOUT_0x99
      </div>
    </motion.div>
  </div>
);


const PromptRefiner = ({ onRefine, prevPrompt, color }) => {
  const [refinement, setRefinement] = useState('');
  const [show, setShow] = useState(false);

  if (!show) {
    return (
      <button
        onClick={() => setShow(true)}
        className={`flex items-center gap-2 text-[10px] font-bold text-on-surface-variant hover:text-primary transition-all uppercase tracking-widest bg-surface-container-high px-4 py-2 rounded-lg nm-flat hover:nm-convex`}
      >
        <span className="material-symbols-outlined text-sm">auto_fix_high</span>
        Fine-tune
      </button>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6 p-6 bg-surface-container rounded-3xl border border-primary/10 space-y-4 nm-inset"
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="material-symbols-outlined text-primary text-sm">edit_note</span>
        <span className="text-[10px] font-black text-primary uppercase tracking-widest">Correction Input</span>
      </div>
      <textarea
        value={refinement}
        onChange={(e) => setRefinement(e.target.value)}
        placeholder="How should we adjust this? e.g., 'Make it more cinematic' or 'Focus more on the architecture'."
        className="w-full bg-surface-container-lowest border border-white/[0.05] rounded-2xl p-4 text-sm text-on-surface placeholder:text-on-surface-variant/20 focus:outline-none focus:ring-1 focus:ring-primary/30 min-h-[100px] resize-none font-body"
      />
      <div className="flex justify-end gap-3">
        <button
          onClick={() => setShow(false)}
          className="px-4 py-2 text-[10px] font-bold text-on-surface-variant uppercase tracking-widest hover:text-on-surface transition-colors"
        >
          Discard
        </button>
        <button
          onClick={() => { onRefine(refinement, prevPrompt); setShow(false); setRefinement(''); }}
          disabled={!refinement.trim()}
          className={`px-6 py-2 bg-on-surface text-background text-[10px] font-black uppercase tracking-widest rounded-xl shadow-lg disabled:opacity-20 transition-all hover:scale-105 active:scale-95`}
        >
          Redo Prompt
        </button>
      </div>
    </motion.div>
  );
};


const App = () => {
  const [view, setView] = useState('workshop'); // workshop | 404
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showError, setShowError] = useState(false);
  const [showConstruction, setShowConstruction] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true); // Startup loading state
  const [copiedId, setCopiedId] = useState(null);
  const [activeTask, setActiveTask] = useState('code'); // code | image | document
  const [formatType, setFormatType] = useState('structured'); // structured | json
  const [statusNote, setStatusNote] = useState(''); // Live backend feedback
  const [layoutView, setLayoutView] = useState('list'); // grid | list
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Simulate Neural Sync/Initial Loading Sequence
    const timer = setTimeout(() => {
      setIsInitialLoading(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);
  const [messages, setMessages] = useState([]);

  const handleNewPrompt = () => {
    setInput('');
    setMessages([]);
    setStatusNote('');
    setActiveTask('code');
    setFormatType('structured');
  };

  if (view === '404') {
    return <NotFoundView onBack={() => setView('workshop')} />;
  }

  const handleSend = async (instructions = null, prevPrompt = null) => {
    const isRefinement = !!instructions;

    if (!isRefinement && (!input.trim() || loading)) return;

    if (!isRefinement && input.toLowerCase().includes("goto 404")) {
      setView('404');
      return;
    }

    setLoading(true);

    try {
      const resp = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task: activeTask,
          user_input: isRefinement ? "Refining previous output" : input,
          user_id: 1001,
          format_type: formatType,
          refinement_instructions: instructions || "",
          previous_prompt: prevPrompt || ""
        })
      });

      const data = await resp.json();
      let outputText = data.output || "Error generating response.";

      // If the output is a JSON object, stringify it for the Markdown renderer
      if (typeof outputText === 'object' && outputText !== null) {
        outputText = `\`\`\`json\n${JSON.stringify(outputText, null, 2)}\n\`\`\``;
      }

      const newMsg = {
        id: Date.now(),
        text: outputText,
        type: isRefinement ? "Refined Output" : "Engine Generated",
        icon: isRefinement ? "auto_fix_high" : "auto_awesome",
        color: isRefinement ? "tertiary" : "primary",
        params: data.evaluations || { Engine: "FastAPI", Model: "DeepMind v4" },
        notes: isRefinement ? "Iteration completed based on user feedback." : "Architecture generated based on real-time Feast feature ingestion and context injection."
      };

      setMessages([newMsg, ...messages]);
      if (!isRefinement) setInput('');
      setStatusNote('');

    } catch (err) {
      setShowError(true);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (id, text) => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback for non-secure contexts or older browsers
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "absolute";
        textArea.style.opacity = "0";
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
      alert('Failed to copy to clipboard.');
    }
  };

  return (
    <div className="bg-surface text-on-surface font-body min-h-screen">

      {/* TopNavBar */}
      <header className="bg-surface/95 backdrop-blur-md flex justify-between items-center w-full px-4 md:px-10 h-20 fixed top-0 z-50 border-b border-white/[0.03]">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-3 -ml-2 text-on-surface hover:text-primary transition-colors flex items-center justify-center z-[60]"
            aria-label="Toggle Menu"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
          <span className="material-symbols-outlined text-on-surface/40 text-2xl md:text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>memory</span>
          <span className="text-xl md:text-2xl font-black text-on-surface uppercase tracking-tighter">Dr. <span className="text-on-surface-variant opacity-60">Prompt</span></span>
        </div>
        <div className="flex items-center gap-3 md:gap-6">
          <div className="hidden md:flex gap-8 text-[#adaaaa] font-inter text-sm font-medium">
            <a className="text-on-surface font-bold transition-all hover:text-primary px-2" href="#" onClick={(e) => { e.preventDefault(); }}>
              Workshop
            </a>
            <a className="text-on-surface-variant hover:text-on-surface transition-all px-2" href="#" onClick={(e) => { e.preventDefault(); setShowConstruction(true); }}>
              History
            </a>
            <a className="text-on-surface-variant hover:text-on-surface transition-all px-2" href="#" onClick={(e) => { e.preventDefault(); setShowConstruction(true); }}>
              Templates
            </a>
            <a className="text-on-surface-variant hover:text-on-surface transition-all px-2" href="#" onClick={(e) => { e.preventDefault(); setShowConstruction(true); }}>
              Settings
            </a>
          </div>
          <div className="flex items-center gap-2 md:gap-4">
            <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors text-xl md:text-2xl">help_outline</span>
            <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-surface-container-high border border-primary/20 flex items-center justify-center cursor-pointer hover:scale-110 transition-transform">
              <span className="material-symbols-outlined text-primary text-xl md:text-2xl">account_circle</span>
            </div>
          </div>
        </div>
      </header>

      {/* SideNavBar - Responsive Drawer */}
      <aside className={`fixed left-0 top-0 h-full w-72 bg-surface/95 lg:bg-surface/50 backdrop-blur-3xl pt-24 pb-8 px-6 flex flex-col border-r border-white/[0.03] z-40 transition-transform duration-300 lg:translate-x-0 ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="mb-8 px-4">
          <h2 className="text-xl font-black text-primary uppercase tracking-tighter flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <span className="material-symbols-outlined text-xl">bolt</span>
            </div>
            PROMPT ENGINE
          </h2>
          <p className="text-[10px] text-on-surface-variant font-black tracking-widest uppercase opacity-30 mt-1">Version 1.0</p>
        </div>
        <button
          onClick={handleNewPrompt}
          className="mb-8 w-full py-4 px-6 bg-on-surface text-background font-black uppercase tracking-[0.2em] text-[10px] rounded-xl shadow-xl hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-3 transition-all duration-300"
        >
          <span className="material-symbols-outlined text-lg">add</span>
          New Prompt
        </button>
        <nav className="flex flex-col gap-1">
          <a className="flex items-center gap-4 px-6 py-4 bg-surface-variant text-on-surface rounded-xl border border-white/[0.05] shadow-lg transition-all duration-300" href="#">
            <span className="text-[10px] font-black uppercase tracking-[0.2em]">Workshop</span>
          </a>
          <a className="flex items-center gap-4 px-6 py-4 text-on-surface-variant hover:bg-surface-variant/50 hover:text-on-surface rounded-xl transition-all duration-300 group" href="#" onClick={(e) => { e.preventDefault(); setShowConstruction(true); }}>
            <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60 group-hover:opacity-100 transition-opacity">History</span>
          </a>
          <a className="flex items-center gap-4 px-6 py-4 text-on-surface-variant hover:bg-surface-variant/50 hover:text-on-surface rounded-xl transition-all duration-300 group" href="#" onClick={(e) => { e.preventDefault(); setShowConstruction(true); }}>
            <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60 group-hover:opacity-100 transition-opacity">Templates</span>
          </a>
          <a className="flex items-center gap-4 px-6 py-4 text-on-surface-variant hover:bg-surface-variant/50 hover:text-on-surface rounded-xl transition-all duration-300 group" href="#" onClick={(e) => { e.preventDefault(); setShowConstruction(true); }}>
            <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60 group-hover:opacity-100 transition-opacity">Settings</span>
          </a>
        </nav>

        <div className="mt-auto mx-2 mb-6 p-6 bg-surface-variant/40 rounded-2xl border border-white/[0.03] flex items-center gap-3 group hover:bg-surface-variant transition-all cursor-pointer">
          <div className="w-10 h-10 rounded-full bg-surface-container-highest flex items-center justify-center text-primary font-bold border border-primary/20 group-hover:scale-110 transition-transform overflow-hidden">
            <img className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuC95K08BV9p1bHA-yCkin7ca1UVxigdjmCVRRU_1ng3entFGFqhL50Tu9qsD-XNgg6OAvIlTJaKVGUBfcCwSq02Py1lqIo51zSJoRL_yh_4jvogcUYO8-k-QafBqSmDUT_yI4qw3dW2lRTwEw85NYb0ya9RxyDQ7Agcnn96SB2XB9JkXs6rCLm34oqZ32eq1Ma5jG80qt8RK_51_oD9sLpoIuO0TYrvypFqakGXS4BZvkTBDIDPIBk7rmICgQ6YfSBfE2hVx1P75fA" alt="Avatar" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-bold text-on-surface">Alex Chen</span>
            <span className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold opacity-60">Pro Account</span>
          </div>
          <span className="material-symbols-outlined ml-auto text-on-surface-variant group-hover:text-primary transition-colors">more_vert</span>
        </div>
      </aside>

      {/* Mobile Drawer Overlay */}
      {isMobileMenuOpen && (
        <div
          className="drawer-overlay lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        ></div>
      )}

      {/* Main Content */}
      <main className="lg:ml-72 pt-20 min-h-screen px-4 sm:px-8 md:px-12 pb-20">
        {/* Header Section */}
        <section className="max-w-5xl mx-auto mb-8 md:mb-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <h1 className="text-3xl md:text-4xl font-extrabold tracking-tighter text-on-surface mb-2">Workshop <span className="text-primary">Canvas</span></h1>
              <p className="text-on-surface-variant text-xs md:text-sm max-w-md leading-relaxed">Refine, iterate, and master your AI instructions with volcanic precision. Optimized for LLM performance.</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="px-4 py-2 bg-surface-container-low rounded-full nm-inset flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${loading ? 'bg-on-surface-variant animate-pulse' : 'bg-green-500/80 shadow-[0_0_8px_rgba(34,197,94,0.4)]'}`}></div>
                <span className="text-[9px] md:text-[10px] font-black tracking-[0.2em] uppercase opacity-40">Engine {loading ? 'Syncing' : 'Online'}</span>
              </div>
            </div>
          </div>
        </section>

        {/* Primary Input Area */}
        <section className="max-w-5xl mx-auto mb-16 relative">
          <div className="relative group p-1 rounded-[2.2rem] border border-white/[0.05] bg-surface-variant/20 backdrop-blur-sm">
            <div className="bg-surface-container-lowest rounded-3xl p-1 shrink-0 overflow-hidden">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                className="w-full bg-transparent border-none focus:ring-0 text-base md:text-xl text-on-surface placeholder:text-on-surface-variant/20 p-4 md:p-8 min-h-[180px] md:min-h-[220px] resize-none font-body leading-loose outline-none"
                placeholder="Refine your conceptual core here. Let the engine handle the architecture..."
              />
              <div className="flex flex-wrap items-center justify-between p-6 border-t border-white/[0.03] bg-surface/30">
                <div className="flex gap-6 items-center">
                  <div className="flex bg-surface-variant/40 rounded-lg p-1 border border-white/[0.05]">
                    {['code', 'image', 'document'].map(t => (
                      <button
                        key={t}
                        onClick={() => setActiveTask(t)}
                        className={`px-3 py-1.5 rounded-md text-[9px] font-black uppercase tracking-widest transition-all ${activeTask === t ? 'bg-primary text-on-primary shadow-lg' : 'text-on-surface-variant hover:text-on-surface'}`}
                      >
                        {t}
                      </button>
                    ))}
                  </div>

                  <div className="flex bg-surface-variant/40 rounded-lg p-1 border border-white/[0.05]">
                    {['structured', 'json'].map(f => (
                      <button
                        key={f}
                        onClick={() => setFormatType(f)}
                        className={`px-3 py-1.5 rounded-md text-[9px] font-black uppercase tracking-widest transition-all ${formatType === f ? 'bg-on-surface text-background shadow-lg' : 'text-on-surface-variant hover:text-on-surface'}`}
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                </div>
                <button
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                  className={`w-full md:w-auto py-3 px-6 md:px-10 rounded-xl border-2 font-black uppercase tracking-[0.25em] text-[9px] md:text-[10px] flex items-center justify-center gap-3 group transition-all duration-500 ${loading
                    ? 'border-surface-container-highest text-on-surface-variant/40 bg-surface-container-low cursor-not-allowed'
                    : 'border-primary/60 text-primary hover:bg-primary hover:text-on-primary hover:shadow-[0_0_40px_rgba(255,122,47,0.4)] shadow-2xl'
                    }`}
                >
                  {loading ? 'Analyzing Neural Patterns...' : 'Engineer Prompt'}
                  <span className={`material-symbols-outlined text-lg transition-transform ${loading ? 'animate-spin' : 'group-hover:translate-x-1'}`}>
                    {loading ? 'autorenew' : 'auto_awesome'}
                  </span>
                </button>
              </div>
              {statusNote && (
                <div className="px-8 pb-4 text-[9px] font-bold text-primary/60 uppercase tracking-widest animate-pulse flex items-center gap-2">
                  <span className="w-1 h-1 bg-primary/40 rounded-full"></span>
                  {statusNote}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Results Grid */}
        <section className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-xl font-black text-on-surface uppercase tracking-tight flex items-center gap-4">
              <div className="w-1.5 h-6 bg-on-surface/10 rounded-full group-hover:scale-y-125 transition-transform"></div>
              Refinement Variations
            </h3>
            <div className="flex bg-surface-container rounded-xl p-1 border border-white/[0.03] nm-inset">
              <button
                onClick={() => setLayoutView('grid')}
                className={`p-2 rounded-lg transition-all hover:scale-105 ${layoutView === 'grid' ? 'text-primary bg-surface-container-high shadow-lg' : 'text-on-surface-variant hover:text-on-surface'}`}
              >
                <span className="material-symbols-outlined text-base">grid_view</span>
              </button>
              <button
                onClick={() => setLayoutView('list')}
                className={`p-2 rounded-lg transition-all hover:scale-105 ${layoutView === 'list' ? 'text-primary bg-surface-container-high shadow-lg' : 'text-on-surface-variant hover:text-on-surface'}`}
              >
                <span className="material-symbols-outlined text-base">view_agenda</span>
              </button>
            </div>
          </div>

          <div className={layoutView === 'grid' ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8" : "grid grid-cols-1 gap-12"}>
            <AnimatePresence mode="popLayout">
              {messages.map((msg) => (
                <motion.div
                  initial={{ opacity: 0, y: 50 }}
                  animate={{ opacity: 1, y: 0 }}
                  key={msg.id}
                  className="bg-surface-container-low rounded-[1.5rem] md:rounded-[2rem] p-4 md:p-8 nm-convex relative overflow-hidden group"
                >
                  <div className={`grid ${layoutView === 'grid' ? 'grid-cols-1' : 'lg:grid-cols-12'} gap-8`}>
                    {/* Left Panel: The Prompt */}
                    <div className={layoutView === 'grid' ? "col-span-1" : "lg:col-span-8"}>
                      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                        <div className="flex items-center gap-3">
                          <h4 className="text-sm font-bold text-on-surface-variant flex items-center gap-2">
                            <span className={`material-symbols-outlined text-${msg.color} text-sm`}>{msg.icon}</span> Refined Prompt
                          </h4>
                          <span className={`bg-${msg.color}/10 text-${msg.color} px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-tighter h-fit`}>
                            {msg.type}
                          </span>
                        </div>
                        <button
                          onClick={() => copyToClipboard(msg.id, msg.text)}
                          className={`flex items-center gap-2 text-[10px] font-bold bg-surface-container-highest px-4 py-2 rounded-lg nm-flat nm-button-active transition-colors h-fit ${copiedId === msg.id ? 'text-green-500' : `hover:text-${msg.color}`}`}
                        >
                          <span className="material-symbols-outlined text-xs">{copiedId === msg.id ? 'check' : 'content_copy'}</span>
                          {copiedId === msg.id ? 'COPIED!' : 'COPY'}
                        </button>
                      </div>
                      <div className="border border-white/[0.05] p-1 rounded-3xl bg-surface/40">
                        <div className="bg-surface-container-lowest p-4 md:p-8 rounded-[1.4rem]">
                          <div className="text-on-surface text-sm md:text-base leading-relaxed md:leading-[2] font-body markdown-content opacity-90">
                            <ReactMarkdown>{msg.text}</ReactMarkdown>
                          </div>
                        </div>
                      </div>
                      <div className="mt-4">
                        <PromptRefiner onRefine={handleSend} prevPrompt={msg.text} color={msg.color} />
                      </div>
                    </div>

                    {/* Right Panel: Metadata */}
                    <div className={layoutView === 'grid' ? "col-span-1 flex flex-col gap-6" : "lg:col-span-4 flex flex-col gap-6"}>
                      <div>
                        <h5 className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest mb-3">Style Parameters</h5>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(msg.params).map(([key, val]) => (
                            <span key={key} className="px-3 py-1 bg-surface-container-high rounded-md text-[10px] border border-outline-variant/10">
                              {key}: {val}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h5 className="text-[10px] font-black text-on-surface uppercase tracking-widest mb-3 opacity-40">Context Notes</h5>
                        <div className="p-5 bg-surface-container-high/30 border border-white/[0.03] rounded-2xl text-xs text-on-surface leading-loose">
                          {msg.notes}
                        </div>
                      </div>
                      <button
                        onClick={() => setShowConstruction(true)}
                        className={`mt-auto w-full py-3 rounded-xl border border-${msg.color}/20 text-${msg.color} text-[10px] font-black hover:bg-${msg.color}/5 transition-all uppercase tracking-[0.2em] flex items-center justify-center gap-2 group nm-flat hover:nm-convex`}
                      >
                        <span className="material-symbols-outlined text-sm group-hover:rotate-180 transition-transform">expand_more</span>
                        Expand Details
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </section>
      </main>

      {/* Floating Action Button */}
      <div className="fixed bottom-10 right-10 z-50">
        <button
          onClick={() => setShowConstruction(true)}
          className="w-16 h-16 bg-surface-variant text-on-surface rounded-full shadow-2xl flex flex-col items-center justify-center border border-white/[0.05] hover:scale-110 transition-transform active:scale-90 group relative overflow-hidden"
        >
          <span className="material-symbols-outlined text-3xl opacity-60 group-hover:opacity-100 group-hover:text-primary transition-all">chat_bubble</span>
        </button>
      </div>

      {/* Overlays */}
      <AnimatePresence>
        {(loading || isInitialLoading) && <LoadingScreen />}
        {showError && (
          <ConnectionErrorPopup
            onRetry={() => { setShowError(false); handleSend(); }}
            onSupport={() => alert("Redirecting to Mission Control...")}
          />
        )}
        {showConstruction && (
          <ConstructionModal onClose={() => setShowConstruction(false)} />
        )}
      </AnimatePresence>

    </div>
  );
};

export default App;
