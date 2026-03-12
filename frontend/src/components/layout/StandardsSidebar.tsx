import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { nistDomainsData } from '@/data/nistPolicies'
import { ChevronDown, ExternalLink, BookOpen, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'

export function StandardsSidebar() {
  const [expandedDomain, setExpandedDomain] = useState<string | null>(nistDomainsData[0].name)

  return (
    <div className="w-[300px] lg:w-[320px] h-screen bg-[#0B0B15]/80 backdrop-blur-xl border-l border-white/5 flex flex-col z-40 sticky top-0 shadow-2xl shadow-black/50 overflow-hidden shrink-0 hidden md:flex">
      <div className="p-6 border-b border-white/5 bg-gradient-to-br from-slate-900/50 to-transparent">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-[#3B8FF3]/10 rounded-lg text-[#3B8FF3] border border-[#3B8FF3]/20">
            <BookOpen className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-white tracking-tight">NIST Policies</h2>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          Standard policy directory and templates for compliance domains.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent p-4 space-y-4">
        {nistDomainsData.map((domain) => (
          <div
            key={domain.name}
            className="rounded-xl border border-white/5 bg-[#1E1E2C]/30 overflow-hidden"
          >
            <button
              onClick={() => setExpandedDomain(expandedDomain === domain.name ? null : domain.name)}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-white/5 transition-colors"
            >
              <span className="font-semibold text-sm text-slate-200">{domain.name}</span>
              <ChevronDown
                className={cn(
                  "w-4 h-4 text-slate-500 transition-transform duration-300",
                  expandedDomain === domain.name ? "rotate-180" : ""
                )}
              />
            </button>
            <AnimatePresence>
              {expandedDomain === domain.name && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden"
                >
                  <div className="px-3 pb-3 pt-1 space-y-1">
                    {domain.policies.map((policy) => (
                      <a
                        key={policy.name}
                        href={policy.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group flex items-center gap-3 p-2 rounded-lg hover:bg-[#3B8FF3]/10 transition-colors"
                      >
                        <div className="p-1.5 rounded-md bg-[#252536] text-slate-400 group-hover:text-[#3B8FF3] group-hover:bg-[#3B8FF3]/20 transition-colors">
                          <FileText className="w-3.5 h-3.5" />
                        </div>
                        <span className="text-xs font-medium text-slate-400 group-hover:text-slate-200 truncate flex-1 leading-snug">
                          {policy.name}
                        </span>
                        <ExternalLink className="w-3 h-3 text-slate-600 group-hover:text-[#3B8FF3] opacity-0 group-hover:opacity-100 transition-all -ml-2" />
                      </a>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </div>
  )
}
