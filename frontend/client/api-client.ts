const BASE_URL = "https://transcribe.param.codes/api/v1";

export const submitLink = async (link: string) => {
  const response = await fetch(`${BASE_URL}/transcribe`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ link }),
  });
  return response.json();
};

export const getDetailsForUUID = async (uuid: string) => {
  const response = await fetch(`${BASE_URL}/transcription/${uuid}/details`);
  return response.json();
};
