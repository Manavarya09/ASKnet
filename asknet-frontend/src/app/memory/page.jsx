"use client"

import React from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card"
import { useAgents, useLearningAnalytics } from "../../lib/hooks"
import { motion } from "framer-motion"

export default function MemoryPage() {
  const { data: agentsData } = useAgents()
  const { data: analyticsData } = useLearningAnalytics()

  const agents = agentsData?.agents || []
  const analytics = analyticsData?.analytics || {}

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      <header className="border-b-4 border-black bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="text-lg hover:underline">
            ← Dashboard
          </Link>
          <h1 className="text-2xl font-bold">System Memory</h1>
          <Link href="/agents" className="text-lg hover:underline">
            Agents
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <h1 className="text-5xl font-bold mb-8 border-b-4 border-black pb-4">
          Memory Viewer
        </h1>

        <div className="grid grid-cols-2 gap-6 mb-12">
          {/* System Stats */}
          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">System Statistics</CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm text-gray-600">Total Queries</p>
                  <p className="text-2xl font-bold">
                    {analytics.total_feedback_entries || 0}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-gray-600">Average Rating</p>
                  <p className="text-2xl font-bold">
                    {(analytics.average_rating || 0).toFixed(2)}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-gray-600">Active Agents</p>
                  <p className="text-2xl font-bold">{agents.length}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-gray-600">Feedback Entries</p>
                  <p className="text-2xl font-bold">
                    {analytics.total_feedback_entries || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Agent Activity */}
          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">Agent Activity</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-3">
                {agents.map((agent, index) => (
                  <motion.div
                    key={agent.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex justify-between items-center p-3 bg-gray-100 border-2 border-black"
                  >
                    <span className="font-semibold">{agent.name}</span>
                    <span className="text-sm text-gray-600">
                      {(agent.trust_score * 100).toFixed(0)}% trust
                    </span>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Memory Grid */}
        <Card>
          <CardHeader className="border-b-4 border-black py-4">
            <CardTitle className="text-xl">Stored Memories</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="border-4 border-black">
              <div className="grid grid-cols-4 bg-black text-white font-bold">
                <div className="p-3 border-r-4 border-black">Type</div>
                <div className="p-3 border-r-4 border-black">Agent</div>
                <div className="p-3 border-r-4 border-black">Content</div>
                <div className="p-3">Status</div>
              </div>
              <div className="divide-y-4 divide-black">
                {[
                  { type: "Query", agent: "Task Planner", content: "Climate risk analysis", status: "Completed" },
                  { type: "Debate", agent: "Research Agent", content: "Evidence collected", status: "Active" },
                  { type: "Prediction", agent: "Prediction Agent", content: "Wildfire risk model", status: "Trained" },
                  { type: "Feedback", agent: "System", content: "User rating: 5/5", status: "Recorded" },
                ].map((row, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="grid grid-cols-4"
                  >
                    <div className="p-3 border-r-4 border-black">{row.type}</div>
                    <div className="p-3 border-r-4 border-black">{row.agent}</div>
                    <div className="p-3 border-r-4 border-black truncate">{row.content}</div>
                    <div className="p-3">{row.status}</div>
                  </motion.div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
