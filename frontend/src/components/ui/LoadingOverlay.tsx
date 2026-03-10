import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, Zap, BrainCircuit, ShieldCheck, Database, FileSearch, Sparkles } from 'lucide-react';
import { useState, useEffect } from 'react';

export function LoadingOverlay() {
    const [step, setStep] = useState(0);

    const steps = [
        { icon: FileSearch, text: "Analyzing Structure...", color: "text-blue-400" },
        { icon: BrainCircuit, text: "Processing Context...", color: "text-purple-400" },
        { icon: Database, text: "Mapping NIST Controls...", color: "text-orange-400" },
        { icon: ShieldCheck, text: "Detecting Gaps...", color: "text-emerald-400" },
        { icon: Sparkles, text: "Generating Insights...", color: "text-amber-400" }
    ];

    useEffect(() => {
        const timer = setInterval(() => {
            setStep((prev) => (prev < steps.length - 1 ? prev + 1 : 0));
        }, 2000); // Change step every 2 seconds
        return () => clearInterval(timer);
    }, []);

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#0B0B15]/90 backdrop-blur-md"
        >
            <div className="relative w-full max-w-sm flex flex-col items-center justify-center space-y-8 p-8">
                {/* Animated Glow Background */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-orange-500/10 blur-3xl animate-pulse" />

                {/* Central Icon Animation */}
                <div className="relative">
                    <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-0 rounded-full border-t-2 border-r-2 border-blue-500/30 blur-sm w-32 h-32 -m-4"
                    />
                    <motion.div
                        animate={{ rotate: -360 }}
                        transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-0 rounded-full border-b-2 border-l-2 border-purple-500/30 blur-sm w-40 h-40 -m-8"
                    />

                    <AnimatePresence mode="wait">
                        <motion.div
                            key={step}
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                            transition={{ duration: 0.5 }}
                            className="bg-[#1E1E2C] p-6 rounded-2xl border border-white/10 shadow-2xl relative z-10"
                        >
                            {(() => {
                                const Icon = steps[step].icon;
                                return <Icon className={`w-12 h-12 ${steps[step].color}`} />;
                            })()}
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* Text and Progress */}
                <div className="text-center space-y-4 relative z-10 w-full">
                    <AnimatePresence mode="wait">
                        <motion.h3
                            key={step}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="text-2xl font-bold text-white tracking-wide"
                        >
                            {steps[step].text}
                        </motion.h3>
                    </AnimatePresence>

                    <div className="w-full bg-[#334155]/30 h-1.5 rounded-full overflow-hidden backdrop-blur-sm">
                        <motion.div
                            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-orange-500"
                            animate={{
                                width: ["0%", "100%"],
                                x: ["-100%", "100%"]
                            }}
                            transition={{
                                duration: 2,
                                ease: "easeInOut",
                                repeat: Infinity
                            }}
                        />
                    </div>

                    <p className="text-sm text-slate-500 animate-pulse">
                        Using Mistral-7B Intelligence Engine
                    </p>
                </div>
            </div>
        </motion.div>
    );
}
