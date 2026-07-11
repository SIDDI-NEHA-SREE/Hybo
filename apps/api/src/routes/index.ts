import { Router } from 'express';
// import { authRoutes } from './auth.routes';
// import { complaintRoutes } from './complaint.routes';

export const router = Router();

// router.use('/auth', authRoutes);
// router.use('/complaints', complaintRoutes);

router.get('/status', (req, res) => {
  res.json({ status: 'ok' });
});
