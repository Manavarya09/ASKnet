"use client"

import React from "react"
import Link from "next/link"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card"
import { motion } from "framer-motion"

export default function Home() {
  const features = [
    { title: "Multi-Agent Debate", desc: "Watch multiple AI agents collaborate and debate in real-time" },
    { title: "Self-Learning System", desc: "Agents improve their trust scores based on performance" },
    { title: "Persistent Memory", desc: "System remembers all interactions and learns from them" },
    { title: "ML Prediction Engine", desc: "Advanced forecasting with scikit-learn models" },
  ]

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      {/* Navigation */}
      <nav className="border-b-4 border-black bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold tracking-tight">ASK-NET</h1>
          <div className="flex gap-4">
            <Link href="/dashboard" className="text-lg hover:underline">
              Console
            </Link>
            <Link href="/agents" className="text-lg hover:underline">
              Agents
            </Link>
            <Link href="/memory" className="text-lg hover:underline">
              Memory
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h1 className="text-8xl font-bold tracking-tight mb-4">
            ASK-Net
          </h1>
          <p className="text-3xl text-gray-600 mb-2">
            Autonomous Self-learning Knowledge Network
          </p>
          <p className="text-xl text-gray-500 mb-12 max-w-2xl mx-auto">
            A multi-agent AI research system where specialized agents collaborate,
            debate, and improve over time through reinforcement learning.
          </p>
          <Link href="/dashboard">
            <Button size="xl" className="text-2xl px-12">
              Open Console
            </Button>
          </Link>
        </motion.div>
      </section>

      {/* Feature Grid */}
      <section className="max-w-7xl mx-auto px-6 pb-20">
        <h2 className="text-4xl font-bold mb-12 border-b-4 border-black pb-4">
          Core Features
        </h2>
        <div className="grid grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card>
                <CardHeader className="border-b-4 border-black">
                  <CardTitle className="text-2xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent className="pt-4">
                  <p className="text-lg text-gray-600">{feature.desc}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t-4 border-black bg-white py-8">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-gray-600">ASK-Net Autonomous Self-learning Knowledge Network</p>
        </div>
      </footer>
    </div>
  )
}
