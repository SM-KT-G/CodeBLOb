import axios from "axios";
import { ApiError, NotFoundError } from "../errors/custom.error";

export interface DisasterRequestParams {
  serviceKey: string;
  returnType?: "xml" | "json";
  pageNo?: string;
  numOfRows?: string;
}
// 인터페이스 다른곳 
// T = unknown 이거 왜씀??
export interface DisasterServiceResponse<T = unknown> {
  status: number;
  data: T;
}

const DISASTER_BASE_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-00247";

export class DisasterService {
  static async getDisasterMessages(
    params: DisasterRequestParams
  ): Promise<DisasterServiceResponse> {
    const {
      serviceKey,
      returnType = "json",
      pageNo = "1",
      numOfRows = "5",
    } = params;

    const response = await axios.get(DISASTER_BASE_URL, {
      params: { serviceKey, returnType, pageNo, numOfRows },
    });

    return { status: response.status, data: response.data };
  }
}
