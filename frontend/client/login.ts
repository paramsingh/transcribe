const BASE_URL = "http://localhost:6550/login";

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
