import express from 'express';
import { studentController } from './student.controller.js';
import { authMiddleware } from '../../core/middlewares/auth.js';

const router = express.Router();

router.use(authMiddleware.authenticate);

router.get('/', studentController.getAll);
router.get('/:id', studentController.getById);
router.post('/', studentController.create);
router.put('/:id', studentController.update);
router.delete('/:id', studentController.delete);

export default router;