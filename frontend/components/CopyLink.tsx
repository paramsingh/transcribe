import { CopyIcon } from "@chakra-ui/icons";
import { Button } from "@chakra-ui/react";
import { useState } from "react";

export const CopyLink = ({ link }: { link: string }) => {
  const [copied, setCopied] = useState<boolean>(false);
  return (
    <Button
      leftIcon={<CopyIcon />}
      onClick={() => {
        navigator.clipboard.writeText(link);
        setCopied(true);
      }}
      onMouseEnter={() => setCopied(false)}
      marginBottom={5}
    >
      {!copied ? "Copy transcription link for later." : "Copied!"}
    </Button>
  );
};
