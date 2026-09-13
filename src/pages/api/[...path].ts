import type { APIRoute } from "astro";
import { handleApi } from "../../backend/app";

export const prerender = false;

const ALL: APIRoute = ({ request, locals }) =>
	handleApi(request, locals.cfContext);

export const GET = ALL;
export const POST = ALL;
export const PUT = ALL;
export const PATCH = ALL;
export const DELETE = ALL;
export const OPTIONS = ALL;
