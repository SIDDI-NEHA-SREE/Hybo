export type Role = 'admin' | 'department' | 'user';

export type User = {
  id: number;
  email: string;
  name: string | null;
  role: Role;
  departmentId: number | null;
};

export type ComplaintStatus = 'open' | 'in_progress' | 'resolved';

export type Complaint = {
  id: number;
  userId: number;
  title: string;
  description: string;
  category: string;
  status: ComplaintStatus;
};
