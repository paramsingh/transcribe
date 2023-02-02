export const getSessionToken = () => {
  return localStorage.getItem("sessionToken");
};

export const removeSessionToken = () => {
  localStorage.removeItem("sessionToken");
};

export const setSessionToken = (sessionToken: string) => {
  localStorage.setItem("sessionToken", sessionToken);
};
