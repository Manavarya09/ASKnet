"use client"

import React from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card"
import { Progress } from "../../components/ui/progress"
import { useAgents, useLearningAnalytics } from "../../lib/hooks"
import { motion } from "framer-motion"

export default function AgentsPage() {
  const { data: agentsData } = useAgents()
  const { data: analyticsData } = useLearningAnalytics()

  const agents = agentsData?.agents || []
  const topAgents = analyticsData?.top_agents || []

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      <header className="border-b-4 border-black bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="text-lg hover:underline">
            ← Dashboard
          </Link>
          <h1 className="text-2xl font-bold">Agent Explorer</h1>
          <Link href="/memory" className="text-lg hover:underline">
            Memory
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <h1 className="text-5xl font-bold mb-8 border-b-4 border-black pb-4">
          System Agents
        </h1>

        <div className="grid grid-cols-3 gap-6">
          {agents.map((agent, index) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="h-full">
                <CardHeader className="border-b-4 border-black py-4">
                  <CardTitle className="text-xl">{agent.name}</CardTitle>
                  <CardDescription className="text-sm">
                    {agent.type}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Trust Score</span>
                        <span className="text-sm font-semibold">
                          {(agent.trust_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <Progress value={agent.trust_score * 100} max={100} />
                    </div>
                    <div className="pt-2 text-sm text-gray-600">
                      Type: {agent.type}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Top Agents Section */}
        {topAgents.length > 0 && (
          <div className="mt-12">
            <h2 className="text-3xl font-bold mb-6 border-b-4 border-black pb-4">
              Top Performing Agents
            </h2>
            <div className="grid grid-cols-3 gap-6">
              {topAgents.map((agent, index) => (
                <motion.div
                  key={agent.agent}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="bg-black text-white">
                    <CardContent className="pt-6">
                      <div className="flex justify-between items-center">
                        <span className="text-xl font-bold">{agent.agent}</span>
                        <span className="text-lg">
                          {(agent.score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
