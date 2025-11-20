# TypeScript Disaster Alert helpers

This folder contains a minimal service/controller/router trio that calls the SafetyData disaster alert API (`DSSP-IF-00247`) and returns the JSON payload. Environment variables are loaded via `dotenv`.

- Copy `.env.sample` to `.env` and set `SAFETYDATA_SERVICE_KEY` (Decoding key) at the repo root.
- Mount `disasterRouter` in an Express app, e.g. `app.use("/disaster", disasterRouter);`.
- Optional query params forwarded to the API: `serviceKey`, `returnType`, `pageNo`, `numOfRows`.

The HTTP client disables TLS verification by default to mirror the Python sample behavior. If you want strict verification, pass your own `https.Agent` to `new DisasterService(/* apiKey */, agent)` in `ts/services/disaster.service.ts`.
