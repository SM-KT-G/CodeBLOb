import "dotenv/config";
import axios, { AxiosInstance } from "axios";
import https from "https";

export interface DisasterRequestParams {
  serviceKey?: string;
  returnType?: string;
  pageNo?: string;
  numOfRows?: string;
}

export interface DisasterServiceResponse<T = unknown> {
  status: number;
  data: T;
}

const DISASTER_BASE_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-00247";

const defaultHttpsAgent = new https.Agent({
  rejectUnauthorized: false, // mirror Python urllib3.disable_warnings
});

export class DisasterService {
  private readonly client: AxiosInstance;

  constructor(
    private readonly apiKey: string = process.env.SAFETYDATA_SERVICE_KEY ?? "",
    httpsAgent: https.Agent | undefined = defaultHttpsAgent
  ) {
    this.client = axios.create({
      baseURL: DISASTER_BASE_URL,
      httpsAgent,
    });
  }

  async getDisasterMessages(
    overrides: DisasterRequestParams = {}
  ): Promise<DisasterServiceResponse> {
    const {
      serviceKey = this.apiKey,
      returnType = "json",
      pageNo = "1",
      numOfRows = "5",
    } = overrides;

    if (!serviceKey) {
      throw new Error(
        "Missing serviceKey. Provide it in overrides or set SAFETYDATA_SERVICE_KEY."
      );
    }

    const response = await this.client.get("", {
      params: { serviceKey, returnType, pageNo, numOfRows },
    });

    return { status: response.status, data: response.data };
  }
}

export const disasterService = new DisasterService();
