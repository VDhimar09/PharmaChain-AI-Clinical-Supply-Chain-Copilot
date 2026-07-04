export type ApiQueryParams = Record<string, string | number | boolean | undefined>;

export type ApiResponse<T> = T;

export type ApiErrorBody = {
  detail?: string | string[];
  message?: string;
  [key: string]: unknown;
};

export class ApiError extends Error {
  public status: number;
  public body: ApiErrorBody | null;

  constructor(status: number, message: string, body: ApiErrorBody | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}
