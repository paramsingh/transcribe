import { getUserFromSessionToken } from "../client/login";

export const getUser = async (sessionToken: string) => {
  return await getUserFromSessionToken(sessionToken);
};
