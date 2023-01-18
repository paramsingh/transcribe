export const validateUrl = (url: string): boolean => {
  return url.includes("youtube.com") || url.includes("youtu.be");
};
