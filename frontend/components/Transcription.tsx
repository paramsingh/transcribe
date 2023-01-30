import { Heading } from "@chakra-ui/react";

export const Transcription = ({
  heading,
  text,
}: {
  heading: string;
  text: string;
}) => {
  return (
    <div style={{ whiteSpace: "pre-line", marginBottom: "10px" }}>
      <Heading as={"h1"} size="xl" style={{ marginBottom: "10px" }}>
        {heading}
      </Heading>
      <p>{text}</p>
    </div>
  );
};
