import 'server-only';

import { getAgents, type Agent } from './data';

const signals: Record<string, string[]> = {
  'A-02': ['proposal', 'pursuit', 'opportunity', 'lead', 'rfp', 'bid', 'client intake'],
  'A-03': ['permit', 'permitting', 'feasibility', 'jurisdiction', 'entitlement', 'utility'],
  'A-04': ['design', 'drawing', 'engineering', 'calculation', 'deliverable', 'qaqc', 'qa/qc'],
  'A-05': ['estimate', 'estimating', 'construction', 'schedule', 'submittal', 'rfi', 'procurement', 'field', 'closeout'],
  'A-06': ['budget', 'invoice', 'billing', 'cash', 'cost', 'finance', 'collection', 'variance'],
  'A-07': ['client update', 'email', 'communication', 'meeting summary', 'status update']
};

export type WorkflowRecommendation = {
  agent: Agent;
  reason: string;
  confidence: 'high' | 'medium' | 'low';
};

export async function recommendWorkflow(outcome: string): Promise<WorkflowRecommendation> {
  const agents = await getAgents();
  const normalized = outcome.toLowerCase();
  const estimatingRequest = /\b(estimate|estimating|takeoff|quantity takeoff)\b/.test(normalized);
  const scores = Object.entries(signals).map(([agentId, keywords]) => ({
    agentId,
    matches: keywords.filter((keyword) => normalized.includes(keyword))
  }));
  scores.sort((a, b) => b.matches.length - a.matches.length);

  const best = estimatingRequest
    ? { agentId: 'A-05', matches: ['estimating'] }
    : scores[0];
  const fallbackId = 'A-01';
  const agent = agents.find((candidate) => candidate.id === (best?.matches.length ? best.agentId : fallbackId));
  if (!agent) throw new Error('Agent registry is incomplete.');

  if (!best?.matches.length) {
    return {
      agent,
      confidence: 'low',
      reason: 'The request does not contain enough domain detail, so the Orchestrator should clarify and route it.'
    };
  }

  return {
    agent,
    confidence: best.matches.length >= 2 ? 'high' : 'medium',
    reason: `Matched the request to ${best.matches.slice(0, 3).join(', ')}.`
  };
}
