export type Priority = 'High' | 'Med' | 'Low';
export type TestStatus = 'Passing' | 'Failing' | 'Pending';
export type AgentRole = 'Frontend' | 'Backend' | 'Tester';
export type KanbanStatus = 'Backlog' | 'InProgress' | 'Review' | 'Done';

export interface Test {
  id: string;
  description: string;
  status: TestStatus;
}

export interface Requirement {
  id: string;
  title: string;
  description: string;
  priority: Priority;
  status: KanbanStatus;
  tests: Test[];
  assignedAgents: AgentRole[];
}

export const mockRequirements: Requirement[] = [
  {
    id: 'REQ-001',
    title: 'User Authentication',
    description: 'Allow users to register, login, and securely store JWT tokens in HttpOnly cookies.',
    priority: 'High',
    status: 'Done',
    assignedAgents: ['Backend', 'Tester'],
    tests: [
      { id: 'T-101', description: 'POST /api/login returns 200 on valid creds', status: 'Passing' },
      { id: 'T-102', description: 'POST /api/login returns 401 on invalid creds', status: 'Passing' },
      { id: 'T-103', description: 'Cookie contains secure HttpOnly flag', status: 'Passing' },
    ]
  },
  {
    id: 'REQ-002',
    title: 'Payment Processing Integration',
    description: 'Integrate Stripe checkout for subscription purchases. Webhooks must update DB.',
    priority: 'High',
    status: 'InProgress',
    assignedAgents: ['Backend', 'Frontend', 'Tester'],
    tests: [
      { id: 'T-201', description: 'Checkout session ID generated', status: 'Passing' },
      { id: 'T-202', description: 'Webhook signature validation', status: 'Failing' },
      { id: 'T-203', description: 'DB user status updated to Premium', status: 'Pending' },
    ]
  },
  {
    id: 'REQ-003',
    title: 'Dark Mode Toggle',
    description: 'UI toggle to switch between dark and light themes. Persist in local storage.',
    priority: 'Low',
    status: 'Backlog',
    assignedAgents: ['Frontend'],
    tests: [
      { id: 'T-301', description: 'Theme state persists in localStorage', status: 'Pending' },
      { id: 'T-302', description: 'CSS variables update dynamically', status: 'Pending' },
    ]
  },
  {
    id: 'REQ-004',
    title: 'Database Schema Migration',
    description: 'Update user table to support multi-tenant workspaces.',
    priority: 'Med',
    status: 'Review',
    assignedAgents: ['Backend'],
    tests: [
      { id: 'T-401', description: 'Migrations run successfully', status: 'Passing' },
      { id: 'T-402', description: 'Old data is preserved', status: 'Passing' },
    ]
  }
];

export interface ChatMessage {
  id: string;
  agent: AgentRole | 'PM';
  text: string;
  timestamp: string;
}

export const mockChat: ChatMessage[] = [
  { id: 'M1', agent: 'Backend', text: 'I am starting on REQ-002 (Stripe Webhooks). Frontend, do you need the payload spec?', timestamp: '10:00 AM' }
];
