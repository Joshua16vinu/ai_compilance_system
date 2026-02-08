'use client'

import { motion } from 'framer-motion'
import { Database, FileText, ArrowRight, Shield, Lock, Activity } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'

interface Domain {
    domain: string
    text: string
    subdomains: string[]
}

interface DomainSelectionProps {
    domains: Domain[]
    onSelect: (domain: Domain) => void
    onBack?: () => void
}

export function DomainSelectionView({ domains, onSelect, onBack }: DomainSelectionProps) {
    return (
        <div className="space-y-8 animate-enter max-w-5xl mx-auto">
            <div className="text-center space-y-4 mb-12">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="inline-flex items-center justify-center p-3 rounded-2xl bg-[#3B8FF3]/10 text-[#3B8FF3] mb-4"
                >
                    <Shield className="w-8 h-8" />
                </motion.div>
                <motion.h2
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-3xl font-bold text-white tracking-tight"
                >
                    Select Analysis Domain
                </motion.h2>
                <motion.p
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="text-slate-400 max-w-2xl mx-auto text-lg"
                >
                    We identified {domains.length} security domains in your document. Select a domain to generate a detailed gap analysis and implementation roadmap.
                </motion.p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {domains.map((domain, index) => (
                    <DomainCard
                        key={index}
                        domain={domain}
                        index={index}
                        onClick={() => onSelect(domain)}
                    />
                ))}
            </div>

            <div className="text-center mt-12">
                <button
                    onClick={onBack}
                    className="text-slate-500 hover:text-white transition-colors text-sm"
                >
                    ← Upload different document
                </button>
            </div>
        </div>
    )
}

function DomainCard({ domain, index, onClick }: { domain: Domain, index: number, onClick: () => void }) {
    // Determine icon based on domain name (simple heuristic)
    const getIcon = (name: string) => {
        const n = name.toLowerCase()
        if (n.includes('risk')) return Activity
        if (n.includes('security') || n.includes('isms')) return Lock
        return Database
    }

    const Icon = getIcon(domain.domain)

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 + 0.3 }}
            onClick={onClick}
            className="group relative overflow-hidden rounded-2xl border border-white/5 bg-[#151520]/60 backdrop-blur-md p-6 hover:border-[#F29F67]/50 transition-all cursor-pointer hover:shadow-2xl hover:shadow-[#F29F67]/10 hover:-translate-y-1"
        >
            <div className="absolute inset-0 bg-gradient-to-br from-[#F29F67]/0 via-transparent to-[#3B8FF3]/0 opacity-0 group-hover:opacity-10 transition-opacity duration-500" />

            <div className="relative z-10 flex flex-col h-full">
                <div className="flex justify-between items-start mb-4">
                    <div className="p-3 rounded-xl bg-[#1E1E2C] group-hover:bg-[#F29F67]/20 transition-colors border border-white/5">
                        <Icon className="w-6 h-6 text-[#F29F67] group-hover:scale-110 transition-transform" />
                    </div>
                    <Badge label={`${domain.subdomains.length} Subdomains`} variant="default" />
                </div>

                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-[#F29F67] transition-colors">
                    {domain.domain}
                </h3>

                <div className="bg-[#0B0B15]/30 p-3 rounded-lg border border-white/5 mb-6">
                    <p className="text-slate-400 text-sm leading-relaxed max-h-[150px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent pr-2">
                        {domain.text}
                    </p>
                </div>

                <div className="mt-auto space-y-4">
                    <div className="flex flex-wrap gap-2">
                        {domain.subdomains.slice(0, 3).map((sub, i) => (
                            <span key={i} className="text-xs font-mono text-slate-500 bg-[#0B0B15]/50 border border-white/5 px-2 py-1 rounded">
                                {sub}
                            </span>
                        ))}
                        {domain.subdomains.length > 3 && (
                            <span className="text-xs font-mono text-slate-500 px-1 py-1">
                                +{domain.subdomains.length - 3} more
                            </span>
                        )}
                    </div>

                    <div className="flex items-center text-[#F29F67] font-medium text-sm pt-4 border-t border-white/5 group-hover:border-[#F29F67]/20 transition-colors">
                        <span>Generate Analysis</span>
                        <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </div>
                </div>
            </div>
        </motion.div>
    )
}
