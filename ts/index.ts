import axios from "axios";
import { disasterService } from "./services/disaster.service";

async function main(): Promise<void> {
  try {
    const { status, data } = await disasterService.getDisasterMessages();
    console.log("Status Code:", status);
    console.log("Data:", JSON.stringify(data, null, 2));
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("Axios Error:", error.message);
      return;
    }

    if (error instanceof Error) {
      console.error("Unexpected Error:", error.message);
      return;
    }

    console.error("Unknown failure while fetching disaster messages");
  }
}

void main();
