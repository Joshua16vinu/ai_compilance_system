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
    AlertCircle,
    Download,
    ArrowLeft
} from 'lucide-react'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/Badge'

interface AnalysisResult {
    domain: string
    subdomain: string
    gap_analysis?: Gap[]
    revised_policy?: RevisedPolicy
    implementation_roadmap?: Roadmap
    nist_records_used?: any[]
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

    const gaps = data?.gap_analysis ?? []

    const highestSeverity =
        gaps.some(g => g.severity === 'Critical')
            ? 'Critical'
            : gaps.some(g => g.severity === 'High')
                ? 'High'
                : gaps.length > 0
                    ? 'Medium'
                    : 'None'

    const downloadPDF = () => {
        const doc = new jsPDF()

        const primaryColor = [59, 143, 243]
        const secondaryColor = [242, 159, 103]

        doc.setFillColor(11, 11, 21)
        doc.rect(0, 0, 210, 297, 'F')

        doc.setTextColor(255, 255, 255)
        doc.setFontSize(24)
        doc.text("Security Gap Analysis Report", 20, 100)

        doc.setFontSize(16)
        doc.setTextColor(primaryColor[0], primaryColor[1], primaryColor[2])
        doc.text(`Domain: ${data.domain}`, 20, 115)

        doc.setFontSize(12)
        doc.setTextColor(150, 150, 160)
        doc.text(`Report Generated: ${new Date().toLocaleDateString()}`, 20, 280)

        doc.addPage()

        const addHeader = (title: string) => {
            doc.setFillColor(245, 247, 250)
            doc.rect(0, 0, 210, 20, 'F')
            doc.setFontSize(10)
            doc.setTextColor(100, 100, 100)
            doc.text("Mistral Security Audit", 14, 13)
            doc.text(title, 200, 13, { align: "right" })
        }

        addHeader("Gap Analysis")

        const gapData = gaps.map(g => [
            g.gap_id,
            g.description,
            g.severity,
            g.nist_reference
        ])

        autoTable(doc, {
            startY: 40,
            head: [['ID', 'Description', 'Severity', 'NIST Ref']],
            body: gapData
        })

        doc.save(`${data.domain.replace(/\s+/g, '_')}_Security_Report.pdf`)
    }

    return (
        <div className="space-y-8 animate-enter pb-20">

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/5 pb-8">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <Badge label={data.domain} variant="primary" />
                        <span className="text-slate-500 text-sm">/</span>
                        <span className="text-slate-300 font-medium">{data.subdomain}</span>
                    </div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Analysis Results</h1>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={downloadPDF}
                        className="flex items-center gap-2 px-4 py-2 bg-[#F29F67] hover:bg-[#F29F67]/90 text-white rounded-lg font-medium shadow-lg shadow-[#F29F67]/20 transition-all hover:scale-105"
                    >
                        <Download className="w-4 h-4" />
                        Download Report
                    </button>

                    <div className="h-8 w-[1px] bg-white/10 mx-2" />

                    <div className="flex gap-2 bg-[#151520] p-1 rounded-lg border border-white/5">
                        <TabButton active={activeTab === 'gaps'} onClick={() => setActiveTab('gaps')} icon={AlertTriangle} label="Gap Analysis" />
                        <TabButton active={activeTab === 'policy'} onClick={() => setActiveTab('policy')} icon={FileText} label="Revised Policy" />
                        <TabButton active={activeTab === 'roadmap'} onClick={() => setActiveTab('roadmap')} icon={Target} label="Roadmap" />
                    </div>
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
                                value={gaps.length}
                                icon={AlertCircle}
                                color="text-[#ef4444]"
                                bg="bg-[#ef4444]/10"
                            />

                            <StatsCard
                                label="Highest Severity"
                                value={highestSeverity}
                                icon={Activity}
                                color="text-[#F29F67]"
                                bg="bg-[#F29F67]/10"
                            />

                            <StatsCard
                                label="Compliance Impact"
                                value={gaps.length > 0 ? "Significant" : "Minimal"}
                                icon={Target}
                                color="text-[#3B8FF3]"
                                bg="bg-[#3B8FF3]/10"
                            />
                        </div>

                        <div className="space-y-4">
                            {gaps.map((gap, i) => (
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
                        <div className="space-y-6">
                            <p>{data?.revised_policy?.introduction}</p>

                            <ul className="space-y-3">
                                {data?.revised_policy?.statements?.map((stmt, i) => (
                                    <li key={i}>{stmt}</li>
                                ))}
                            </ul>

                            <p>{data?.revised_policy?.compliance_notes}</p>
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
                        <RoadmapSection title="Short Term" period="0-3 Months" items={data?.implementation_roadmap?.short_term ?? []} />
                        <RoadmapSection title="Mid Term" period="3-6 Months" items={data?.implementation_roadmap?.mid_term ?? []} />
                        <RoadmapSection title="Long Term" period="6-12 Months" items={data?.implementation_roadmap?.long_term ?? []} />
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="fixed bottom-8 right-8">
                <button
                    onClick={onReset}
                    className="flex items-center gap-2 px-6 py-3 bg-[#1E1E2C] hover:bg-[#252536] text-white rounded-full font-medium shadow-2xl border border-white/10 transition-all hover:scale-105"
                >
                    <ArrowLeft className="w-5 h-5" />
                    Back to Domains
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
        <div className="bg-[#151520]/60 backdrop-blur border border-white/5 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white">{gap.description}</h3>
            <p className="text-slate-400 text-sm">{gap.impact}</p>
        </div>
    )
}

function RoadmapSection({ title, period, items }: any) {
    return (
        <div className="space-y-4">
            <h3 className="text-xl font-bold text-white">{title}</h3>

            {items.map((item: RoadmapAction, i: number) => (
                <div key={i} className="bg-[#151520]/60 border border-white/5 p-5 rounded-xl">
                    <h4 className="font-semibold text-white">{item.action}</h4>
                    <p className="text-slate-400 text-sm">Resources: {item.resources}</p>
                </div>
            ))}
        </div>
    )
}