'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    AlertTriangle,
    CheckCircle2,
    ChevronDown,
    FileText,
    Target,
    Activity,
    Calendar,
    ArrowRight,
    LayoutDashboard,
    AlertCircle
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/Badge'

interface AnalysisResult {
    domain: string
    subdomain: string
    gap_analysis: Gap[]
    revised_policy: RevisedPolicy
    implementation_roadmap: Roadmap
    nist_records_used: any[]
}

interface Gap {
    gap_id: string
    description: string
    nist_reference: string
    severity: string
    impact: string
}

interface RevisedPolicy {
    introduction: string
    statements: string[]
    compliance_notes: string
}

interface RoadmapAction {
    action: string
    timeline: string
    priority: string
    resources: string
}

interface Roadmap {
    short_term: RoadmapAction[]
    mid_term: RoadmapAction[]
    long_term: RoadmapAction[]
}

interface Props {
    data: AnalysisResult
    onReset: () => void
}

export function SingleDomainAnalysisView({ data, onReset }: Props) {
    const [activeTab, setActiveTab] = useState<'gaps' | 'policy' | 'roadmap'>('gaps')

    return (
        <div className="space-y-8 animate-enter pb-20">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/5 pb-8">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <Badge label={data.domain} variant="primary" />
                        <span className="text-slate-500 text-sm">/</span>
                        <span className="text-slate-300 font-medium">{data.subdomain}</span>
                    </div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Analysis Results</h1>
                </div>

                <div className="flex gap-2 bg-[#151520] p-1 rounded-lg border border-white/5">
                    <TabButton active={activeTab === 'gaps'} onClick={() => setActiveTab('gaps')} icon={AlertTriangle} label="Gap Analysis" />
                    <TabButton active={activeTab === 'policy'} onClick={() => setActiveTab('policy')} icon={FileText} label="Revised Policy" />
                    <TabButton active={activeTab === 'roadmap'} onClick={() => setActiveTab('roadmap')} icon={Target} label="Roadmap" />
                </div>
            </div>

            <AnimatePresence mode="wait">
                {activeTab === 'gaps' && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        key="gaps"
                        className="space-y-6"
                    >
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <StatsCard
                                label="Total Gaps"
                                value={data.gap_analysis.length}
                                icon={AlertCircle}
                                color="text-[#ef4444]"
                                bg="bg-[#ef4444]/10"
                            />
                            <StatsCard
                                label="Highest Severity"
                                value={data.gap_analysis.some(g => g.severity === 'Critical') ? 'Critical' : 'High'}
                                icon={Activity}
                                color="text-[#F29F67]"
                                bg="bg-[#F29F67]/10"
                            />
                            <StatsCard
                                label="Compliance Impact"
                                value="Significant"
                                icon={Target}
                                color="text-[#3B8FF3]"
                                bg="bg-[#3B8FF3]/10"
                            />
                        </div>

                        <div className="space-y-4">
                            {data.gap_analysis.map((gap, i) => (
                                <GapCard key={i} gap={gap} />
                            ))}
                        </div>
                    </motion.div>
                )}

                {activeTab === 'policy' && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        key="policy"
                        className="bg-[#151520]/40 backdrop-blur border border-white/5 rounded-2xl p-8 max-w-4xl mx-auto"
                    >
                        <div className="prose prose-invert max-w-none">
                            <h3 className="text-xl font-bold text-white mb-4 border-b border-white/5 pb-4">
                                Optimized Policy Document
                            </h3>

                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-[#3B8FF3] text-sm font-bold uppercase tracking-wider mb-2">Introduction</h4>
                                    <p className="text-slate-300 leading-relaxed bg-[#1E1E2C]/50 p-4 rounded-lg border border-white/5">
                                        {data.revised_policy.introduction}
                                    </p>
                                </div>

                                <div>
                                    <h4 className="text-[#34B1AA] text-sm font-bold uppercase tracking-wider mb-2">Policy Statements</h4>
                                    <ul className="space-y-3">
                                        {data.revised_policy.statements.map((stmt, i) => (
                                            <li key={i} className="flex gap-4 items-start bg-[#1E1E2C]/30 p-4 rounded-lg border border-white/5 hover:border-[#34B1AA]/30 transition-colors">
                                                <span className="flex-shrink-0 w-6 h-6 rounded bg-[#34B1AA]/10 text-[#34B1AA] flex items-center justify-center text-xs font-bold mt-0.5">
                                                    {i + 1}
                                                </span>
                                                <span className="text-slate-200">{stmt}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                <div>
                                    <h4 className="text-[#F29F67] text-sm font-bold uppercase tracking-wider mb-2">Compliance Notes</h4>
                                    <div className="flex items-start gap-3 p-4 bg-[#F29F67]/5 rounded-lg border border-[#F29F67]/10 text-[#F29F67]/90 text-sm">
                                        <CheckCircle2 className="w-5 h-5 shrink-0" />
                                        <p>{data.revised_policy.compliance_notes}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {activeTab === 'roadmap' && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        key="roadmap"
                        className="max-w-4xl mx-auto space-y-8"
                    >
                        <RoadmapSection title="Short Term" period="0-3 Months" items={data.implementation_roadmap.short_term} color="text-[#ef4444]" border="border-[#ef4444]" />
                        <RoadmapSection title="Mid Term" period="3-6 Months" items={data.implementation_roadmap.mid_term} color="text-[#F29F67]" border="border-[#F29F67]" />
                        <RoadmapSection title="Long Term" period="6-12 Months" items={data.implementation_roadmap.long_term} color="text-[#34B1AA]" border="border-[#34B1AA]" />
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="fixed bottom-8 right-8">
                <button
                    onClick={onReset}
                    className="flex items-center gap-2 px-6 py-3 bg-[#1E1E2C] hover:bg-[#252536] text-white rounded-full font-medium shadow-2xl border border-white/10 transition-all hover:scale-105"
                >
                    <LayoutDashboard className="w-5 h-5" />
                    Back to Dashboard
                </button>
            </div>
        </div>
    )
}

function TabButton({ active, onClick, icon: Icon, label }: any) {
    return (
        <button
            onClick={onClick}
            className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all",
                active
                    ? "bg-[#3B8FF3] text-white shadow-lg shadow-[#3B8FF3]/20"
                    : "text-slate-400 hover:text-white hover:bg-white/5"
            )}
        >
            <Icon className="w-4 h-4" />
            {label}
        </button>
    )
}

function StatsCard({ label, value, icon: Icon, color, bg }: any) {
    return (
        <div className="bg-[#151520]/60 backdrop-blur border border-white/5 p-6 rounded-xl flex items-center justify-between">
            <div>
                <p className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">{label}</p>
                <p className="text-2xl font-bold text-white">{value}</p>
            </div>
            <div className={cn("p-3 rounded-xl", bg, color)}>
                <Icon className="w-6 h-6" />
            </div>
        </div>
    )
}

function GapCard({ gap }: { gap: Gap }) {
    return (
        <div className="group relative overflow-hidden bg-[#151520]/60 backdrop-blur border border-white/5 rounded-xl p-6 hover:border-[#ef4444]/30 transition-all">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#ef4444]" />

            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-4">
                <div className="space-y-1">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-slate-500 bg-[#1E1E2C] px-2 py-1 rounded border border-white/5">
                            {gap.gap_id}
                        </span>
                        <span className="text-xs font-bold text-[#ef4444] bg-[#ef4444]/10 px-2 py-1 rounded uppercase">
                            {gap.severity} Severity
                        </span>
                    </div>
                    <h3 className="text-lg font-semibold text-white">{gap.description}</h3>
                </div>
                <div className="text-right shrink-0">
                    <span className="text-xs text-slate-500 block">Reference</span>
                    <span className="text-sm font-mono text-[#3B8FF3]">{gap.nist_reference}</span>
                </div>
            </div>

            <div className="bg-[#1E1E2C]/50 p-4 rounded-lg">
                <div className="flex items-center gap-2 text-[#ef4444] mb-2 text-sm font-medium">
                    <AlertTriangle className="w-4 h-4" />
                    Business Impact
                </div>
                <p className="text-slate-400 text-sm leading-relaxed">{gap.impact}</p>
            </div>
        </div>
    )
}

function RoadmapSection({ title, period, items, color, border }: any) {
    return (
        <div className="relative pl-8 border-l-2 border-[#1E1E2C]">
            <div className={cn("absolute -left-[9px] top-0 w-4 h-4 rounded-full border-2 bg-[#0B0B15]", border, color)} />

            <div className="mb-6">
                <h3 className={cn("text-xl font-bold mb-1", color)}>{title}</h3>
                <div className="flex items-center gap-2 text-slate-500 text-sm">
                    <Calendar className="w-4 h-4" />
                    {period}
                </div>
            </div>

            <div className="space-y-4">
                {items?.map((item: RoadmapAction, i: number) => (
                    <div key={i} className="bg-[#151520]/60 border border-white/5 p-5 rounded-xl hover:border-white/10 transition-colors">
                        <div className="flex justify-between items-start mb-2">
                            <h4 className="font-semibold text-white">{item.action}</h4>
                            <Badge label={item.priority} variant={item.priority === 'Critical' ? 'danger' : item.priority === 'High' ? 'warning' : 'primary'} />
                        </div>
                        <p className="text-slate-400 text-sm">Resources: <span className="text-slate-300">{item.resources}</span></p>
                    </div>
                ))}
            </div>
        </div>
    )
}
