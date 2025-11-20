import { Router } from "express";
import { fetchDisasterMessages } from "../controllers/disaster.controller";

const disasterRouter = Router();

disasterRouter.get("/messages", fetchDisasterMessages);

export { disasterRouter };
