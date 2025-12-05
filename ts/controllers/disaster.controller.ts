import { Request, Response } from "express";
import axios from "axios";
import {
  disasterService,
  DisasterRequestParams,
} from "../services/disaster.service";

const pickString = (value: unknown): string | undefined =>
  typeof value === "string" ? value : undefined;

export async function fetchDisasterMessages(
  req: Request,
  res: Response
): Promise<void> {
  const query = req.query as Record<string, unknown>;

  const params: DisasterRequestParams = {
    serviceKey: pickString(query.serviceKey),
    returnType: pickString(query.returnType),
    pageNo: pickString(query.pageNo),
    numOfRows: pickString(query.numOfRows),
  };

  try {
    const { status, data } = await disasterService.getDisasterMessages(params);
    res.status(status).json({ source: "safetydata", data });
  } catch (error) {
    if (axios.isAxiosError(error)) {
      res
        .status(error.response?.status ?? 500)
        .json({ message: "Failed to fetch disaster messages", detail: error });
      return;
    }

    res.status(500).json({
      message: error instanceof Error ? error.message : "Unknown error",
    });
  }
}
