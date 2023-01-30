import { Box } from "@chakra-ui/react";

const getVideoId = (link: string) => {
  if (link.includes("youtu.be")) {
    return link.split("/")[3];
  }
  return link.split("=")[1];
};

export const YoutubeEmbed = ({ link }: { link: string }) => {
  const videoId = getVideoId(link);
  return (
    <Box
      as="iframe"
      src={`https://youtube.com/embed/${videoId}`}
      style={{ width: "80%", marginBottom: "20px" }}
      sx={{ aspectRatio: "16 / 9" }}
    />
  );
};
