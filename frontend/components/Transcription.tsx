import { Heading } from "@chakra-ui/react";

export const Transcription = ({ text }: { text: string }) => {
  return (
    <div style={{ whiteSpace: "pre-line" }}>
      <Heading as={"h1"} size="3xl" style={{marginBottom: "10px"}}>
        Transcription
      </Heading>
      <p>{text}</p>
    </div>
  );
};
