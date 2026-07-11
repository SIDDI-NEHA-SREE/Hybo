import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { router } from './routes';

const app = express();
const port = process.env.PORT || 4000;

app.use(helmet());
app.use(cors());
app.use(express.json());

app.use('/api', router);

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'HYBO Smart City API', version: '1.0.0' });
});

app.listen(port, () => {
  console.log(`🚀 HYBO API server running on http://localhost:${port}`);
});
