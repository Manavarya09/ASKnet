"use client"

import React from "react"
import { cn } from "../../lib/utils"
import { motion } from "framer-motion"

const Progress = ({ className, value = 0, max = 100, ...props }) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  return (
    <div
      className={cn(
        "relative h-6 w-full overflow-hidden border-4 border-black bg-gray-100",
        className
      )}
      {...props}
    >
      <motion.div
        className="h-full bg-black"
        initial={{ width: 0 }}
        animate={{ width: `${percentage}%` }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-bold text-black z-10">{Math.round(percentage)}%</span>
      </div>
    </div>
  )
}

export { Progress }