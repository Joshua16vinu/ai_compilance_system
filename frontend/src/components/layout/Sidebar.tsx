'use client'

import {
    ShieldCheck,
    LayoutDashboard,
    Files,
    Search,
    Settings,
    Bell,
    ChevronRight,
    LogOut,
    User
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import { useState } from 'react'

export function Sidebar({ setActiveTab, activeTab }: any) {
    const [collapsed, setCollapsed] = useState(false)

    const items = [
        { id: 'dashboard', icon: LayoutDashboard, label: 'Overview' },
        { id: 'scan', icon: Search, label: 'Audit Log' },
    ]

    return (
        <motion.div
            initial={{ width: 240 }}
            animate={{ width: collapsed ? 72 : 240 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="h-screen bg-[#0B0B15]/80 backdrop-blur-xl border-r border-white/5 flex flex-col z-50 sticky top-0 shadow-2xl shadow-black/50"
        >
            {/* Brand */}
            <div className="h-16 flex items-center px-6 border-b border-white/5 relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-r from-[#F29F67]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="w-8 h-8 rounded-lg bg-[#F29F67] flex items-center justify-center shrink-0 shadow-lg shadow-[#F29F67]/20">
                    <ShieldCheck className="w-5 h-5 text-white" />
                </div>
                <motion.div
                    initial={{ opacity: 1, width: 'auto' }}
                    animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto' }}
                    className="ml-3 font-bold text-white tracking-tight overflow-hidden whitespace-nowrap"
                >
                    Policy<span className="text-[#F29F67]">Guard</span>
                </motion.div>
            </div>

            {/* Navigation */}
            <div className="flex-1 py-6 px-3 space-y-1">
                <div className={cn("text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4 px-3", collapsed && "text-center")}>
                    {collapsed ? "Main" : "Workspace"}
                </div>

                {items.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        suppressHydrationWarning
                        className={cn(
                            "w-full flex items-center px-3 py-2.5 rounded-lg transition-all group relative duration-300",
                            activeTab === item.id
                                ? "bg-gradient-to-r from-[#F29F67]/10 to-transparent text-[#F29F67] font-medium shadow-[inset_2px_0_0_0_#F29F67]"
                                : "text-slate-400 hover:bg-white/5 hover:text-white"
                        )}
                    >
                        {activeTab === item.id && (
                            <motion.div
                                layoutId="activeTabIndicator"
                                className="absolute left-0 top-2 bottom-2 w-0.5 bg-[#F29F67] rounded-r-full shadow-[0_0_10px_rgba(242,159,103,0.5)]"
                            />
                        )}

                        <item.icon className={cn("w-5 h-5 shrink-0 transition-colors", activeTab === item.id ? "text-[#F29F67]" : "text-slate-500 group-hover:text-slate-300")} />

                        <motion.span
                            animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto' }}
                            className="ml-3 text-sm font-medium whitespace-nowrap overflow-hidden"
                        >
                            {item.label}
                        </motion.span>

                        {!collapsed && activeTab === item.id && (
                            <ChevronRight className="w-4 h-4 ml-auto text-blue-500/50" />
                        )}
                    </button>
                ))}
            </div>

            {/* User Footer */}
            <div className="p-4 border-t border-[#252536]">
                <div className={cn("flex items-center p-2 rounded-lg hover:bg-[#252536] cursor-pointer transition-colors group", collapsed && "justify-center")}>
                    <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                        <User className="w-4 h-4" />
                    </div>

                    <motion.div
                        animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto' }}
                        className="ml-3 overflow-hidden whitespace-nowrap"
                    >
                        <p className="text-sm font-medium text-white group-hover:text-[#F29F67] transition-colors">Admin User</p>
                        <p className="text-xs text-slate-500">Security Team</p>
                    </motion.div>

                    {!collapsed && <LogOut className="w-4 h-4 text-slate-600 ml-auto group-hover:text-[#ef4444] transition-colors" />}
                </div>

                <button
                    onClick={() => setCollapsed(!collapsed)}
                    suppressHydrationWarning
                    className="w-full mt-4 flex items-center justify-center p-2 text-slate-500 hover:text-white transition-colors text-xs uppercase tracking-wider font-semibold border-t border-[#252536] pt-4"
                >
                    {collapsed ? "Exp" : "Collapse View"}
                </button>
            </div>
        </motion.div >
    )
}
