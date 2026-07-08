import { validationResult } from 'express-validator';
import { AppError } from '../errors/AppError.js';

export const validate = (validations) => {
  return async (req, res, next) => {
    await Promise.all(validations.map(validation => validation.run(req)));

    const errors = validationResult(req);
    if (errors.isEmpty()) {
      return next();
    }

    const errorMessages = errors.array().map(err => ({
      field: err.path,
      message: err.msg,
    }));

    next(new AppError('Error de validación', 400, 'VALIDATION_ERROR', errorMessages));
  };
};