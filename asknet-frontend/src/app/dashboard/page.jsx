"use client"

import React, { useState } from "react"
import Link from "next/link"
import { Button } from "../../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card"
import { Progress } from "../../components/ui/progress"
import { useAgents, useSubmitQuery, useTaskStatus, useLearningAnalytics } from "../../lib/hooks"
import { motion, AnimatePresence } from "framer-motion"

export default function Dashboard() {
  const [query, setQuery] = useState("")
  const [taskId, setTaskId] = useState(null)

  const { data: agentsData } = useAgents()
  const { data: analyticsData } = useLearningAnalytics()
  const submitMutation = useSubmitQuery()
  const { data: taskData, isLoading: taskLoading } = useTaskStatus(taskId)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    try {
      const result = await submitMutation.mutateAsync(query)
      setTaskId(result.task_id)
      setQuery("")
    } catch (error) {
      console.error("Failed to submit query:", error)
    }
  }

  const agents = agentsData?.agents || []
  const topAgents = analyticsData?.top_agents || []

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      {/* Header */}
      <header className="border-b-4 border-black bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">ASK-NET Console</h1>
          <div className="flex gap-4">
            <Link href="/" className="text-lg hover:underline">Home</Link>
            <Link href="/agents" className="text-lg hover:underline">Agents</Link>
            <Link href="/memory" className="text-lg hover:underline">Memory</Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-12 gap-6">
        {/* Left Sidebar - Agent Status */}
        <aside className="col-span-3 space-y-4">
          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">Agent Status</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              {agents.map((agent, index) => (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="space-y-2"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-lg">{agent.name}</span>
                    <span className="text-sm text-gray-600">
                      {(agent.trust_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <Progress value={agent.trust_score * 100} max={100} />
                </motion.div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">Top Agents</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              {topAgents.map((agent, index) => (
                <div key={agent.agent} className="flex justify-between items-center py-2">
                  <span className="text-lg">{agent.agent}</span>
                  <span className="text-sm font-semibold">
                    {(agent.score * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
        </aside>

        {/* Main Content - Query Interface */}
        <main className="col-span-6 space-y-6">
          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-2xl">Submit Query</CardTitle>
              <CardDescription className="text-lg">
                Enter your research question and let the agents collaborate
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Assess wildfire risk under drought conditions and propose mitigation strategies..."
                  className="w-full h-32 p-4 border-4 border-black text-lg resize-none focus:outline-none focus:ring-4 focus:ring-black"
                />
                <Button
                  type="submit"
                  size="lg"
                  disabled={submitMutation.isPending || !query.trim()}
                  className="w-full"
                >
                  {submitMutation.isPending ? "Submitting..." : "Submit Query"}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Task Results */}
          <AnimatePresence>
            {taskId && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Card>
                  <CardHeader className="border-b-4 border-black py-4">
                    <div className="flex justify-between items-center">
                      <CardTitle className="text-xl">Task Status</CardTitle>
                      <span className="text-sm bg-black text-white px-3 py-1">
                        {taskData?.status || "Processing..."}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-4">
                    {taskLoading ? (
                      <div className="flex items-center justify-center h-32">
                        <span className="text-xl">Processing query...</span>
                      </div>
                    ) : taskData?.final_answer ? (
                      <div className="space-y-4">
                        <p className="text-lg whitespace-pre-wrap">
                          {taskData.final_answer}
                        </p>
                        <Link href={`/query/${taskId}`}>
                          <Button variant="outline" className="mt-4">
                            View Full Analysis
                          </Button>
                        </Link>
                      </div>
                    ) : (
                      <p className="text-gray-500">Waiting for results...</p>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* Right Sidebar - System Stats */}
        <aside className="col-span-3 space-y-4">
          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">System Analytics</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              {analyticsData && (
                <>
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600">Average Rating</p>
                    <p className="text-2xl font-bold">
                      {(analyticsData.analytics?.average_rating || 0).toFixed(2)}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600">Total Queries</p>
                    <p className="text-2xl font-bold">
                      {analyticsData.analytics?.total_feedback_entries || 0}
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <Link href="/agents">
                <Button variant="outline" className="w-full justify-start">
                  Explore Agents
                </Button>
              </Link>
              <Link href="/memory">
                <Button variant="outline" className="w-full justify-start">
                  View Memory
                </Button>
              </Link>
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  )
}
