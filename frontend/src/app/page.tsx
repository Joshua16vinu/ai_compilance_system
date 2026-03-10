'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { UploadZone } from '@/features/upload/UploadZone'
import { AnalysisView } from '@/features/analysis/AnalysisView'
import { DomainSelectionView } from '@/features/analysis/DomainSelectionView'
import { SingleDomainAnalysisView } from '@/features/analysis/SingleDomainAnalysisView'
import { BarChart3, Database, ShieldAlert, FileKey, Loader2 } from 'lucide-react'
import { RmfCycleChart, TaxonomyChart, NistDistributionChart } from '@/components/StandardsCharts'
import { PolicyDetailsModal, Policy } from '@/components/features/analysis/PolicyDetailsModal'
import { LoadingOverlay } from '@/components/ui/LoadingOverlay'

export default function EnterpriseDashboard() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [uploadedDomains, setUploadedDomains] = useState<any[]>([])
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  // existing state for compatibility/sidebar
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  // Load from cache on mount
  useEffect(() => {
    const cached = localStorage.getItem('uploadedDomains')
    if (cached) {
      try {
        setUploadedDomains(JSON.parse(cached))
      } catch (e) {
        console.error("Failed to parse cached domains", e)
      }
    }
  }, [])

  const handleUploadSuccess = (data: any[]) => {
    // The API returns an array of domains
    setUploadedDomains(data)
    localStorage.setItem('uploadedDomains', JSON.stringify(data))
    setActiveTab('domain-selection')
  }

  const handleDomainSelect = async (domainObj: any) => {
    setIsAnalyzing(true)
    // Small delay to let the UI update and show the loader smoothly
    await new Promise(r => setTimeout(r, 500))

    try {
      const res = await axios.post('http://127.0.0.1:5000/api/analyze-domain', domainObj)
      setAnalysisResult(res.data)
      setActiveTab('scan')
    } catch (error) {
      console.error("Analysis failed", error)
      // Ideally show an error toast here
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReturnToDomains = () => {
    setAnalysisResult(null)
    setActiveTab('domain-selection')
  }

  const handleReset = () => {
    // This is a full reset
    setAnalysisResult(null)
    setUploadedDomains([])
    localStorage.removeItem('uploadedDomains')
    setActiveTab('dashboard')
  }

  return (
    <div className="flex h-screen overflow-hidden selection:bg-[#F29F67]/30 selection:text-[#F29F67] font-sans">

      {/* 1. Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* 2. Main Area */}
      <div className="flex-1 flex flex-col relative overflow-hidden text-slate-400 bg-transparent">
        {/* Ambient Glow */}
        <div className="absolute top-0 left-0 w-full h-[500px] bg-[#3B8FF3]/10 blur-[120px] rounded-full pointer-events-none mix-blend-screen" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-[#F29F67]/5 blur-[100px] rounded-full pointer-events-none mix-blend-screen" />

        <Header onSelectPolicy={setSelectedPolicy} />

        <main className="flex-1 overflow-y-auto p-4 lg:p-12 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
          <AnimatePresence mode="wait">

            {/* VIEW: DASHBOARD */}
            {activeTab === 'dashboard' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="w-full space-y-16 max-w-[1800px] mx-auto pb-12"
              >
                <div className="space-y-4 text-center lg:text-left mt-4">
                  <h1 className="text-4xl lg:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-200 to-slate-500 tracking-tight mb-2 drop-shadow-sm">
                    Secure AI Policy Compliance & Gap Analysis System
                  </h1>
                  <p className="text-base lg:text-lg max-w-3xl leading-relaxed text-slate-400 mx-auto lg:mx-0">
                    Next-generation policy analysis platform running entirely offline for complete data privacy.
                  </p>
                </div>

                {/* UPLOAD & WORKFLOW */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-12 lg:gap-16 items-start mb-16">
                  <div className="space-y-8">
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-6">Policy Analysis Workflow</h2>
                      <div className="space-y-6">
                        <WorkflowStep number="01" title="Import Documents" text="Upload organizational policy files (PDF/DOCX) for processing." />
                        <WorkflowStep number="02" title="Semantic Analysis" text="AI maps content to relevant NIST SP 800-53 control families." />
                        <WorkflowStep number="03" title="Gap Detection" text="Identify missing controls and compliance weaknesses automatically." />
                        <WorkflowStep number="04" title="Report Generation" text="Download comprehensive gap analysis reports for stakeholders." />
                      </div>
                    </div>
                  </div>

                  <div className="w-full h-full flex flex-col justify-center">
                    <UploadZone onSuccess={handleUploadSuccess} />
                  </div>
                </div>

                <div className="border-t border-[#F29F67]/10 mb-12" />

                {/* VISUALIZATION GRID */}
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 h-auto min-h-[400px]">
                  {/* RMF Cycle */}
                  <div className="h-[400px] lg:h-auto">
                    <RmfCycleChart />
                  </div>
                  {/* Taxonomy */}
                  <div className="h-auto min-h-[400px]">
                    <TaxonomyChart />
                  </div>
                  {/* Distribution */}
                  <div className="h-auto min-h-[400px]">
                    <NistDistributionChart />
                  </div>
                </div>

                {/* SECURITY DOMAINS REFERENCE */}
                <div className="space-y-8">
                  <div className="flex items-center gap-4">
                    <div className="h-8 w-1 bg-[#F29F67] rounded-full" />
                    <h2 className="text-2xl font-bold text-white tracking-tight">Supported Security Domains</h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <DomainCard
                      title="ISMS Governance"
                      definition="Governance, policy structure, and organizational roles."
                      families="PM, PL, CA, RA"
                      icon={Database}
                      color="text-[#3B8FF3]"
                      bg="bg-[#3B8FF3]/10"
                      border="border-[#3B8FF3]/20"
                    />
                    <DomainCard
                      title="Data Privacy & Security"
                      definition="Protection of sensitive data, encryption, and privacy controls."
                      families="SC, MP, PE"
                      icon={FileKey}
                      color="text-[#34B1AA]"
                      bg="bg-[#34B1AA]/10"
                      border="border-[#34B1AA]/20"
                    />
                    <DomainCard
                      title="Patch & Vulnerability"
                      definition="System integrity, update management, and flaw remediation."
                      families="SI, CM, MA"
                      icon={ShieldAlert}
                      color="text-[#E0B50F]"
                      bg="bg-[#E0B50F]/10"
                      border="border-[#E0B50F]/20"
                    />
                    <DomainCard
                      title="Risk Management"
                      definition="Risk assessment methodologies and response strategies."
                      families="RA, IR, CP"
                      icon={BarChart3}
                      color="text-[#F29F67]"
                      bg="bg-[#F29F67]/10"
                      border="border-[#F29F67]/20"
                    />
                  </div>
                </div>

              </motion.div>
            )}

            {/* VIEW: DOMAIN SELECTION */}
            {activeTab === 'domain-selection' && (
              <div className="max-w-[1400px] mx-auto">
                {isAnalyzing ? (
                  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
                    <LoadingOverlay />
                  </div>
                ) : (
                  <DomainSelectionView
                    domains={uploadedDomains}
                    onSelect={handleDomainSelect}
                    onBack={handleReset}
                  />
                )}
              </div>
            )}

            {/* VIEW: ANALYSIS */}
            {activeTab === 'scan' && analysisResult && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="max-w-[1400px] mx-auto"
              >
                <SingleDomainAnalysisView
                  data={analysisResult}
                  onReset={handleReturnToDomains}
                />
              </motion.div>
            )}

          </AnimatePresence>
        </main>

        {/* Global Modals */}
        <PolicyDetailsModal
          policy={selectedPolicy}
          onClose={() => setSelectedPolicy(null)}
        />

      </div>
    </div>
  )
}

function DomainCard({ title, definition, families, icon: Icon, color, bg, border }: any) {
  return (
    <div className={`p-6 rounded-xl border ${border} ${bg} hover:bg-opacity-20 transition-all group h-full flex flex-col`}>
      <div className="flex justify-between items-start mb-4">
        <div className={`p-3 rounded-lg bg-[#1E1E2C]/50 ${color} border border-white/5`}>
          <Icon className="w-6 h-6" />
        </div>
        <span className="text-[10px] font-mono text-slate-500 border border-slate-700/50 px-2 py-0.5 rounded uppercase tracking-wider">Ref</span>
      </div>

      <h3 className="text-white font-bold text-lg mb-2 group-hover:text-[#F29F67] transition-colors">{title}</h3>
      <p className="text-sm text-slate-400 leading-relaxed mb-4 flex-1">
        {definition}
      </p>

      <div className="pt-4 border-t border-white/5">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">Related NIST Families</span>
        <div className="flex flex-wrap gap-2">
          {families.split(', ').map((f: string) => (
            <span key={f} className="text-xs font-mono text-slate-300 bg-[#1E1E2C] border border-white/10 px-2 py-1 rounded">
              {f}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

function WorkflowStep({ number, title, text }: any) {
  return (
    <div className="flex items-start gap-4 group">
      <div className="w-12 h-12 rounded-xl bg-[#252536]/50 border border-[#334155] flex items-center justify-center text-[#F29F67] font-bold text-lg shrink-0 group-hover:border-[#F29F67]/50 group-hover:text-[#F29F67] transition-colors shadow-lg">
        {number}
      </div>
      <div>
        <h4 className="text-white font-semibold mb-1 group-hover:text-[#F29F67] transition-colors">{title}</h4>
        <p className="text-slate-400 text-sm leading-relaxed">{text}</p>
      </div>
    </div>
  )
}

