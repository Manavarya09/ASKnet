import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import * as api from "./api"

export function useAgents() {
  return useQuery({
    queryKey: ["agents"],
    queryFn: api.listAgents,
  })
}

export function useTaskStatus(taskId, enabled = true) {
  return useQuery({
    queryKey: ["task", taskId],
    queryFn: () => api.getTaskStatus(taskId),
    refetchInterval: enabled ? 2000 : false,
    enabled: !!taskId && enabled,
  })
}

export function useAgentMemory(agentName) {
  return useQuery({
    queryKey: ["memory", agentName],
    queryFn: () => api.getAgentMemory(agentName),
    enabled: !!agentName,
  })
}

export function useLearningAnalytics() {
  return useQuery({
    queryKey: ["analytics"],
    queryFn: api.getLearningAnalytics,
  })
}

export function useSubmitQuery() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.submitQuery,
    onSuccess: (data) => {
      queryClient.invalidateQueries(["tasks"])
    },
  })
}

export function useSubmitFeedback() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ taskId, rating, comments }) => 
      api.submitFeedback(taskId, rating, comments),
    onSuccess: () => {
      queryClient.invalidateQueries(["tasks"])
    },
  })
}
