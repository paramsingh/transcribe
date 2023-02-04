import { getSessionToken } from "../utils/sessionTokenUtils";

// const BASE_URL = "http://localhost:6550/api/v1";
const BASE_URL = "https://transcribe.param.codes/api/v1";

export const submitLink = async (link: string) => {
  const headers: { "Content-Type": string; Authorization?: string } = {
    "Content-Type": "application/json",
  };
  const sessionToken = getSessionToken();
  if (sessionToken) {
    headers["Authorization"] = `Bearer ${sessionToken}`;
  }
  const response = await fetch(`${BASE_URL}/transcribe`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({ link }),
  });
  return response.json();
};

export const getDetailsForToken = async (token: string) => {
  const response = await fetch(`${BASE_URL}/transcription/${token}/details`);
  return response.json();
};

export const getTranscriptionsForUser = async (userToken: string) => {
  const sessionToken = getSessionToken();
  if (!sessionToken) {
    throw new Error("No session token");
  }
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${sessionToken}`,
  };
  const response = await fetch(`${BASE_URL}/user/${userToken}/transcriptions`, {
    method: "GET",
    headers,
  });
  return response.json();
};
