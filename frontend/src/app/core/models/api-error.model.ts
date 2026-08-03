export interface ApiSimpleError {
  detail: string;
}

export interface ApiValidationErrorItem {
  type: string;
  loc: (string | number)[];
  msg: string;
  input?: unknown;
}

export interface ApiValidationError {
  detail: ApiValidationErrorItem[];
}

export type ApiErrorBody = ApiSimpleError | ApiValidationError;

export function isValidationError(body: unknown): body is ApiValidationError {
  return (
    !!body &&
    typeof body === 'object' &&
    Array.isArray((body as ApiValidationError).detail)
  );
}
