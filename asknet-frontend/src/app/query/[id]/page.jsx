"use client"

import React from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { Button } from "../../../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card"
import { useTaskStatus } from "../../../lib/hooks"
import { motion } from "framer-motion"

export default function QueryPage() {
  const params = useParams()
  const taskId = params.id

  const { data: taskData, isLoading } = useTaskStatus(taskId)

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F5F5F5] flex items-center justify-center">
        <span className="text-2xl">Loading task...</span>
      </div>
    )
  }

  if (!taskData) {
    return (
      <div className="min-h-screen bg-[#F5F5F5] flex items-center justify-center">
        <span className="text-2xl">Task not found</span>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      <header className="border-b-4 border-black bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="text-lg hover:underline">
            ← Back to Dashboard
          </Link>
          <span className="text-lg text-gray-600">Task: {taskId}</span>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h1 className="text-4xl font-bold">Task Analysis</h1>
          <div className="flex gap-4">
            <span className="bg-black text-white px-4 py-2 text-lg">
              Status: {taskData.status}
            </span>
          </div>
        </motion.div>

        {/* Query Summary */}
        <Card>
          <CardHeader className="border-b-4 border-black py-4">
            <CardTitle className="text-xl">Query</CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <p className="text-lg">{taskData.query_text}</p>
          </CardContent>
        </Card>

        {/* Agent Contributions */}
        {taskData.synthesis?.refined_claims && (
          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">Agent Contributions</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              {taskData.synthesis.refined_claims.map((claim, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border-4 border-black p-4 bg-gray-50"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-semibold">{claim.agent}</span>
                    <span className="text-sm text-gray-600">
                      {(claim.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <p className="text-gray-700">{claim.content}</p>
                </motion.div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Final Answer */}
        {taskData.final_answer && (
          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">Final Answer</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="text-lg whitespace-pre-wrap">
                {taskData.final_answer}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Debate History */}
        {taskData.debate_history && taskData.debate_history.length > 0 && (
          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">Debate Rounds</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              {taskData.debate_history.map((round, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border-4 border-black p-4"
                >
                  <div className="flex justify-between items-center mb-3">
                    <span className="font-semibold">Round {round.round}</span>
                    <span className="text-sm text-gray-500">{round.timestamp}</span>
                  </div>
                  {round.responses && (
                    <div className="space-y-2">
                      {round.responses.map((response, rIndex) => (
                        <div key={rIndex} className="bg-gray-100 p-3">
                          <span className="font-medium">{response.agent}: </span>
                          <span>{response.response}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Synthesis Info */}
        {taskData.synthesis && (
          <Card>
            <CardHeader className="border-b-4 border-black py-4">
              <CardTitle className="text-xl">Synthesis Summary</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-2">
                <p className="text-lg">{taskData.synthesis.summary_of_reasoning}</p>
                <div className="mt-4">
                  <p className="font-semibold mb-2">Citations:</p>
                  {taskData.synthesis.citations?.map((citation, index) => (
                    <div key={index} className="text-sm text-gray-600 py-1">
                      • {citation.source}: {citation.content_preview}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
