import { removeSessionToken } from "../utils/sessionTokenUtils";

const BASE_URL = "http://localhost:6550/api/login";

export const sendEmail = async (email: string) => {
  const response = await fetch(`${BASE_URL}/send-email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email }),
  });
  return response.json();
};

export const redeemToken = async (token: string) => {
  const response = await fetch(`${BASE_URL}/redeem-magic-link`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ secret: token }),
  });
  return response.json();
};

export const getUserFromSessionToken = async (sessionToken: string) => {
  const response = await fetch(`${BASE_URL}/get-user`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${sessionToken}`,
    },
  });
  if (response.status == 200) {
    return response.json();
  }
  removeSessionToken();
  throw new Error("Session token invalid");
};

export const logOut = async (sessionToken: string) => {
  const response = await fetch(`${BASE_URL}/logout`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${sessionToken}`,
    },
  });
  if (response.status == 200) {
    return response.json();
  }
  throw new Error("Logout failed");
};
